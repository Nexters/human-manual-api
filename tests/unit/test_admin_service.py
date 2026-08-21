from datetime import UTC, datetime, timedelta

from pakit.services.admin_repository import StoredResult, StoredUsageEvent
from pakit.services.admin_service import (
    build_compatibility_analytics,
    build_dashboard,
    build_result_analytics,
    filter_results,
    mask_nickname,
)


def _result(code: str, mbti: str, created_at: datetime, nickname: str = "해서니") -> StoredResult:
    return StoredResult(
        result_code=code,
        assessment_version="questions-v1",
        content_version="content-v1",
        created_at=created_at,
        snapshot={
            "participant": {"nickname": nickname},
            "overview": {
                "result_name": "팽이 지은",
                "character_id": "spinning_top",
                "tags": ["장난꾸러기", "도파민 MAX", "혼자서도 잘 놀아요"],
            },
            "unboxing_kit": {
                "axis_scores": {
                    "attachment": 25,
                    "expression": 75,
                    "routine": 10,
                    "egen": 50,
                }
            },
            "compatibility_profile": {"mbti": mbti},
        },
    )


def _event(
    name: str,
    code: str,
    occurred_at: datetime,
    *,
    friend: str | None = None,
    score: int | None = None,
) -> StoredUsageEvent:
    return StoredUsageEvent(
        event_name=name,  # type: ignore[arg-type]
        result_code=code,
        related_result_code=friend,
        compatibility_score=score,
        compatibility_version="rules-v1" if score is not None else None,
        occurred_at=occurred_at,
    )


def test_calculates_result_code_based_view_to_compatibility_conversion() -> None:
    started_at = datetime(2026, 8, 20, tzinfo=UTC)
    results = [
        _result("RESULT01", "ENTP", started_at),
        _result("RESULT02", "INTJ", started_at + timedelta(minutes=1)),
    ]
    events = [
        _event("result_viewed", "RESULT01", started_at + timedelta(hours=1)),
        _event(
            "compatibility_completed",
            "RESULT01",
            started_at + timedelta(hours=2),
            friend="RESULT02",
            score=80,
        ),
        _event(
            "compatibility_completed",
            "RESULT01",
            started_at + timedelta(hours=3),
            friend="RESULT02",
            score=90,
        ),
        _event(
            "compatibility_completed",
            "RESULT02",
            started_at + timedelta(hours=1),
            friend="RESULT01",
            score=40,
        ),
        _event("result_viewed", "RESULT02", started_at + timedelta(hours=2)),
    ]

    analytics = build_compatibility_analytics(results, events, tracking_started_at=started_at)

    assert analytics["completed_count"] == 3
    assert analytics["experienced_result_count"] == 2
    assert analytics["experience_ratio"] == 100.0
    assert analytics["viewed_result_count"] == 2
    assert analytics["result_view_count"] == 2
    assert analytics["viewed_result_ratio"] == 100.0
    assert analytics["view_to_compatibility_ratio"] == 50.0
    assert analytics["average_per_experienced_result"] == 1.5
    assert analytics["average_score"] == 70.0
    assert analytics["score_bands"] == {
        "0~24": 0,
        "25~49": 1,
        "50~74": 0,
        "75~100": 2,
    }
    assert analytics["mbti_combinations"][0]["key"] == "ENTP x INTJ"


def test_does_not_publish_experience_ratio_without_tracking_start() -> None:
    now = datetime(2026, 8, 20, tzinfo=UTC)
    analytics = build_compatibility_analytics(
        [_result("RESULT01", "ENTP", now)],
        [_event("compatibility_completed", "RESULT01", now, score=70)],
        tracking_started_at=None,
    )

    assert analytics["experience_ratio"] is None
    assert analytics["tracking_started_at"] is None


def test_dashboard_uses_seoul_calendar_day_boundary() -> None:
    now = datetime(2026, 8, 20, 16, 0, tzinfo=UTC)  # 2026-08-21 01:00 KST
    results = [
        _result("RESULT01", "ENTP", datetime(2026, 8, 20, 14, 59, tzinfo=UTC)),
        _result("RESULT02", "INTJ", datetime(2026, 8, 20, 15, 1, tzinfo=UTC)),
    ]

    dashboard = build_dashboard(results, [], tracking_started_at=None, now=now)

    assert dashboard["counts"]["today_results"] == 1
    assert dashboard["trend"][-1]["date"].isoformat() == "2026-08-21"
    assert dashboard["trend"][-1]["results"] == 1


def test_filters_results_and_masks_nicknames() -> None:
    now = datetime(2026, 8, 20, tzinfo=UTC)
    results = [
        _result("RESULT01", "ENTP", now, "해서니"),
        _result("RESULT02", "INTJ", now, "선우"),
    ]

    assert [result.result_code for result in filter_results(results, nickname="해서")] == [
        "RESULT01"
    ]
    assert [result.result_code for result in filter_results(results, mbti="INTJ")] == ["RESULT02"]
    assert mask_nickname("해서니") == "해*니"
    assert mask_nickname("선우") == "선*"
    assert mask_nickname("이") == "이*"


def test_keyword_ratio_is_the_share_of_results_with_that_keyword() -> None:
    now = datetime(2026, 8, 20, tzinfo=UTC)

    analytics = build_result_analytics(
        [_result("RESULT01", "ENTP", now), _result("RESULT02", "INTJ", now)]
    )

    assert analytics["tags"][0] == {
        "key": "장난꾸러기",
        "count": 2,
        "ratio": 100.0,
    }
