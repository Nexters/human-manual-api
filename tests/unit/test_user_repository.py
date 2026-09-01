import asyncio
from datetime import UTC, datetime, timedelta

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from pakit.core.models import (
    AssessmentResultRecord,
    BackendUsageEventRecord,
    Base,
    UserRecord,
)
from pakit.core.user_repository import SqlAlchemyUserRepository


def _snapshot(nickname: str, result_name: str, noun: str) -> dict[str, object]:
    return {
        "participant": {"nickname": nickname},
        "overview": {
            "result_name": result_name,
            "noun": noun,
            "character_id": "spinning_top",
            "image_url": "/assets/characters/spinning_top.png",
        },
    }


def test_upserts_user_syncs_results_and_lists_latest_compatibilities() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        now = datetime(2026, 9, 1, tzinfo=UTC)

        async with sessions() as session:
            other_user = UserRecord(kakao_user_id="other")
            session.add(other_user)
            await session.flush()
            session.add_all(
                [
                    AssessmentResultRecord(
                        result_code="MINE0001",
                        assessment_version="v1",
                        content_version="v1",
                        result_snapshot=_snapshot("나", "테스트용 팽이", "팽이"),
                        created_at=now,
                    ),
                    AssessmentResultRecord(
                        result_code="FRIEND01",
                        assessment_version="v1",
                        content_version="v1",
                        result_snapshot=_snapshot("친구", "테스트용 망원경", "망원경"),
                        created_at=now - timedelta(minutes=1),
                    ),
                    AssessmentResultRecord(
                        result_code="TAKEN001",
                        assessment_version="v1",
                        content_version="v1",
                        result_snapshot=_snapshot("다른 사람", "테스트용 상자", "상자"),
                        user_id=other_user.id,
                        created_at=now - timedelta(minutes=2),
                    ),
                ]
            )
            session.add_all(
                [
                    BackendUsageEventRecord(
                        event_name="compatibility_completed",
                        result_code="MINE0001",
                        related_result_code="FRIEND01",
                        compatibility_score=80,
                        compatibility_version="v1",
                        occurred_at=now - timedelta(hours=1),
                    ),
                    BackendUsageEventRecord(
                        event_name="compatibility_completed",
                        result_code="FRIEND01",
                        related_result_code="MINE0001",
                        compatibility_score=91,
                        compatibility_version="v2",
                        occurred_at=now,
                    ),
                ]
            )
            await session.commit()

            repository = SqlAlchemyUserRepository(session)
            user = await repository.upsert_kakao_user("kakao-123")
            same_user = await repository.upsert_kakao_user("kakao-123")
            sync = await repository.sync_results(
                user.id,
                ("MINE0001", "MINE0001", "TAKEN001", "UNKNOWN1"),
            )
            sync_again = await repository.sync_results(user.id, ("MINE0001",))
            results = await repository.list_results(user.id)
            compatibilities = await repository.list_compatibilities(user.id)

        await engine.dispose()

        assert same_user.id == user.id
        assert sync.synced == ("MINE0001",)
        assert sync.rejected == ("TAKEN001", "UNKNOWN1")
        assert sync_again.already_synced == ("MINE0001",)
        assert [result.result_code for result in results] == ["MINE0001"]
        assert len(compatibilities) == 1
        assert compatibilities[0].mine.result_code == "MINE0001"
        assert compatibilities[0].friend.result_code == "FRIEND01"
        assert compatibilities[0].score == 91

    asyncio.run(run())


def test_returns_empty_history_for_user_without_results() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            repository = SqlAlchemyUserRepository(session)
            user = await repository.upsert_kakao_user("kakao-empty")
            assert await repository.get_user(user.id) == user
            assert await repository.get_user(9999) is None
            assert await repository.list_compatibilities(user.id) == []
        await engine.dispose()

    asyncio.run(run())
