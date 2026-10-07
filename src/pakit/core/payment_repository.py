from secrets import token_urlsafe
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.models import AssessmentResultRecord, PaymentOrderRecord
from pakit.services.payment_service import (
    ROMANTIC_REPORT_PRICE_KRW,
    ROMANTIC_REPORT_PRODUCT_CODE,
    PaymentApprovalResult,
    PaymentOrder,
    PaymentRepository,
    PaymentStatus,
    ResultAccess,
    RomanticReportPurchase,
)


class SqlAlchemyPaymentRepository(PaymentRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_result_access(
        self, user_id: int, mine_result_code: str, partner_result_code: str
    ) -> ResultAccess:
        records = (
            await self._session.scalars(
                select(AssessmentResultRecord).where(
                    AssessmentResultRecord.result_code.in_((mine_result_code, partner_result_code))
                )
            )
        ).all()
        by_code = {record.result_code: record for record in records}
        mine = by_code.get(mine_result_code)
        return ResultAccess(
            mine_exists=mine is not None,
            mine_owned_by_user=mine is not None and mine.user_id == user_id,
            partner_exists=partner_result_code in by_code,
        )

    async def create_order(self, user_id: int, purchase: RomanticReportPurchase) -> PaymentOrder:
        record = PaymentOrderRecord(
            order_id=token_urlsafe(18),
            user_id=user_id,
            product_code=ROMANTIC_REPORT_PRODUCT_CODE,
            product_name="Pakit 연인 관계 설명서",
            product_payload={
                "mine_result_code": purchase.mine_result_code,
                "partner_result_code": purchase.partner_result_code,
                "mine_gender": purchase.mine_gender,
                "partner_gender": purchase.partner_gender,
            },
            amount=ROMANTIC_REPORT_PRICE_KRW,
            currency="KRW",
            status="CREATED",
        )
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return _stored(record)

    async def set_ready(self, order_id: str, tid: str) -> PaymentOrder:
        record = await self._get(order_id)
        if record is None or record.status != "CREATED":
            raise RuntimeError("결제 준비 상태를 저장할 수 없습니다.")
        record.kakaopay_tid = tid
        record.status = "READY"
        await self._session.commit()
        await self._session.refresh(record)
        return _stored(record)

    async def set_failed(self, order_id: str, user_id: int) -> PaymentOrder | None:
        return await self._set_terminal_status(order_id, user_id, "FAILED")

    async def set_canceled(self, order_id: str, user_id: int) -> PaymentOrder | None:
        return await self._set_terminal_status(order_id, user_id, "CANCELED")

    async def get_for_user(self, order_id: str, user_id: int) -> PaymentOrder | None:
        record = await self._session.scalar(
            select(PaymentOrderRecord).where(
                PaymentOrderRecord.order_id == order_id,
                PaymentOrderRecord.user_id == user_id,
            )
        )
        return _stored(record) if record is not None else None

    async def set_approved(
        self,
        order_id: str,
        user_id: int,
        approval: PaymentApprovalResult,
    ) -> PaymentOrder | None:
        record = await self._session.scalar(
            select(PaymentOrderRecord)
            .where(
                PaymentOrderRecord.order_id == order_id,
                PaymentOrderRecord.user_id == user_id,
            )
            .with_for_update()
        )
        if record is None:
            return None
        if record.status == "APPROVED":
            return _stored(record)
        if record.status != "READY":
            return None
        record.status = "APPROVED"
        record.kakaopay_aid = approval.aid
        record.payment_method_type = approval.payment_method_type
        record.approved_at = approval.approved_at
        await self._session.commit()
        await self._session.refresh(record)
        return _stored(record)

    async def attach_report(
        self, order_id: str, user_id: int, report_code: str
    ) -> PaymentOrder | None:
        record = await self._session.scalar(
            select(PaymentOrderRecord)
            .where(
                PaymentOrderRecord.order_id == order_id,
                PaymentOrderRecord.user_id == user_id,
                PaymentOrderRecord.status == "APPROVED",
            )
            .with_for_update()
        )
        if record is None:
            return None
        record.fulfillment_reference = report_code
        await self._session.commit()
        await self._session.refresh(record)
        return _stored(record)

    async def _get(self, order_id: str) -> PaymentOrderRecord | None:
        record: PaymentOrderRecord | None = await self._session.scalar(
            select(PaymentOrderRecord).where(PaymentOrderRecord.order_id == order_id)
        )
        return record

    async def _set_terminal_status(
        self, order_id: str, user_id: int, status: str
    ) -> PaymentOrder | None:
        record = await self._session.scalar(
            select(PaymentOrderRecord).where(
                PaymentOrderRecord.order_id == order_id,
                PaymentOrderRecord.user_id == user_id,
            )
        )
        if record is None:
            return None
        if record.status != "APPROVED":
            record.status = status
            await self._session.commit()
            await self._session.refresh(record)
        return _stored(record)


def _stored(record: PaymentOrderRecord) -> PaymentOrder:
    payload = record.product_payload
    return PaymentOrder(
        order_id=record.order_id,
        user_id=record.user_id,
        product_code=record.product_code,
        product_name=record.product_name,
        purchase=RomanticReportPurchase(
            mine_result_code=str(payload["mine_result_code"]),
            partner_result_code=str(payload["partner_result_code"]),
            mine_gender=str(payload["mine_gender"]),
            partner_gender=str(payload["partner_gender"]),
        ),
        amount=record.amount,
        status=cast(PaymentStatus, record.status),
        tid=record.kakaopay_tid,
        aid=record.kakaopay_aid,
        fulfillment_reference=record.fulfillment_reference,
        created_at=record.created_at,
        approved_at=record.approved_at,
    )
