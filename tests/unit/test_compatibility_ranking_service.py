import asyncio
from datetime import UTC, datetime, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from pakit.services.compatibility_ranking_service import (
    CompatibilityRankingNotFoundError,
    get_compatibility_ranking,
)
from pakit.services.usage_event_repository import StoredCompatibilityEvent


class FakeResultRepository:
    def __init__(self, results: dict[str, Any]) -> None:
        self.results = results

    async def get(self, result_code: str) -> Any | None:
        return self.results.get(result_code)

    async def save(self, result: Any, **versions: str) -> None:
        self.results[result.result_code] = result

    async def count(self) -> int:
        return len(self.results)


class FakeUsageRepository:
    def __init__(self, events: list[StoredCompatibilityEvent]) -> None:
        self.events = events

    async def list_compatibility_events(
        self,
        result_code: str,
    ) -> list[StoredCompatibilityEvent]:
        return self.events

    async def record(self, **event: Any) -> None:
        return None


def _result(nickname: str) -> SimpleNamespace:
    return SimpleNamespace(
        participant=SimpleNamespace(nickname=nickname),
        overview=SimpleNamespace(
            result_name=f"테스트용 {nickname}",
            noun="팽이",
            character_id="spinning_top",
            image_url="/assets/characters/spinning_top.png",
        ),
    )


def _event(
    mine: str,
    friend: str,
    score: int,
    occurred_at: datetime,
) -> StoredCompatibilityEvent:
    return StoredCompatibilityEvent(mine, friend, score, "rules-v1", occurred_at)


def test_deduplicates_by_latest_event_and_uses_competition_ranks() -> None:
    async def run() -> None:
        now = datetime(2026, 8, 27, tzinfo=UTC)
        results = {
            "MINE0001": _result("나"),
            "FRIEND01": _result("첫째"),
            "FRIEND02": _result("둘째"),
            "FRIEND03": _result("셋째"),
        }
        events = [
            _event("MINE0001", "MINE0001", 100, now + timedelta(minutes=4)),
            _event("MINE0001", "FRIEND01", 100, now),
            _event("MINE0001", "FRIEND01", 80, now + timedelta(minutes=3)),
            _event("FRIEND02", "MINE0001", 80, now + timedelta(minutes=2)),
            _event("MINE0001", "FRIEND03", 0, now + timedelta(minutes=1)),
        ]

        ranking = await get_compatibility_ranking(
            "MINE0001",
            FakeResultRepository(results),
            FakeUsageRepository(events),
        )

        assert ranking.total == 3
        assert [item.result_code for item in ranking.rankings] == [
            "FRIEND01",
            "FRIEND02",
            "FRIEND03",
        ]
        assert [item.score for item in ranking.rankings] == [80, 80, 0]
        assert [item.rank for item in ranking.rankings] == [1, 1, 3]

    asyncio.run(run())


def test_rejects_an_unknown_ranking_owner() -> None:
    async def run() -> None:
        with pytest.raises(CompatibilityRankingNotFoundError):
            await get_compatibility_ranking(
                "UNKNOWN1",
                FakeResultRepository({}),
                FakeUsageRepository([]),
            )

    asyncio.run(run())
