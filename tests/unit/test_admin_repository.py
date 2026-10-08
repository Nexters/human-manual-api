import asyncio
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from pakit.core.admin_repository import SqlAlchemyAdminRepository
from pakit.core.models import (
    AssessmentResultRecord,
    Base,
    PaymentOrderRecord,
    RomanticRelationshipReportRecord,
    UserRecord,
)


def test_lists_linked_users_payments_and_paid_reports() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        now = datetime(2026, 10, 8, tzinfo=UTC)
        order_id = "order_123456789012345"
        report_code = "REPORT000001"

        async with sessions() as session:
            user = UserRecord(
                kakao_user_id="private-kakao-id",
                created_at=now,
                last_logged_in_at=now,
            )
            session.add(user)
            await session.flush()
            session.add(
                AssessmentResultRecord(
                    result_code="RESULT01",
                    assessment_version="v1",
                    content_version="v1",
                    result_snapshot={},
                    response_snapshot={},
                    user_id=user.id,
                    created_at=now,
                )
            )
            session.add(
                RomanticRelationshipReportRecord(
                    report_code=report_code,
                    mine_result_code="RESULT01",
                    partner_result_code="RESULT02",
                    mine_gender="여자",
                    partner_gender="남자",
                    prompt_version="prompt-v1",
                    profile_version="profile-v1",
                    model="test-model",
                    input_snapshot={"profiles": []},
                    content="유료 결과 본문",
                    input_tokens=10,
                    output_tokens=20,
                    created_at=now,
                )
            )
            session.add(
                PaymentOrderRecord(
                    order_id=order_id,
                    user_id=user.id,
                    product_code="romantic-report-v1",
                    product_name="Pakit 연인 관계 설명서",
                    product_payload={"mine_result_code": "RESULT01"},
                    amount=990,
                    currency="KRW",
                    status="APPROVED",
                    kakaopay_tid="T1234567890123456789",
                    fulfillment_reference=report_code,
                    created_at=now,
                    approved_at=now,
                )
            )
            await session.commit()

            repository = SqlAlchemyAdminRepository(session)
            payments = await repository.list_payments()
            users = await repository.list_users()
            reports = await repository.list_paid_reports()
            payment = await repository.get_payment(order_id)
            stored_user = await repository.get_user(user.id)
            report = await repository.get_paid_report(report_code)

        await engine.dispose()

        assert payments == [payment]
        assert payment is not None
        assert payment.product_payload == {"mine_result_code": "RESULT01"}
        assert users == [stored_user]
        assert stored_user is not None
        assert stored_user.result_codes == ("RESULT01",)
        assert stored_user.approved_payment_count == 1
        assert stored_user.total_paid_amount == 990
        assert reports == [report]
        assert report is not None
        assert report.order_ids == (order_id,)
        assert report.user_ids == (user.id,)
        assert report.content == "유료 결과 본문"

    asyncio.run(run())
