from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.admin_repository import SqlAlchemyAdminRepository
from pakit.core.database import get_database_session
from pakit.core.result_repository import SqlAlchemyResultRepository
from pakit.core.usage_event_repository import SqlAlchemyUsageEventRepository
from pakit.services.admin_repository import AdminRepository
from pakit.services.result_repository import ResultRepository
from pakit.services.usage_event_repository import UsageEventRepository

DatabaseSession = Annotated[AsyncSession, Depends(get_database_session)]


def get_result_repository(session: DatabaseSession) -> ResultRepository:
    return SqlAlchemyResultRepository(session)


def get_usage_event_repository(session: DatabaseSession) -> UsageEventRepository:
    return SqlAlchemyUsageEventRepository(session)


def get_admin_repository(session: DatabaseSession) -> AdminRepository:
    return SqlAlchemyAdminRepository(session)
