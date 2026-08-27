from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol

UsageEventName = Literal["result_viewed", "compatibility_completed"]


@dataclass(frozen=True)
class StoredCompatibilityEvent:
    """랭킹 생성에 필요한 궁합 완료 기록입니다."""

    mine_result_code: str
    friend_result_code: str
    score: int
    version: str
    occurred_at: datetime


class UsageEventRepository(Protocol):
    async def record(
        self,
        *,
        event_name: UsageEventName,
        result_code: str,
        related_result_code: str | None = None,
        compatibility_score: int | None = None,
        compatibility_version: str | None = None,
        occurred_at: datetime | None = None,
    ) -> None: ...


class CompatibilityEventReader(Protocol):
    async def list_compatibility_events(
        self,
        result_code: str,
    ) -> list[StoredCompatibilityEvent]: ...
