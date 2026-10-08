from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.models import AssessmentResultRecord, RomanticRelationshipReportRecord
from pakit.services.romantic_report_repository import (
    RelationshipProfileSource,
    RelationshipProfileSourceUnavailableError,
    RomanticReportRepository,
    RomanticReportToSave,
    StoredRomanticReport,
)


class SqlAlchemyRomanticReportRepository(RomanticReportRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_report_code(self, report_code: str) -> StoredRomanticReport | None:
        record = await self._session.scalar(
            select(RomanticRelationshipReportRecord).where(
                RomanticRelationshipReportRecord.report_code == report_code
            )
        )
        return _stored(record) if record is not None else None

    async def get_profile_source(self, result_code: str) -> RelationshipProfileSource | None:
        record = await self._session.scalar(
            select(AssessmentResultRecord).where(AssessmentResultRecord.result_code == result_code)
        )
        if record is None:
            return None
        if record.response_snapshot is None:
            raise RelationshipProfileSourceUnavailableError
        result = record.result_snapshot
        response = record.response_snapshot
        participant = result.get("participant") or {}
        nickname = participant.get("nickname")
        scores = (result.get("unboxing_kit") or {}).get("axis_scores")
        answers = response.get("answers")
        mbti = response.get("mbti")
        assessment_version = response.get("assessment_version")
        if not (
            isinstance(nickname, str)
            and isinstance(scores, dict)
            and isinstance(answers, list)
            and isinstance(mbti, str)
            and isinstance(assessment_version, str)
        ):
            raise RelationshipProfileSourceUnavailableError
        try:
            return RelationshipProfileSource(
                result_code=result_code,
                nickname=nickname,
                mbti=mbti,
                assessment_version=assessment_version,
                axis_scores={key: int(value) for key, value in scores.items()},
                answers={str(item["question_id"]): item["value"] for item in answers},
            )
        except (KeyError, TypeError, ValueError) as error:
            raise RelationshipProfileSourceUnavailableError from error

    async def find_existing(
        self,
        *,
        mine_result_code: str,
        partner_result_code: str,
        mine_gender: str,
        partner_gender: str,
        prompt_version: str,
        profile_version: str,
        model: str,
    ) -> StoredRomanticReport | None:
        record = await self._session.scalar(
            select(RomanticRelationshipReportRecord).where(
                RomanticRelationshipReportRecord.mine_result_code == mine_result_code,
                RomanticRelationshipReportRecord.partner_result_code == partner_result_code,
                RomanticRelationshipReportRecord.mine_gender == mine_gender,
                RomanticRelationshipReportRecord.partner_gender == partner_gender,
                RomanticRelationshipReportRecord.prompt_version == prompt_version,
                RomanticRelationshipReportRecord.profile_version == profile_version,
                RomanticRelationshipReportRecord.model == model,
            )
        )
        return _stored(record) if record is not None else None

    async def save(self, report: RomanticReportToSave) -> StoredRomanticReport:
        record = RomanticRelationshipReportRecord(**report.__dict__)
        self._session.add(record)
        await self._session.commit()
        await self._session.refresh(record)
        return _stored(record)


def _stored(record: RomanticRelationshipReportRecord) -> StoredRomanticReport:
    return StoredRomanticReport(
        report_code=record.report_code,
        content=record.content,
        created_at=record.created_at,
    )
