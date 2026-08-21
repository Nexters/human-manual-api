import logging

from pakit.services.usage_event_repository import UsageEventRepository

logger = logging.getLogger(__name__)


async def record_result_viewed(
    repository: UsageEventRepository,
    *,
    result_code: str,
) -> None:
    try:
        await repository.record(event_name="result_viewed", result_code=result_code)
    except Exception:
        logger.exception("Failed to record result_viewed usage event")


async def record_compatibility_completed(
    repository: UsageEventRepository,
    *,
    mine_result_code: str,
    friend_result_code: str,
    score: int,
    version: str,
) -> None:
    try:
        await repository.record(
            event_name="compatibility_completed",
            result_code=mine_result_code,
            related_result_code=friend_result_code,
            compatibility_score=score,
            compatibility_version=version,
        )
    except Exception:
        logger.exception("Failed to record compatibility_completed usage event")
