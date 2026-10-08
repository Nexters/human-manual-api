import asyncio
from datetime import UTC, datetime
from typing import cast

from pakit.services.payment_service import (
    PaymentOrder,
    PaymentRepository,
    RomanticReportPurchase,
    get_relationship_report_access,
)


class ApprovedOrderLookup:
    def __init__(self, order: PaymentOrder | None) -> None:
        self.order = order

    async def find_approved_romantic_report_order(
        self, user_id: int, mine_result_code: str, partner_result_code: str
    ) -> PaymentOrder | None:
        return self.order


def test_reports_login_purchase_generation_and_ready_states() -> None:
    pending = _order(report_code=None)
    ready = _order(report_code="report-123")

    async def run() -> None:
        login_required = await get_relationship_report_access(
            user_id=None,
            mine_result_code="MINE0001",
            partner_result_code="FRIEND01",
            repository=cast(PaymentRepository, ApprovedOrderLookup(ready)),
        )
        not_purchased = await get_relationship_report_access(
            user_id=42,
            mine_result_code="MINE0001",
            partner_result_code="FRIEND01",
            repository=cast(PaymentRepository, ApprovedOrderLookup(None)),
        )
        paid_pending = await get_relationship_report_access(
            user_id=42,
            mine_result_code="MINE0001",
            partner_result_code="FRIEND01",
            repository=cast(PaymentRepository, ApprovedOrderLookup(pending)),
        )
        fulfilled = await get_relationship_report_access(
            user_id=42,
            mine_result_code="MINE0001",
            partner_result_code="FRIEND01",
            repository=cast(PaymentRepository, ApprovedOrderLookup(ready)),
        )

        assert login_required.status == "LOGIN_REQUIRED"
        assert not_purchased.status == "NOT_PURCHASED"
        assert paid_pending.status == "PAID_PENDING_REPORT"
        assert paid_pending.order_id == "order-123"
        assert fulfilled.status == "READY"
        assert fulfilled.report_code == "report-123"

    asyncio.run(run())


def _order(*, report_code: str | None) -> PaymentOrder:
    now = datetime(2026, 10, 8, tzinfo=UTC)
    return PaymentOrder(
        order_id="order-123",
        user_id=42,
        product_code="romantic-report-v1",
        product_name="Pakit 연인 관계 설명서",
        purchase=RomanticReportPurchase("MINE0001", "FRIEND01", "여자", "남자"),
        amount=990,
        status="APPROVED",
        tid="tid",
        aid="aid",
        fulfillment_reference=report_code,
        created_at=now,
        approved_at=now,
    )
