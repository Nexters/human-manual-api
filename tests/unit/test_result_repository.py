import asyncio
from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from pakit.core.models import AssessmentResultRecord, Base
from pakit.core.result_repository import SqlAlchemyResultRepository
from pakit.domain.assessment_submission import (
    AxisScoresData,
    CharacterStoryData,
    ChargingActivityData,
    ChargingData,
    CompatibilityProfileData,
    CompatibleFriendData,
    FeatureData,
    OverviewData,
    ResultParticipantData,
    SubmissionResultData,
    UnboxingItemData,
    UnboxingKitData,
)
from pakit.services.result_repository import ResultCodeConflictError


def _result() -> SubmissionResultData:
    return SubmissionResultData(
        result_code="aB3dE7_x",
        participant=ResultParticipantData(nickname="송송"),
        overview=OverviewData(
            rarity="상위 4%",
            adjective="테스트용",
            noun="팽이",
            result_name="테스트용 팽이",
            character_id="spinning_top",
            image_url="/assets/characters/spinning_top.png",
            tags=("하나", "둘", "셋"),
        ),
        unboxing_kit=UnboxingKitData(
            axis_scores=AxisScoresData(10, 20, 30, 40),
            title="테스트 제목",
            description="테스트 설명",
            packaging=UnboxingItemData(
                "minimal_box",
                "미니멀 상자",
                "/assets/packaging_boxes/minimal_box.png",
                ("직진형", "거리조절형"),
                "이유",
            ),
            opening_tool=UnboxingItemData(
                "chainsaw",
                "전기톱",
                "/assets/opening_tools/chainsaw.png",
                ("탐험형", "테토형"),
                "이유",
            ),
        ),
        features=(FeatureData("특징", "설명"),) * 4,
        character_story=CharacterStoryData("이야기", "설명"),
        can_do=("하나", "둘", "셋", "넷"),
        warnings=("하나", "둘", "셋", "넷"),
        charging=ChargingData(
            score=90,
            description="충전 설명",
            activities=(ChargingActivityData("rest", "쉬기"),) * 3,
        ),
        compatible_friends=(
            CompatibleFriendData(
                "환상의 장난감",
                "비밀상자",
                "secret_box",
                "/assets/characters/secret_box.png",
                "설명",
            ),
        ),
        compatibility_profile=CompatibilityProfileData(
            version="compatibility-v1",
            mbti="ENTP",
            relationship_role="organizer",
            motivation="fun",
            support_preference="make_me_laugh",
            conflict_style="resolve_immediately",
            affection_style="express_with_actions",
        ),
    )


def test_persists_and_restores_an_immutable_result_snapshot() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        expected = _result()
        async with sessions() as session:
            repository = SqlAlchemyResultRepository(session)
            await repository.save(
                expected,
                assessment_version="assessment-v1",
                content_version="content-v1",
            )

        async with sessions() as session:
            repository = SqlAlchemyResultRepository(session)
            restored = await repository.get(expected.result_code)
            record = await session.scalar(select(AssessmentResultRecord))

        await engine.dispose()

        assert restored == expected
        assert record is not None
        assert record.assessment_version == "assessment-v1"
        assert record.content_version == "content-v1"
        assert record.result_snapshot["participant"] == {"nickname": "송송"}
        assert record.result_snapshot["compatibility_profile"]["mbti"] == "ENTP"

    asyncio.run(run())


def test_returns_none_for_an_unknown_result_code() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            result = await SqlAlchemyResultRepository(session).get("not-found")

        await engine.dispose()
        assert result is None

    asyncio.run(run())


def test_rejects_a_duplicate_result_code() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            repository = SqlAlchemyResultRepository(session)
            await repository.save(
                _result(), assessment_version="assessment-v1", content_version="content-v1"
            )
            with pytest.raises(ResultCodeConflictError):
                await repository.save(
                    _result(), assessment_version="assessment-v1", content_version="content-v1"
                )

        await engine.dispose()

    asyncio.run(run())


def test_restores_a_legacy_snapshot_without_a_participant() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        snapshot = asdict(_result())
        snapshot.pop("participant")
        snapshot.pop("compatibility_profile")
        snapshot.pop("compatible_friends")
        snapshot["unboxing_kit"]["packaging"].pop("image_url")
        snapshot["unboxing_kit"]["opening_tool"].pop("image_url")
        snapshot["result_code"] = "legacy01"
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            session.add(
                AssessmentResultRecord(
                    result_code="legacy01",
                    assessment_version="assessment-v1",
                    content_version="content-v1",
                    result_snapshot=snapshot,
                )
            )
            await session.commit()

        async with sessions() as session:
            restored = await SqlAlchemyResultRepository(session).get("legacy01")

        await engine.dispose()
        assert restored is not None
        assert restored.participant is None
        assert restored.compatibility_profile is None
        assert restored.compatible_friends == ()
        assert restored.unboxing_kit.packaging.image_url == (
            "/assets/packaging_boxes/minimal_box.png"
        )
        assert restored.unboxing_kit.opening_tool.image_url == (
            "/assets/opening_tools/chainsaw.png"
        )

    asyncio.run(run())
