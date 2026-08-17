import pytest

from pakit.services.charging_service import (
    BASE_CHARGING_ACTIVITY,
    CHARGING_COMBINATION_COPY,
    EMERGENCY_CHARGING_ACTIVITY,
    build_charging,
)


def test_defines_every_holiday_and_cancellation_combination() -> None:
    expected = {
        (holiday, cancellation)
        for holiday in BASE_CHARGING_ACTIVITY
        for cancellation in EMERGENCY_CHARGING_ACTIVITY
    }

    assert set(CHARGING_COMBINATION_COPY) == expected
    assert len(expected) == 24


@pytest.mark.parametrize(
    ("holiday", "cancellation"),
    [
        (holiday, cancellation)
        for holiday in BASE_CHARGING_ACTIVITY
        for cancellation in EMERGENCY_CHARGING_ACTIVITY
    ],
)
def test_builds_three_personalized_charging_activities(
    holiday: str,
    cancellation: str,
) -> None:
    result = build_charging(holiday, cancellation)

    assert result.score == 90
    assert result.description
    assert len(result.activities) == 3
    assert result.activities[0].type == holiday
    assert result.activities[1].type == cancellation
    assert result.activities[2].type == f"{holiday}_{cancellation}"
    assert all(activity.label for activity in result.activities)


def test_combines_rest_and_driving_into_a_specific_recovery_pattern() -> None:
    result = build_charging("stay_in_bed", "go_for_drive")

    assert result.description == (
        "평소에는 아무것도 하지 않는 시간이 있어야 회복돼요. 하지만 답답함까지 쌓인 날에는 "
        "익숙한 동네를 벗어날 때 훨씬 빨리 살아나요."
    )
    assert result.activities[2].label == ("충분히 늘어진 뒤 좋아하는 음악을 틀고 야간 드라이브하기")
