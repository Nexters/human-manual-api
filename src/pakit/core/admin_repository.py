from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.models import (
    AssessmentResultRecord,
    BackendUsageEventRecord,
    PaymentOrderRecord,
    RomanticRelationshipReportRecord,
    UserRecord,
)
from pakit.services.admin_repository import (
    StoredAdminPaidReport,
    StoredAdminPayment,
    StoredAdminUser,
    StoredResult,
    StoredUsageEvent,
)


class SqlAlchemyAdminRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list_results(self) -> list[StoredResult]:
        records = (await self._session.scalars(select(AssessmentResultRecord))).all()
        return [self._to_result(record) for record in records]

    async def get_result(self, result_code: str) -> StoredResult | None:
        record = await self._session.scalar(
            select(AssessmentResultRecord).where(AssessmentResultRecord.result_code == result_code)
        )
        return self._to_result(record) if record is not None else None

    async def list_usage_events(self) -> list[StoredUsageEvent]:
        records = (await self._session.scalars(select(BackendUsageEventRecord))).all()
        return [
            StoredUsageEvent(
                event_name=record.event_name,  # type: ignore[arg-type]
                result_code=record.result_code,
                related_result_code=record.related_result_code,
                compatibility_score=record.compatibility_score,
                compatibility_version=record.compatibility_version,
                occurred_at=record.occurred_at,
            )
            for record in records
        ]

    async def list_payments(self) -> list[StoredAdminPayment]:
        records = (await self._session.scalars(select(PaymentOrderRecord))).all()
        return [self._to_payment(record) for record in records]

    async def get_payment(self, order_id: str) -> StoredAdminPayment | None:
        record = await self._session.scalar(
            select(PaymentOrderRecord).where(PaymentOrderRecord.order_id == order_id)
        )
        return self._to_payment(record) if record is not None else None

    async def list_users(self) -> list[StoredAdminUser]:
        users = (await self._session.scalars(select(UserRecord))).all()
        results = (await self._session.scalars(select(AssessmentResultRecord))).all()
        payments = (await self._session.scalars(select(PaymentOrderRecord))).all()
        result_codes: dict[int, list[str]] = defaultdict(list)
        user_payments: dict[int, list[PaymentOrderRecord]] = defaultdict(list)
        for result in results:
            if result.user_id is not None:
                result_codes[result.user_id].append(result.result_code)
        for payment in payments:
            user_payments[payment.user_id].append(payment)
        return [
            self._to_user(user, result_codes[user.id], user_payments[user.id]) for user in users
        ]

    async def get_user(self, user_id: int) -> StoredAdminUser | None:
        return next((user for user in await self.list_users() if user.user_id == user_id), None)

    async def list_paid_reports(self) -> list[StoredAdminPaidReport]:
        reports = (await self._session.scalars(select(RomanticRelationshipReportRecord))).all()
        payments = (
            await self._session.scalars(
                select(PaymentOrderRecord).where(
                    PaymentOrderRecord.status == "APPROVED",
                    PaymentOrderRecord.fulfillment_reference.is_not(None),
                )
            )
        ).all()
        paid_orders: dict[str, list[PaymentOrderRecord]] = defaultdict(list)
        for payment in payments:
            if payment.fulfillment_reference is not None:
                paid_orders[payment.fulfillment_reference].append(payment)
        return [
            self._to_paid_report(report, paid_orders[report.report_code])
            for report in reports
            if paid_orders[report.report_code]
        ]

    async def get_paid_report(self, report_code: str) -> StoredAdminPaidReport | None:
        return next(
            (
                report
                for report in await self.list_paid_reports()
                if report.report_code == report_code
            ),
            None,
        )

    @staticmethod
    def _to_result(record: AssessmentResultRecord) -> StoredResult:
        return StoredResult(
            result_code=record.result_code,
            assessment_version=record.assessment_version,
            content_version=record.content_version,
            snapshot=record.result_snapshot,
            created_at=record.created_at,
        )

    @staticmethod
    def _to_payment(record: PaymentOrderRecord) -> StoredAdminPayment:
        return StoredAdminPayment(
            order_id=record.order_id,
            user_id=record.user_id,
            product_code=record.product_code,
            product_name=record.product_name,
            product_payload=record.product_payload,
            amount=record.amount,
            currency=record.currency,
            status=record.status,
            kakaopay_tid=record.kakaopay_tid,
            kakaopay_aid=record.kakaopay_aid,
            payment_method_type=record.payment_method_type,
            report_code=record.fulfillment_reference,
            created_at=record.created_at,
            approved_at=record.approved_at,
        )

    @staticmethod
    def _to_user(
        record: UserRecord,
        result_codes: list[str],
        payments: list[PaymentOrderRecord],
    ) -> StoredAdminUser:
        approved = [payment for payment in payments if payment.status == "APPROVED"]
        return StoredAdminUser(
            user_id=record.id,
            created_at=record.created_at,
            last_logged_in_at=record.last_logged_in_at,
            result_codes=tuple(sorted(result_codes)),
            order_ids=tuple(
                payment.order_id
                for payment in sorted(payments, key=lambda item: item.created_at, reverse=True)
            ),
            report_codes=tuple(
                dict.fromkeys(
                    payment.fulfillment_reference
                    for payment in approved
                    if payment.fulfillment_reference is not None
                )
            ),
            approved_payment_count=len(approved),
            total_paid_amount=sum(payment.amount for payment in approved),
        )

    @staticmethod
    def _to_paid_report(
        record: RomanticRelationshipReportRecord,
        payments: list[PaymentOrderRecord],
    ) -> StoredAdminPaidReport:
        return StoredAdminPaidReport(
            report_code=record.report_code,
            order_ids=tuple(payment.order_id for payment in payments),
            user_ids=tuple(sorted({payment.user_id for payment in payments})),
            mine_result_code=record.mine_result_code,
            partner_result_code=record.partner_result_code,
            mine_gender=record.mine_gender,
            partner_gender=record.partner_gender,
            prompt_version=record.prompt_version,
            profile_version=record.profile_version,
            model=record.model,
            input_snapshot=record.input_snapshot,
            content=record.content,
            provider_response_id=record.provider_response_id,
            input_tokens=record.input_tokens,
            output_tokens=record.output_tokens,
            created_at=record.created_at,
        )
