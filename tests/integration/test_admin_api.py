from datetime import UTC, datetime, timedelta
from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import SecretStr
from pytest import MonkeyPatch

import pakit.api.admin_auth as admin_auth
import pakit.api.routes.admin as admin_routes
from pakit.api.dependencies import (
    get_admin_repository,
    get_payment_repository,
    get_romantic_report_generator,
    get_romantic_report_repository,
)
from pakit.core.config import Settings
from pakit.main import create_app
from pakit.services.admin_repository import (
    StoredAdminPaidReport,
    StoredAdminPayment,
    StoredAdminUser,
    StoredResult,
    StoredUsageEvent,
)
from pakit.services.payment_service import PaymentOrder
from pakit.services.romantic_report_generator import GeneratedRelationshipReport
from pakit.services.romantic_report_repository import (
    RelationshipProfileSource,
    RomanticReportToSave,
    StoredRomanticReport,
)


def _result(code: str, mbti: str, created_at: datetime, nickname: str) -> StoredResult:
    return StoredResult(
        result_code=code,
        assessment_version="questions-v1",
        content_version="content-v1",
        created_at=created_at,
        snapshot={
            "participant": {"nickname": nickname},
            "overview": {
                "result_name": "팽이 지은",
                "character_id": "spinning_top",
                "tags": ["장난꾸러기", "도파민 MAX", "혼자서도 잘 놀아요"],
            },
            "unboxing_kit": {
                "axis_scores": {
                    "attachment": 25,
                    "expression": 75,
                    "routine": 10,
                    "egen": 50,
                }
            },
            "compatibility_profile": {"mbti": mbti},
        },
    )


class FakeAdminRepository:
    def __init__(
        self,
        results: list[StoredResult],
        events: list[StoredUsageEvent],
        payments: list[StoredAdminPayment],
        users: list[StoredAdminUser],
        paid_reports: list[StoredAdminPaidReport],
    ) -> None:
        self.results = results
        self.events = events
        self.payments = payments
        self.users = users
        self.paid_reports = paid_reports

    async def list_results(self) -> list[StoredResult]:
        return self.results

    async def get_result(self, result_code: str) -> StoredResult | None:
        return next((result for result in self.results if result.result_code == result_code), None)

    async def list_usage_events(self) -> list[StoredUsageEvent]:
        return self.events

    async def list_payments(self) -> list[StoredAdminPayment]:
        return self.payments

    async def get_payment(self, order_id: str) -> StoredAdminPayment | None:
        return next((payment for payment in self.payments if payment.order_id == order_id), None)

    async def list_users(self) -> list[StoredAdminUser]:
        return self.users

    async def get_user(self, user_id: int) -> StoredAdminUser | None:
        return next((user for user in self.users if user.user_id == user_id), None)

    async def list_paid_reports(self) -> list[StoredAdminPaidReport]:
        return self.paid_reports

    async def get_paid_report(self, report_code: str) -> StoredAdminPaidReport | None:
        return next(
            (report for report in self.paid_reports if report.report_code == report_code), None
        )


def _event(
    name: str,
    code: str,
    occurred_at: datetime,
    *,
    friend: str | None = None,
    score: int | None = None,
) -> StoredUsageEvent:
    return StoredUsageEvent(
        event_name=name,  # type: ignore[arg-type]
        result_code=code,
        related_result_code=friend,
        compatibility_score=score,
        compatibility_version="rules-v1" if score else None,
        occurred_at=occurred_at,
    )


def _client(monkeypatch: MonkeyPatch, *, configured: bool = True) -> TestClient:
    started_at = datetime(2026, 8, 20, tzinfo=UTC)
    settings = Settings(
        admin_username="operator" if configured else None,
        admin_password=SecretStr("correct-horse") if configured else None,
        usage_tracking_started_at=started_at,
    )
    monkeypatch.setattr(admin_auth, "get_settings", lambda: settings)
    monkeypatch.setattr(admin_routes, "get_settings", lambda: settings)
    application = create_app()
    results = [
        _result("RESULT01", "ENTP", started_at, "해서니"),
        _result("RESULT02", "INTJ", started_at + timedelta(minutes=1), "선우"),
    ]
    events = [
        _event("result_viewed", "RESULT01", started_at + timedelta(hours=1)),
        _event(
            "compatibility_completed",
            "RESULT01",
            started_at + timedelta(hours=2),
            friend="RESULT02",
            score=84,
        ),
    ]
    order_id = "order_123456789012345"
    report_code = "REPORT000001"
    payments = [
        StoredAdminPayment(
            order_id=order_id,
            user_id=42,
            product_code="romantic-report-v1",
            product_name="Pakit 연인 관계 설명서",
            product_payload={
                "mine_result_code": "RESULT01",
                "partner_result_code": "RESULT02",
                "mine_gender": "여자",
                "partner_gender": "남자",
            },
            amount=990,
            currency="KRW",
            status="APPROVED",
            kakaopay_tid="T1234567890123456789",
            kakaopay_aid="A1234567890123456789",
            payment_method_type="MONEY",
            report_code=report_code,
            created_at=started_at + timedelta(hours=3),
            approved_at=started_at + timedelta(hours=4),
        )
    ]
    users = [
        StoredAdminUser(
            user_id=42,
            created_at=started_at,
            last_logged_in_at=started_at + timedelta(hours=2),
            result_codes=("RESULT01",),
            order_ids=(order_id,),
            report_codes=(report_code,),
            approved_payment_count=1,
            total_paid_amount=990,
        )
    ]
    paid_reports = [
        StoredAdminPaidReport(
            report_code=report_code,
            order_ids=(order_id,),
            user_ids=(42,),
            mine_result_code="RESULT01",
            partner_result_code="RESULT02",
            mine_gender="여자",
            partner_gender="남자",
            prompt_version="prompt-v1",
            profile_version="profile-v1",
            model="test-model",
            input_snapshot={"profiles": ["A", "B"]},
            content="관계 설명서 본문",
            provider_response_id="response-1",
            input_tokens=100,
            output_tokens=200,
            created_at=started_at + timedelta(hours=5),
        )
    ]
    repository = FakeAdminRepository(results, events, payments, users, paid_reports)
    application.dependency_overrides[get_admin_repository] = lambda: repository
    return TestClient(application)


def test_admin_is_closed_when_credentials_are_not_configured(monkeypatch: MonkeyPatch) -> None:
    client = _client(monkeypatch, configured=False)

    response = client.get("/admin")

    assert response.status_code == 503
    assert response.headers["cache-control"] == "no-store"


def test_admin_requires_basic_authentication(monkeypatch: MonkeyPatch) -> None:
    client = _client(monkeypatch)

    response = client.get("/api/admin/dashboard", auth=("operator", "wrong"))

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"
    assert response.headers["cache-control"] == "no-store"


def test_admin_html_and_read_only_apis_show_results_and_conversion(
    monkeypatch: MonkeyPatch,
) -> None:
    client = _client(monkeypatch)
    auth = ("operator", "correct-horse")

    html = client.get("/admin", auth=auth)
    dashboard = client.get("/api/admin/dashboard", auth=auth)
    results = client.get("/api/admin/results", auth=auth)
    results_with_compatibility = client.get("/api/admin/results?has_compatibility=true", auth=auth)
    detail = client.get("/api/admin/results/RESULT01", auth=auth)
    friend_detail = client.get("/api/admin/results/RESULT02", auth=auth)
    analytics = client.get("/api/admin/analytics/compatibility", auth=auth)
    missing = client.get("/api/admin/results/UNKNOWN1", auth=auth)

    assert html.status_code == 200
    assert "Pakit Admin" in html.text
    assert "궁합 도달 결과" in html.text
    assert "결제 내역" in html.text
    assert "로그인 유저" in html.text
    assert "유료 결과" in html.text
    assert html.headers["cache-control"] == "no-store"
    assert dashboard.status_code == 200
    assert dashboard.headers["cache-control"] == "no-store"
    assert dashboard.json()["counts"]["total_results"] == 2
    assert dashboard.json()["experience_ratio"] == 50.0
    assert results.json()["items"][0]["nickname"] == "선우"
    assert results.json()["items"][0]["compatibility_count"] == 1
    assert results.json()["items"][1]["nickname"] == "해서니"
    assert results.json()["items"][1]["compatibility_count"] == 1
    assert results_with_compatibility.json()["total"] == 2
    assert detail.json()["nickname"] == "해서니"
    assert detail.json()["usage"] == {
        "view_count": 1,
        "last_viewed_at": "2026-08-20T01:00:00Z",
        "compatibility_count": 1,
    }
    assert friend_detail.json()["usage"]["compatibility_count"] == 1
    assert analytics.json()["completed_count"] == 1
    assert analytics.json()["total_result_count"] == 2
    assert analytics.json()["experienced_result_count"] == 1
    assert missing.status_code == 404
    assert missing.headers["cache-control"] == "no-store"


def test_admin_read_only_commerce_tabs_show_linked_data(monkeypatch: MonkeyPatch) -> None:
    client = _client(monkeypatch)
    auth = ("operator", "correct-horse")
    order_id = "order_123456789012345"
    report_code = "REPORT000001"

    payments_page = client.get("/admin/payments", auth=auth)
    users_page = client.get("/admin/users", auth=auth)
    reports_page = client.get("/admin/paid-reports", auth=auth)
    payments = client.get("/api/admin/payments?status=APPROVED", auth=auth)
    payment = client.get(f"/api/admin/payments/{order_id}", auth=auth)
    users = client.get("/api/admin/users?user_id=42", auth=auth)
    user = client.get("/api/admin/users/42", auth=auth)
    reports = client.get("/api/admin/paid-reports?user_id=42", auth=auth)
    report = client.get(f"/api/admin/paid-reports/{report_code}", auth=auth)

    assert payments_page.status_code == 200
    assert users_page.status_code == 200
    assert reports_page.status_code == 200
    assert payments.json()["total"] == 1
    assert payments.json()["items"][0]["amount"] == 990
    assert payment.json()["report_code"] == report_code
    assert users.json()["total"] == 1
    assert user.json()["order_ids"] == [order_id]
    assert reports.json()["total"] == 1
    assert report.json()["content"] == "관계 설명서 본문"
    assert report.json()["order_ids"] == [order_id]
    assert all(
        response.headers["cache-control"] == "no-store"
        for response in (
            payments_page,
            users_page,
            reports_page,
            payments,
            payment,
            users,
            user,
            reports,
            report,
        )
    )


class RefreshPaymentRepository:
    def __init__(self) -> None:
        self.attached_report_code: str | None = None

    async def attach_report(
        self, order_id: str, user_id: int, report_code: str
    ) -> PaymentOrder | None:
        self.attached_report_code = report_code
        return object()  # type: ignore[return-value]


class RefreshReportRepository:
    report = StoredRomanticReport(
        "REPORT000002", "새 관계 설명서", datetime(2026, 10, 8, tzinfo=UTC)
    )

    async def get_by_report_code(self, report_code: str) -> StoredRomanticReport | None:
        return self.report if report_code == self.report.report_code else None

    async def get_profile_source(self, result_code: str) -> RelationshipProfileSource | None:
        return None

    async def find_existing(self, **keys: str) -> StoredRomanticReport | None:
        return self.report

    async def save(self, report: RomanticReportToSave) -> StoredRomanticReport:
        raise AssertionError("현재 버전 보고서를 재사용해야 합니다.")


class RefreshGenerator:
    model = "test-model"

    async def generate(self, *, instructions: str, user_prompt: str) -> GeneratedRelationshipReport:
        raise AssertionError("현재 버전 보고서를 재사용해야 합니다.")


def test_admin_can_refresh_one_paid_order_to_current_report(monkeypatch: MonkeyPatch) -> None:
    client = _client(monkeypatch)
    payment_repository = RefreshPaymentRepository()
    application = cast(FastAPI, client.app)
    application.dependency_overrides[get_payment_repository] = lambda: payment_repository
    application.dependency_overrides[get_romantic_report_repository] = RefreshReportRepository
    application.dependency_overrides[get_romantic_report_generator] = RefreshGenerator

    response = client.post(
        "/api/admin/payments/order_123456789012345/relationship-report/refresh",
        auth=("operator", "correct-horse"),
    )

    assert response.status_code == 200
    assert response.json()["report_code"] == "REPORT000002"
    assert payment_repository.attached_report_code == "REPORT000002"
