import asyncio
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from pakit.core.models import AssessmentResultRecord, Base, UserRecord
from pakit.core.payment_repository import SqlAlchemyPaymentRepository
from pakit.services.payment_service import PaymentApprovalResult, RomanticReportPurchase


def test_persists_payment_order_and_enforces_result_ownership() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            user = UserRecord(kakao_user_id="kakao-123")
            other = UserRecord(kakao_user_id="kakao-456")
            session.add_all((user, other))
            await session.flush()
            session.add_all(
                (
                    _result("MINE0001", user.id),
                    _result("FRIEND01", other.id),
                )
            )
            await session.commit()

            repository = SqlAlchemyPaymentRepository(session)
            access = await repository.get_result_access(user.id, "MINE0001", "FRIEND01")
            denied = await repository.get_result_access(other.id, "MINE0001", "FRIEND01")
            order = await repository.create_order(
                user.id,
                RomanticReportPurchase("MINE0001", "FRIEND01", "여자", "남자"),
            )
            ready = await repository.set_ready(order.order_id, "T1234567890123456789")
            approved = await repository.set_approved(
                order.order_id,
                user.id,
                PaymentApprovalResult(
                    aid="A1234567890123456789",
                    tid="T1234567890123456789",
                    partner_order_id=order.order_id,
                    partner_user_id=f"pakit-{user.id}",
                    amount=990,
                    payment_method_type="MONEY",
                    approved_at=datetime(2026, 10, 7, tzinfo=UTC),
                ),
            )
            exact_order = await repository.find_approved_romantic_report_order(
                user.id, "MINE0001", "FRIEND01"
            )
            reverse_order = await repository.find_approved_romantic_report_order(
                user.id, "FRIEND01", "MINE0001"
            )

        await engine.dispose()
        assert access.mine_owned_by_user is True
        assert denied.mine_owned_by_user is False
        assert ready.status == "READY"
        assert approved is not None
        assert approved.status == "APPROVED"
        assert approved.amount == 990
        assert exact_order is not None
        assert exact_order.order_id == order.order_id
        assert reverse_order is None

    asyncio.run(run())


def _result(result_code: str, user_id: int) -> AssessmentResultRecord:
    return AssessmentResultRecord(
        result_code=result_code,
        assessment_version="v1",
        content_version="v1",
        result_snapshot={},
        response_snapshot={},
        user_id=user_id,
    )
