from datetime import date
from math import ceil
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Path, Query

from pakit.api.admin_auth import require_admin
from pakit.api.dependencies import get_admin_repository
from pakit.api.schemas.admin import (
    AdminDashboardOutput,
    AdminResultDetailOutput,
    AdminResultListOutput,
    CompatibilityAnalyticsOutput,
    ResultAnalyticsOutput,
)
from pakit.core.config import get_settings
from pakit.services.admin_repository import AdminRepository
from pakit.services.admin_service import (
    build_compatibility_analytics,
    build_dashboard,
    build_result_analytics,
    filter_results,
    filter_usage_events,
    result_summary,
    usage_counts,
)

router = APIRouter(
    prefix="/admin",
    tags=["Admin"],
    dependencies=[Depends(require_admin)],
)


@router.get("/dashboard", response_model=AdminDashboardOutput)
async def get_admin_dashboard(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
) -> AdminDashboardOutput:
    return AdminDashboardOutput.model_validate(
        build_dashboard(
            await repository.list_results(),
            await repository.list_usage_events(),
            tracking_started_at=get_settings().usage_tracking_started_at,
        )
    )


@router.get("/results", response_model=AdminResultListOutput)
async def get_admin_results(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    date_from: date | None = None,
    date_to: date | None = None,
    result_code: str | None = None,
    nickname: str | None = None,
    mbti: str | None = None,
    character_id: str | None = None,
    tag: str | None = None,
    assessment_version: str | None = None,
    content_version: str | None = None,
    has_compatibility: bool | None = None,
    sort: Literal["newest", "oldest"] = "newest",
) -> AdminResultListOutput:
    events = await repository.list_usage_events()
    views, compatibility = usage_counts(events)
    results = filter_results(
        await repository.list_results(),
        date_from=date_from,
        date_to=date_to,
        result_code=result_code,
        nickname=nickname,
        mbti=mbti,
        character_id=character_id,
        tag=tag,
        assessment_version=assessment_version,
        content_version=content_version,
    )
    if has_compatibility is not None:
        results = [
            result
            for result in results
            if (compatibility[result.result_code] > 0) is has_compatibility
        ]
    results.sort(key=lambda result: result.created_at, reverse=sort == "newest")
    total = len(results)
    start = (page - 1) * page_size
    items = [
        result_summary(
            result,
            view_count=views[result.result_code],
            compatibility_count=compatibility[result.result_code],
        )
        for result in results[start : start + page_size]
    ]
    return AdminResultListOutput(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        pages=ceil(total / page_size) if total else 0,
    )


@router.get("/results/{result_code}", response_model=AdminResultDetailOutput)
async def get_admin_result_detail(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    result_code: Annotated[str, Path(min_length=8, max_length=8)],
) -> AdminResultDetailOutput:
    result = await repository.get_result(result_code)
    if result is None:
        raise HTTPException(status_code=404, detail="결과를 찾을 수 없습니다.")
    events = await repository.list_usage_events()
    views = [
        event
        for event in events
        if event.event_name == "result_viewed" and event.result_code == result_code
    ]
    compatibility = [
        event
        for event in events
        if event.event_name == "compatibility_completed" and event.result_code == result_code
    ]
    participant = result.snapshot.get("participant")
    nickname = participant.get("nickname") if isinstance(participant, dict) else None
    return AdminResultDetailOutput(
        result_code=result.result_code,
        created_at=result.created_at,
        nickname=nickname if isinstance(nickname, str) else None,
        assessment_version=result.assessment_version,
        content_version=result.content_version,
        usage={
            "view_count": len(views),
            "last_viewed_at": max((event.occurred_at for event in views), default=None),
            "compatibility_count": len(compatibility),
        },
        snapshot=result.snapshot,
    )


@router.get("/analytics/results", response_model=ResultAnalyticsOutput)
async def get_result_analytics(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    date_from: date | None = None,
    date_to: date | None = None,
) -> ResultAnalyticsOutput:
    results = filter_results(await repository.list_results(), date_from=date_from, date_to=date_to)
    return ResultAnalyticsOutput.model_validate(build_result_analytics(results))


@router.get("/analytics/compatibility", response_model=CompatibilityAnalyticsOutput)
async def get_compatibility_analytics(
    repository: Annotated[AdminRepository, Depends(get_admin_repository)],
    date_from: date | None = None,
    date_to: date | None = None,
) -> CompatibilityAnalyticsOutput:
    results = filter_results(await repository.list_results(), date_from=date_from, date_to=date_to)
    events = filter_usage_events(
        await repository.list_usage_events(), date_from=date_from, date_to=date_to
    )
    return CompatibilityAnalyticsOutput.model_validate(
        build_compatibility_analytics(
            results,
            events,
            tracking_started_at=get_settings().usage_tracking_started_at,
        )
    )
