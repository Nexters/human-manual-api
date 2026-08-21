from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol

from pakit.services.usage_event_repository import UsageEventName


@dataclass(frozen=True)
class StoredResult:
    result_code: str
    assessment_version: str
    content_version: str
    snapshot: dict[str, Any]
    created_at: datetime


@dataclass(frozen=True)
class StoredUsageEvent:
    event_name: UsageEventName
    result_code: str
    related_result_code: str | None
    compatibility_score: int | None
    compatibility_version: str | None
    occurred_at: datetime


class AdminRepository(Protocol):
    async def list_results(self) -> list[StoredResult]: ...

    async def get_result(self, result_code: str) -> StoredResult | None: ...

    async def list_usage_events(self) -> list[StoredUsageEvent]: ...
