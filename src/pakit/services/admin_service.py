from collections import Counter
from collections.abc import Sequence
from datetime import UTC, date, datetime, time, timedelta
from statistics import median
from typing import Any
from zoneinfo import ZoneInfo

from pakit.services.admin_repository import StoredResult, StoredUsageEvent

SEOUL = ZoneInfo("Asia/Seoul")
AXIS_KEYS = ("attachment", "expression", "routine", "egen")
BANDS = ((0, 24, "0~24"), (25, 49, "25~49"), (50, 74, "50~74"), (75, 100, "75~100"))


def _aware(value: datetime) -> datetime:
    return value.replace(tzinfo=UTC) if value.tzinfo is None else value


def _nickname(result: StoredResult) -> str | None:
    participant = result.snapshot.get("participant")
    if not isinstance(participant, dict):
        return None
    nickname = participant.get("nickname")
    return nickname if isinstance(nickname, str) else None


def mask_nickname(nickname: str | None) -> str:
    if not nickname:
        return "-"
    if len(nickname) == 1:
        return f"{nickname}*"
    if len(nickname) == 2:
        return f"{nickname[0]}*"
    return f"{nickname[0]}{'*' * (len(nickname) - 2)}{nickname[-1]}"


def _overview(result: StoredResult) -> dict[str, Any]:
    value = result.snapshot.get("overview")
    return value if isinstance(value, dict) else {}


def _scores(result: StoredResult) -> dict[str, int]:
    kit = result.snapshot.get("unboxing_kit")
    if not isinstance(kit, dict):
        return {}
    value = kit.get("axis_scores")
    if not isinstance(value, dict):
        return {}
    return {key: score for key, score in value.items() if isinstance(score, int)}


def _mbti(result: StoredResult) -> str | None:
    profile = result.snapshot.get("compatibility_profile")
    if not isinstance(profile, dict):
        return None
    mbti = profile.get("mbti")
    return mbti if isinstance(mbti, str) else None


def _in_range(value: datetime, start: datetime | None, end: datetime | None) -> bool:
    aware = _aware(value)
    return (start is None or aware >= start) and (end is None or aware < end)


def seoul_date_range(
    date_from: date | None,
    date_to: date | None,
) -> tuple[datetime | None, datetime | None]:
    start = datetime.combine(date_from, time.min, SEOUL).astimezone(UTC) if date_from else None
    end = (
        datetime.combine(date_to + timedelta(days=1), time.min, SEOUL).astimezone(UTC)
        if date_to
        else None
    )
    return start, end


def filter_results(
    results: list[StoredResult],
    *,
    date_from: date | None = None,
    date_to: date | None = None,
    result_code: str | None = None,
    nickname: str | None = None,
    mbti: str | None = None,
    character_id: str | None = None,
    tag: str | None = None,
    assessment_version: str | None = None,
    content_version: str | None = None,
) -> list[StoredResult]:
    start, end = seoul_date_range(date_from, date_to)
    filtered = []
    for result in results:
        overview = _overview(result)
        tags = overview.get("tags", [])
        if not _in_range(result.created_at, start, end):
            continue
        if result_code and result.result_code != result_code:
            continue
        if nickname and nickname.casefold() not in (_nickname(result) or "").casefold():
            continue
        if mbti and _mbti(result) != mbti:
            continue
        if character_id and overview.get("character_id") != character_id:
            continue
        if tag and (
            (not isinstance(tags, list) and not isinstance(tags, tuple)) or tag not in tags
        ):
            continue
        if assessment_version and result.assessment_version != assessment_version:
            continue
        if content_version and result.content_version != content_version:
            continue
        filtered.append(result)
    return filtered


def filter_usage_events(
    events: list[StoredUsageEvent],
    *,
    date_from: date | None = None,
    date_to: date | None = None,
) -> list[StoredUsageEvent]:
    start, end = seoul_date_range(date_from, date_to)
    return [event for event in events if _in_range(event.occurred_at, start, end)]


def result_summary(
    result: StoredResult,
    *,
    view_count: int,
    compatibility_count: int,
) -> dict[str, Any]:
    overview = _overview(result)
    tags = overview.get("tags")
    return {
        "created_at": _aware(result.created_at),
        "result_code": result.result_code,
        "nickname": mask_nickname(_nickname(result)),
        "mbti": _mbti(result),
        "result_name": overview.get("result_name"),
        "character_id": overview.get("character_id"),
        "tags": list(tags) if isinstance(tags, (list, tuple)) else [],
        "axis_scores": _scores(result),
        "assessment_version": result.assessment_version,
        "content_version": result.content_version,
        "view_count": view_count,
        "compatibility_count": compatibility_count,
    }


def usage_counts(events: list[StoredUsageEvent]) -> tuple[Counter[str], Counter[str]]:
    views: Counter[str] = Counter()
    compatibility: Counter[str] = Counter()
    for event in events:
        if event.event_name == "result_viewed":
            views[event.result_code] += 1
        elif event.event_name == "compatibility_completed":
            compatibility[event.result_code] += 1
    return views, compatibility


def distribution(
    values: Sequence[str | None],
    limit: int | None = None,
    *,
    denominator: int | None = None,
) -> list[dict[str, Any]]:
    counter = Counter(value or "알 수 없음" for value in values)
    total = denominator if denominator is not None else sum(counter.values())
    items = counter.most_common(limit)
    return [
        {"key": key, "count": count, "ratio": round(count / total * 100, 1) if total else 0.0}
        for key, count in items
    ]


def build_result_analytics(results: list[StoredResult]) -> dict[str, Any]:
    overviews = [_overview(result) for result in results]
    tag_values = [
        str(tag)
        for overview in overviews
        for tag in overview.get("tags", [])
        if isinstance(tag, str)
    ]
    axes: dict[str, Any] = {}
    for key in AXIS_KEYS:
        values = [scores[key] for result in results if key in (scores := _scores(result))]
        band_counts = {
            label: sum(low <= value <= high for value in values) for low, high, label in BANDS
        }
        axes[key] = {
            "average": round(sum(values) / len(values), 1) if values else None,
            "median": median(values) if values else None,
            "bands": band_counts,
        }
    return {
        "total_results": len(results),
        "mbti": distribution([_mbti(result) for result in results]),
        "characters": distribution(
            [
                str(overview.get("character_id")) if overview.get("character_id") else None
                for overview in overviews
            ]
        ),
        "result_names": distribution(
            [
                str(overview.get("result_name")) if overview.get("result_name") else None
                for overview in overviews
            ]
        ),
        "tags": distribution(tag_values, denominator=len(results)),
        "assessment_versions": distribution([result.assessment_version for result in results]),
        "content_versions": distribution([result.content_version for result in results]),
        "axes": axes,
    }


def build_compatibility_analytics(
    results: list[StoredResult],
    events: list[StoredUsageEvent],
    *,
    tracking_started_at: datetime | None,
) -> dict[str, Any]:
    result_by_code = {result.result_code: result for result in results}
    compatibility_events = [
        event
        for event in events
        if event.event_name == "compatibility_completed" and event.result_code in result_by_code
    ]
    view_events = [
        event
        for event in events
        if event.event_name == "result_viewed" and event.result_code in result_by_code
    ]
    tracking_start = _aware(tracking_started_at) if tracking_started_at else None
    eligible_codes = {
        result.result_code
        for result in results
        if tracking_start is not None and _aware(result.created_at) >= tracking_start
    }
    experienced_codes = {
        event.result_code for event in compatibility_events if event.result_code in eligible_codes
    }
    viewed_at: dict[str, datetime] = {}
    for event in view_events:
        occurred_at = _aware(event.occurred_at)
        current = viewed_at.get(event.result_code)
        if current is None or occurred_at < current:
            viewed_at[event.result_code] = occurred_at
    converted_codes = {
        event.result_code
        for event in compatibility_events
        if event.result_code in viewed_at
        and _aware(event.occurred_at) > viewed_at[event.result_code]
    }
    viewed_codes = set(viewed_at)
    scores = [
        event.compatibility_score
        for event in compatibility_events
        if event.compatibility_score is not None
    ]
    score_bands = {
        "0~24": sum(0 <= score <= 24 for score in scores),
        "25~49": sum(25 <= score <= 49 for score in scores),
        "50~74": sum(50 <= score <= 74 for score in scores),
        "75~100": sum(75 <= score <= 100 for score in scores),
    }
    combinations: list[str] = []
    for event in compatibility_events:
        mine = result_by_code.get(event.result_code)
        friend = result_by_code.get(event.related_result_code or "")
        mine_mbti = _mbti(mine) if mine else None
        friend_mbti = _mbti(friend) if friend else None
        if mine_mbti and friend_mbti:
            combinations.append(" x ".join(sorted((mine_mbti, friend_mbti))))
    return {
        "tracking_started_at": tracking_start,
        "completed_count": len(compatibility_events),
        "experienced_result_count": len(experienced_codes),
        "experience_ratio": (
            round(len(experienced_codes) / len(eligible_codes) * 100, 1) if eligible_codes else None
        ),
        "viewed_result_count": len(viewed_codes),
        "result_view_count": len(view_events),
        "viewed_result_ratio": (
            round(len(viewed_codes & eligible_codes) / len(eligible_codes) * 100, 1)
            if eligible_codes
            else None
        ),
        "view_to_compatibility_ratio": (
            round(len(converted_codes) / len(viewed_codes) * 100, 1) if viewed_codes else None
        ),
        "average_per_experienced_result": (
            round(len(compatibility_events) / len({e.result_code for e in compatibility_events}), 1)
            if compatibility_events
            else None
        ),
        "average_score": round(sum(scores) / len(scores), 1) if scores else None,
        "score_bands": score_bands,
        "mbti_combinations": distribution(combinations),
        "versions": distribution([event.compatibility_version for event in compatibility_events]),
    }


def build_dashboard(
    results: list[StoredResult],
    events: list[StoredUsageEvent],
    *,
    tracking_started_at: datetime | None,
    now: datetime | None = None,
) -> dict[str, Any]:
    current = _aware(now or datetime.now(UTC))
    today = current.astimezone(SEOUL).date()

    def since(days: int) -> datetime:
        start_date = today - timedelta(days=days - 1)
        return datetime.combine(start_date, time.min, SEOUL).astimezone(UTC)

    compatibility_events = [
        event for event in events if event.event_name == "compatibility_completed"
    ]
    result_analytics = build_result_analytics(results)
    compatibility_analytics = build_compatibility_analytics(
        results, events, tracking_started_at=tracking_started_at
    )
    trend: list[dict[str, Any]] = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        trend.append(
            {
                "date": day,
                "results": sum(
                    _aware(result.created_at).astimezone(SEOUL).date() == day for result in results
                ),
                "views": sum(
                    event.event_name == "result_viewed"
                    and _aware(event.occurred_at).astimezone(SEOUL).date() == day
                    for event in events
                ),
                "compatibility": sum(
                    event.event_name == "compatibility_completed"
                    and _aware(event.occurred_at).astimezone(SEOUL).date() == day
                    for event in events
                ),
            }
        )
    combinations = compatibility_analytics["mbti_combinations"][:5]
    return {
        "counts": {
            "today_results": sum(_aware(r.created_at) >= since(1) for r in results),
            "seven_day_results": sum(_aware(r.created_at) >= since(7) for r in results),
            "thirty_day_results": sum(_aware(r.created_at) >= since(30) for r in results),
            "total_results": len(results),
            "today_compatibility": sum(
                _aware(event.occurred_at) >= since(1) for event in compatibility_events
            ),
            "seven_day_compatibility": sum(
                _aware(event.occurred_at) >= since(7) for event in compatibility_events
            ),
        },
        "experience_ratio": compatibility_analytics["experience_ratio"],
        "view_to_compatibility_ratio": compatibility_analytics["view_to_compatibility_ratio"],
        "trend": trend,
        "top_mbti": result_analytics["mbti"][:5],
        "top_characters": result_analytics["characters"][:5],
        "top_tags": result_analytics["tags"][:5],
        "top_compatibility_pairs": combinations,
    }
