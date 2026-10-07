from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.admin_repository import SqlAlchemyAdminRepository
from pakit.core.config import Settings, get_settings
from pakit.core.database import get_database_session
from pakit.core.kakaopay import KakaoPayClient
from pakit.core.openai_romantic_report_generator import OpenAIRomanticReportGenerator
from pakit.core.payment_repository import SqlAlchemyPaymentRepository
from pakit.core.result_repository import SqlAlchemyResultRepository
from pakit.core.romantic_report_repository import SqlAlchemyRomanticReportRepository
from pakit.core.usage_event_repository import SqlAlchemyUsageEventRepository
from pakit.core.user_repository import SqlAlchemyUserRepository
from pakit.services.admin_repository import AdminRepository
from pakit.services.payment_service import PaymentGateway, PaymentRepository
from pakit.services.result_repository import ResultRepository
from pakit.services.romantic_report_generator import RomanticReportGenerator
from pakit.services.romantic_report_repository import RomanticReportRepository
from pakit.services.usage_event_repository import CompatibilityEventReader, UsageEventRepository
from pakit.services.user_repository import UserRepository

DatabaseSession = Annotated[AsyncSession, Depends(get_database_session)]


def get_result_repository(session: DatabaseSession) -> ResultRepository:
    return SqlAlchemyResultRepository(session)


def get_usage_event_repository(session: DatabaseSession) -> UsageEventRepository:
    return SqlAlchemyUsageEventRepository(session)


def get_compatibility_event_reader(session: DatabaseSession) -> CompatibilityEventReader:
    return SqlAlchemyUsageEventRepository(session)


def get_admin_repository(session: DatabaseSession) -> AdminRepository:
    return SqlAlchemyAdminRepository(session)


def get_user_repository(session: DatabaseSession) -> UserRepository:
    return SqlAlchemyUserRepository(session)


def get_payment_repository(session: DatabaseSession) -> PaymentRepository:
    return SqlAlchemyPaymentRepository(session)


def get_payment_gateway(
    settings: Annotated[Settings, Depends(get_settings)],
) -> PaymentGateway | None:
    if settings.kakaopay_cid is None or settings.kakaopay_secret_key is None:
        return None
    return KakaoPayClient(
        cid=settings.kakaopay_cid,
        secret_key=settings.kakaopay_secret_key.get_secret_value(),
        timeout_seconds=settings.kakaopay_timeout_seconds,
    )


def get_romantic_report_repository(session: DatabaseSession) -> RomanticReportRepository:
    return SqlAlchemyRomanticReportRepository(session)


def get_romantic_report_generator(
    settings: Annotated[Settings, Depends(get_settings)],
) -> RomanticReportGenerator | None:
    if settings.openai_api_key is None or settings.openai_model is None:
        return None
    return OpenAIRomanticReportGenerator(
        api_key=settings.openai_api_key.get_secret_value(),
        model=settings.openai_model,
        max_output_tokens=settings.openai_max_output_tokens,
        timeout_seconds=settings.openai_timeout_seconds,
    )
