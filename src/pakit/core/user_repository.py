from datetime import UTC, datetime
from typing import Any

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.models import AssessmentResultRecord, BackendUsageEventRecord, UserRecord
from pakit.services.user_repository import (
    ResultSyncSummary,
    StoredUser,
    UserCompatibilitySummary,
    UserResultSummary,
)


def _stored_user(record: UserRecord) -> StoredUser:
    return StoredUser(
        id=record.id,
        created_at=record.created_at,
        last_logged_in_at=record.last_logged_in_at,
    )


def _result_summary(record: AssessmentResultRecord) -> UserResultSummary:
    snapshot: dict[str, Any] = record.result_snapshot
    participant = snapshot.get("participant")
    overview = snapshot["overview"]
    return UserResultSummary(
        result_code=record.result_code,
        nickname=participant.get("nickname") if participant is not None else None,
        result_name=overview["result_name"],
        noun=overview["noun"],
        character_id=overview["character_id"],
        image_url=overview["image_url"],
        created_at=record.created_at,
    )


class SqlAlchemyUserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def upsert_kakao_user(self, kakao_user_id: str) -> StoredUser:
        record = await self._session.scalar(
            select(UserRecord).where(UserRecord.kakao_user_id == kakao_user_id)
        )
        now = datetime.now(UTC)
        if record is None:
            record = UserRecord(kakao_user_id=kakao_user_id, last_logged_in_at=now)
            self._session.add(record)
        else:
            record.last_logged_in_at = now
        await self._session.commit()
        await self._session.refresh(record)
        return _stored_user(record)

    async def get_user(self, user_id: int) -> StoredUser | None:
        record = await self._session.get(UserRecord, user_id)
        return _stored_user(record) if record is not None else None

    async def sync_results(
        self,
        user_id: int,
        result_codes: tuple[str, ...],
    ) -> ResultSyncSummary:
        unique_codes = tuple(dict.fromkeys(result_codes))
        records = (
            await self._session.scalars(
                select(AssessmentResultRecord).where(
                    AssessmentResultRecord.result_code.in_(unique_codes)
                )
            )
        ).all()
        by_code = {record.result_code: record for record in records}
        synced: list[str] = []
        already_synced: list[str] = []
        rejected: list[str] = []
        for result_code in unique_codes:
            record = by_code.get(result_code)
            if record is None or record.user_id not in {None, user_id}:
                rejected.append(result_code)
            elif record.user_id == user_id:
                already_synced.append(result_code)
            else:
                record.user_id = user_id
                synced.append(result_code)
        await self._session.commit()
        return ResultSyncSummary(
            synced=tuple(synced),
            already_synced=tuple(already_synced),
            rejected=tuple(rejected),
        )

    async def list_results(self, user_id: int) -> list[UserResultSummary]:
        records = (
            await self._session.scalars(
                select(AssessmentResultRecord)
                .where(AssessmentResultRecord.user_id == user_id)
                .order_by(
                    AssessmentResultRecord.created_at.desc(),
                    AssessmentResultRecord.id.desc(),
                )
            )
        ).all()
        return [_result_summary(record) for record in records]

    async def list_compatibilities(self, user_id: int) -> list[UserCompatibilitySummary]:
        owned_records = (
            await self._session.scalars(
                select(AssessmentResultRecord).where(AssessmentResultRecord.user_id == user_id)
            )
        ).all()
        owned_by_code = {record.result_code: record for record in owned_records}
        if not owned_by_code:
            return []

        owned_codes = tuple(owned_by_code)
        events = (
            await self._session.scalars(
                select(BackendUsageEventRecord)
                .where(
                    BackendUsageEventRecord.event_name == "compatibility_completed",
                    BackendUsageEventRecord.related_result_code.is_not(None),
                    BackendUsageEventRecord.compatibility_score.is_not(None),
                    or_(
                        BackendUsageEventRecord.result_code.in_(owned_codes),
                        BackendUsageEventRecord.related_result_code.in_(owned_codes),
                    ),
                )
                .order_by(
                    BackendUsageEventRecord.occurred_at.desc(),
                    BackendUsageEventRecord.id.desc(),
                )
            )
        ).all()
        all_codes = {
            code
            for event in events
            for code in (event.result_code, event.related_result_code)
            if code is not None
        }
        result_records = (
            await self._session.scalars(
                select(AssessmentResultRecord).where(
                    AssessmentResultRecord.result_code.in_(all_codes)
                )
            )
        ).all()
        results_by_code = {record.result_code: record for record in result_records}

        seen_pairs: set[tuple[str, str]] = set()
        summaries: list[UserCompatibilitySummary] = []
        for event in events:
            friend_code = event.related_result_code
            score = event.compatibility_score
            if friend_code is None or score is None:
                continue
            pair = (
                min(event.result_code, friend_code),
                max(event.result_code, friend_code),
            )
            if pair in seen_pairs:
                continue
            seen_pairs.add(pair)
            if event.result_code in owned_by_code:
                mine_code, other_code = event.result_code, friend_code
            else:
                mine_code, other_code = friend_code, event.result_code
            mine_record = results_by_code.get(mine_code)
            other_record = results_by_code.get(other_code)
            if mine_record is None or other_record is None:
                continue
            summaries.append(
                UserCompatibilitySummary(
                    mine=_result_summary(mine_record),
                    friend=_result_summary(other_record),
                    score=score,
                    tested_at=event.occurred_at,
                )
            )
        return summaries
