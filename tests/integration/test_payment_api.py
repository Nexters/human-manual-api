from datetime import UTC, datetime
from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from pakit.api.auth_dependencies import require_current_user
from pakit.api.dependencies import (
    get_payment_gateway,
    get_payment_repository,
    get_romantic_report_generator,
    get_romantic_report_repository,
)
from pakit.core.config import Settings, get_settings
from pakit.main import create_app
from pakit.services.payment_service import (
    PaymentApprovalResult,
    PaymentOrder,
    PaymentReadyRequest,
    PaymentReadyResult,
    PaymentStatus,
    ResultAccess,
    RomanticReportPurchase,
)
from pakit.services.romantic_report_generator import GeneratedRelationshipReport
from pakit.services.romantic_report_repository import (
    RelationshipProfileSource,
    RomanticReportToSave,
    StoredRomanticReport,
)
from pakit.services.user_repository import StoredUser

NOW = datetime(2026, 10, 7, tzinfo=UTC)
USER = StoredUser(id=42, created_at=NOW, last_logged_in_at=NOW)
PURCHASE = {
    "mine_result_code": "MINE0001",
    "partner_result_code": "FRIEND01",
    "mine_gender": "여자",
    "partner_gender": "남자",
}
ORDER_ID = "order_123456789012345"


class MemoryPaymentRepository:
    def __init__(self, *, owns_result: bool = True) -> None:
        self.owns_result = owns_result
        self.order: PaymentOrder | None = None

    async def get_result_access(
        self, user_id: int, mine_result_code: str, partner_result_code: str
    ) -> ResultAccess:
        return ResultAccess(True, self.owns_result and user_id == 42, True)

    async def create_order(self, user_id: int, purchase: RomanticReportPurchase) -> PaymentOrder:
        self.order = PaymentOrder(
            order_id=ORDER_ID,
            user_id=user_id,
            product_code="romantic-report-v1",
            product_name="Pakit 연인 관계 설명서",
            purchase=purchase,
            amount=990,
            status="CREATED",
            tid=None,
            aid=None,
            fulfillment_reference=None,
            created_at=NOW,
            approved_at=None,
        )
        return self.order

    async def set_ready(self, order_id: str, tid: str) -> PaymentOrder:
        assert self.order is not None
        self.order = PaymentOrder(**{**self.order.__dict__, "status": "READY", "tid": tid})
        return self.order

    async def set_failed(self, order_id: str, user_id: int) -> PaymentOrder | None:
        return await self._set_status(order_id, user_id, "FAILED")

    async def set_canceled(self, order_id: str, user_id: int) -> PaymentOrder | None:
        return await self._set_status(order_id, user_id, "CANCELED")

    async def get_for_user(self, order_id: str, user_id: int) -> PaymentOrder | None:
        if self.order is None or self.order.order_id != order_id or self.order.user_id != user_id:
            return None
        return self.order

    async def set_approved(
        self, order_id: str, user_id: int, approval: PaymentApprovalResult
    ) -> PaymentOrder | None:
        if await self.get_for_user(order_id, user_id) is None:
            return None
        assert self.order is not None
        self.order = PaymentOrder(
            **{
                **self.order.__dict__,
                "status": "APPROVED",
                "aid": approval.aid,
                "approved_at": approval.approved_at,
            }
        )
        return self.order

    async def attach_report(
        self, order_id: str, user_id: int, report_code: str
    ) -> PaymentOrder | None:
        if await self.get_for_user(order_id, user_id) is None:
            return None
        assert self.order is not None
        self.order = PaymentOrder(**{**self.order.__dict__, "fulfillment_reference": report_code})
        return self.order

    async def _set_status(self, order_id: str, user_id: int, status: str) -> PaymentOrder | None:
        if await self.get_for_user(order_id, user_id) is None:
            return None
        assert self.order is not None
        self.order = PaymentOrder(**{**self.order.__dict__, "status": cast(PaymentStatus, status)})
        return self.order


class FakePaymentGateway:
    def __init__(self) -> None:
        self.ready_request: PaymentReadyRequest | None = None
        self.approval_calls = 0

    async def ready(self, request: PaymentReadyRequest) -> PaymentReadyResult:
        self.ready_request = request
        return PaymentReadyResult(
            tid="T1234567890123456789",
            next_redirect_app_url="https://pay.test/app",
            next_redirect_mobile_url="https://pay.test/mobile",
            next_redirect_pc_url="https://pay.test/pc",
        )

    async def approve(
        self,
        *,
        tid: str,
        order_id: str,
        partner_user_id: str,
        pg_token: str,
        amount: int,
    ) -> PaymentApprovalResult:
        self.approval_calls += 1
        assert pg_token == "pg-token"
        return PaymentApprovalResult(
            aid="A1234567890123456789",
            tid=tid,
            partner_order_id=order_id,
            partner_user_id=partner_user_id,
            amount=amount,
            payment_method_type="MONEY",
            approved_at=NOW,
        )


def _client(
    repository: MemoryPaymentRepository, gateway: FakePaymentGateway
) -> tuple[TestClient, FastAPI]:
    application = create_app()
    application.dependency_overrides[require_current_user] = lambda: USER
    application.dependency_overrides[get_payment_repository] = lambda: repository
    application.dependency_overrides[get_payment_gateway] = lambda: gateway
    application.dependency_overrides[get_settings] = lambda: Settings(_env_file=None)
    return TestClient(application), application


def test_prepares_and_approves_fixed_price_payment_idempotently() -> None:
    repository = MemoryPaymentRepository()
    gateway = FakePaymentGateway()
    client, _ = _client(repository, gateway)

    ready = client.post("/api/payments/kakaopay/ready", json=PURCHASE)

    assert ready.status_code == 200
    assert ready.json()["amount"] == 990
    assert ready.json()["redirect_url"]["pc"] == "https://pay.test/pc"
    assert gateway.ready_request is not None
    assert gateway.ready_request.amount == 990
    assert gateway.ready_request.partner_user_id == "pakit-42"
    assert gateway.ready_request.approval_url.endswith(f"/api/payments/kakaopay/{ORDER_ID}/approve")

    first = client.get(
        f"/api/payments/kakaopay/{ORDER_ID}/approve",
        params={"pg_token": "pg-token"},
        follow_redirects=False,
    )
    second = client.get(
        f"/api/payments/kakaopay/{ORDER_ID}/approve",
        params={"pg_token": "pg-token"},
        follow_redirects=False,
    )

    assert first.status_code == 307
    assert first.headers["location"].endswith(
        f"/payments/kakaopay/complete?order_id={ORDER_ID}&status=approved"
    )
    assert second.status_code == 307
    assert gateway.approval_calls == 1


def test_rejects_payment_when_mine_result_is_not_owned() -> None:
    repository = MemoryPaymentRepository(owns_result=False)
    gateway = FakePaymentGateway()
    client, _ = _client(repository, gateway)

    response = client.post("/api/payments/kakaopay/ready", json=PURCHASE)

    assert response.status_code == 403
    assert response.json()["error"]["code"] == "PAYMENT_RESULT_NOT_OWNED"
    assert gateway.ready_request is None


def test_requires_kakaopay_configuration() -> None:
    repository = MemoryPaymentRepository()
    gateway = FakePaymentGateway()
    client, application = _client(repository, gateway)
    application.dependency_overrides[get_payment_gateway] = lambda: None

    response = client.post("/api/payments/kakaopay/ready", json=PURCHASE)

    assert response.status_code == 503
    assert response.json()["error"]["code"] == "KAKAOPAY_NOT_CONFIGURED"


class MemoryReportRepository:
    def __init__(self) -> None:
        self.stored: StoredRomanticReport | None = None

    async def get_profile_source(self, result_code: str) -> RelationshipProfileSource | None:
        if result_code not in {"MINE0001", "FRIEND01"}:
            return None
        return RelationshipProfileSource(
            result_code=result_code,
            nickname="본인" if result_code == "MINE0001" else "상대",
            mbti="ENTP" if result_code == "MINE0001" else "INFP",
            assessment_version="2026-08-20.1",
            axis_scores={"attachment": 50, "expression": 50, "routine": 50, "egen": 50},
            answers={
                "step1.q06": "interrupt",
                "step1.q07": "brunch_cafe",
                "step1.q12": "listen_to_me",
                "step2.q01": "inspect_profile",
                "step2.q02": "hint_and_wait",
                "step2.q03": "rehearse_with_ai",
                "step2.q04": 50,
                "step2.q05": "share_everything",
                "step2.q08": "express_with_words",
                "step2.q09": "ruminate",
                "step2.q10": "try_new_menu",
                "step2.q11": "try_new_store",
                "step2.q12": "skip",
            },
        )

    async def find_existing(self, **keys: str) -> StoredRomanticReport | None:
        return self.stored

    async def save(self, report: RomanticReportToSave) -> StoredRomanticReport:
        self.stored = StoredRomanticReport(report.report_code, report.content, NOW)
        return self.stored


class FakeReportGenerator:
    model = "test-model"

    async def generate(self, *, instructions: str, user_prompt: str) -> GeneratedRelationshipReport:
        headings = (
            "이 관계의 핵심 구조",
            "연락 속도의 차이",
            "마음을 확인하는 방식",
            "갈등이 이어지는 과정",
            "회복의 리듬",
            "표현이 번역되는 순간",
            "이 관계가 가진 힘",
            "서로에게 해주면 좋은 것",
            "둘만의 관계 규칙",
            "이 관계의 성장 방향",
        )
        content = "\n\n".join(
            f"## {index}. {heading}\n\n본문" for index, heading in enumerate(headings, start=1)
        )
        return GeneratedRelationshipReport(content=content)


def test_generates_report_only_after_payment_is_approved() -> None:
    repository = MemoryPaymentRepository()
    gateway = FakePaymentGateway()
    client, application = _client(repository, gateway)
    application.dependency_overrides[get_romantic_report_repository] = MemoryReportRepository
    application.dependency_overrides[get_romantic_report_generator] = FakeReportGenerator

    ready = client.post("/api/payments/kakaopay/ready", json=PURCHASE)
    assert ready.status_code == 200
    before_payment = client.post(f"/api/relationship-reports/romantic/orders/{ORDER_ID}")
    assert before_payment.status_code == 402

    approved = client.get(
        f"/api/payments/kakaopay/{ORDER_ID}/approve",
        params={"pg_token": "pg-token"},
        follow_redirects=False,
    )
    generated = client.post(f"/api/relationship-reports/romantic/orders/{ORDER_ID}")

    assert approved.status_code == 307
    assert generated.status_code == 200
    assert generated.json()["content"].startswith("## 1. 이 관계의 핵심 구조")
    assert repository.order is not None
    assert repository.order.fulfillment_reference == generated.json()["report_code"]
