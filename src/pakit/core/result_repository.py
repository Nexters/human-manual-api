from dataclasses import asdict
from typing import Any

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from pakit.core.models import AssessmentResultRecord
from pakit.domain.assessment_submission import (
    AxisScoresData,
    CharacterStoryData,
    ChargingActivityData,
    ChargingData,
    FeatureData,
    OverviewData,
    ResultParticipantData,
    SubmissionResultData,
    UnboxingItemData,
    UnboxingKitData,
)
from pakit.services.result_repository import ResultCodeConflictError


def _unboxing_item(snapshot: dict[str, Any]) -> UnboxingItemData:
    return UnboxingItemData(
        type=snapshot["type"],
        name=snapshot["name"],
        tags=tuple(snapshot["tags"]),
        reason=snapshot["reason"],
    )


def _result_from_snapshot(snapshot: dict[str, Any]) -> SubmissionResultData:
    overview = snapshot["overview"]
    unboxing = snapshot["unboxing_kit"]
    scores = unboxing["axis_scores"]
    story = snapshot["character_story"]
    charging = snapshot["charging"]
    participant = snapshot.get("participant")

    return SubmissionResultData(
        result_code=snapshot["result_code"],
        participant=(
            ResultParticipantData(nickname=participant["nickname"])
            if participant is not None
            else None
        ),
        overview=OverviewData(
            rarity=overview["rarity"],
            adjective=overview["adjective"],
            noun=overview["noun"],
            result_name=overview["result_name"],
            character_id=overview["character_id"],
            image_url=overview["image_url"],
            tags=tuple(overview["tags"]),
        ),
        unboxing_kit=UnboxingKitData(
            axis_scores=AxisScoresData(
                attachment=scores["attachment"],
                expression=scores["expression"],
                routine=scores["routine"],
                egen=scores["egen"],
            ),
            title=unboxing["title"],
            description=unboxing["description"],
            packaging=_unboxing_item(unboxing["packaging"]),
            opening_tool=_unboxing_item(unboxing["opening_tool"]),
        ),
        features=tuple(
            FeatureData(title=feature["title"], description=feature["description"])
            for feature in snapshot["features"]
        ),
        character_story=CharacterStoryData(
            title=story["title"],
            description=story["description"],
        ),
        can_do=tuple(snapshot["can_do"]),
        warnings=tuple(snapshot["warnings"]),
        charging=ChargingData(
            score=charging["score"],
            description=charging["description"],
            activities=tuple(
                ChargingActivityData(type=activity["type"], label=activity["label"])
                for activity in charging["activities"]
            ),
        ),
    )


class SqlAlchemyResultRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(
        self,
        result: SubmissionResultData,
        *,
        assessment_version: str,
        content_version: str,
    ) -> None:
        self._session.add(
            AssessmentResultRecord(
                result_code=result.result_code,
                assessment_version=assessment_version,
                content_version=content_version,
                result_snapshot=asdict(result),
            )
        )
        try:
            await self._session.commit()
        except IntegrityError as error:
            await self._session.rollback()
            raise ResultCodeConflictError from error

    async def get(self, result_code: str) -> SubmissionResultData | None:
        record = await self._session.scalar(
            select(AssessmentResultRecord).where(AssessmentResultRecord.result_code == result_code)
        )
        if record is None:
            return None
        return _result_from_snapshot(record.result_snapshot)
