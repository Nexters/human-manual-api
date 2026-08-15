from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.database import get_database_session
from pakit.core.result_repository import SqlAlchemyResultRepository
from pakit.services.result_repository import ResultRepository

DatabaseSession = Annotated[AsyncSession, Depends(get_database_session)]


def get_result_repository(session: DatabaseSession) -> ResultRepository:
    return SqlAlchemyResultRepository(session)
