from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.models import BackendUsageEventRecord
from pakit.services.usage_event_repository import UsageEventName


class SqlAlchemyUsageEventRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def record(
        self,
        *,
        event_name: UsageEventName,
        result_code: str,
        related_result_code: str | None = None,
        compatibility_score: int | None = None,
        compatibility_version: str | None = None,
        occurred_at: datetime | None = None,
    ) -> None:
        self._session.add(
            BackendUsageEventRecord(
                event_name=event_name,
                result_code=result_code,
                related_result_code=related_result_code,
                compatibility_score=compatibility_score,
                compatibility_version=compatibility_version,
                **({"occurred_at": occurred_at} if occurred_at is not None else {}),
            )
        )
        await self._session.commit()
