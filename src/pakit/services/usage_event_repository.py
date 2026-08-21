from datetime import datetime
from typing import Literal, Protocol

UsageEventName = Literal["result_viewed", "compatibility_completed"]


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
