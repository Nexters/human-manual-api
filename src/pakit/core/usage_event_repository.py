from datetime import datetime

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.models import BackendUsageEventRecord
from pakit.services.usage_event_repository import StoredCompatibilityEvent, UsageEventName


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

    async def list_compatibility_events(
        self,
        result_code: str,
    ) -> list[StoredCompatibilityEvent]:
        records = (
            await self._session.scalars(
                select(BackendUsageEventRecord)
                .where(
                    BackendUsageEventRecord.event_name == "compatibility_completed",
                    BackendUsageEventRecord.related_result_code.is_not(None),
                    BackendUsageEventRecord.compatibility_score.is_not(None),
                    BackendUsageEventRecord.compatibility_version.is_not(None),
                    or_(
                        BackendUsageEventRecord.result_code == result_code,
                        BackendUsageEventRecord.related_result_code == result_code,
                    ),
                )
                .order_by(
                    BackendUsageEventRecord.occurred_at.desc(),
                    BackendUsageEventRecord.id.desc(),
                )
            )
        ).all()
        return [
            StoredCompatibilityEvent(
                mine_result_code=record.result_code,
                friend_result_code=record.related_result_code,
                score=record.compatibility_score,
                version=record.compatibility_version,
                occurred_at=record.occurred_at,
            )
            for record in records
            if record.related_result_code is not None
            and record.compatibility_score is not None
            and record.compatibility_version is not None
        ]
