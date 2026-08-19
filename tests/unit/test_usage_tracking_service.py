import asyncio
from typing import Any

from pakit.services.usage_tracking_service import (
    record_compatibility_completed,
    record_result_viewed,
)


class FailingUsageRepository:
    async def record(self, **event: Any) -> None:
        raise RuntimeError("storage unavailable")


def test_usage_storage_failure_does_not_break_public_request_flow() -> None:
    async def run() -> None:
        repository = FailingUsageRepository()

        await record_result_viewed(repository, result_code="RESULT01")
        await record_compatibility_completed(
            repository,
            mine_result_code="RESULT01",
            friend_result_code="RESULT02",
            score=82,
            version="rules-v1",
        )

    asyncio.run(run())
