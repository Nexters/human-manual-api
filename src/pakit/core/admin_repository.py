from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.models import AssessmentResultRecord, BackendUsageEventRecord
from pakit.services.admin_repository import StoredResult, StoredUsageEvent


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

    @staticmethod
    def _to_result(record: AssessmentResultRecord) -> StoredResult:
        return StoredResult(
            result_code=record.result_code,
            assessment_version=record.assessment_version,
            content_version=record.content_version,
            snapshot=record.result_snapshot,
            created_at=record.created_at,
        )
