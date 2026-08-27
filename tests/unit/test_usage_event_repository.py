import asyncio
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from pakit.core.models import BackendUsageEventRecord, Base
from pakit.core.usage_event_repository import SqlAlchemyUsageEventRepository


def test_persists_backend_owned_usage_event_without_personal_data() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        occurred_at = datetime(2026, 8, 20, 9, 30, tzinfo=UTC)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            repository = SqlAlchemyUsageEventRepository(session)
            await repository.record(
                event_name="compatibility_completed",
                result_code="RESULT01",
                related_result_code="RESULT02",
                compatibility_score=87,
                compatibility_version="rules-v1",
                occurred_at=occurred_at,
            )

        async with sessions() as session:
            record = await session.scalar(select(BackendUsageEventRecord))

        await engine.dispose()
        assert record is not None
        assert record.event_name == "compatibility_completed"
        assert record.result_code == "RESULT01"
        assert record.related_result_code == "RESULT02"
        assert record.compatibility_score == 87
        assert record.compatibility_version == "rules-v1"
        assert not hasattr(record, "nickname")
        assert not hasattr(record, "ip_address")
        assert not hasattr(record, "user_agent")

    asyncio.run(run())


def test_lists_compatibility_events_for_either_side_of_a_pair() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)

        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            repository = SqlAlchemyUsageEventRepository(session)
            await repository.record(
                event_name="compatibility_completed",
                result_code="RESULT01",
                related_result_code="RESULT02",
                compatibility_score=100,
                compatibility_version="rules-v1",
                occurred_at=datetime(2026, 8, 20, 9, 30, tzinfo=UTC),
            )
            await repository.record(
                event_name="compatibility_completed",
                result_code="RESULT03",
                related_result_code="RESULT01",
                compatibility_score=0,
                compatibility_version="rules-v1",
                occurred_at=datetime(2026, 8, 20, 10, 30, tzinfo=UTC),
            )
            await repository.record(event_name="result_viewed", result_code="RESULT01")
            events = await repository.list_compatibility_events("RESULT01")

        await engine.dispose()
        assert [(event.mine_result_code, event.friend_result_code) for event in events] == [
            ("RESULT03", "RESULT01"),
            ("RESULT01", "RESULT02"),
        ]
        assert [event.score for event in events] == [0, 100]

    asyncio.run(run())
