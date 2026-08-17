from itertools import product

from pakit.services.charging_service import (
    BASE_CHARGING_CLAUSE,
    BASE_CHARGING_KEYWORD,
    EMERGENCY_CHARGING_KEYWORD,
    MOTIVATION_TRIGGER_DESCRIPTION,
    SUPPORT_CHARGING_KEYWORD,
    build_charging,
)


def test_builds_every_charging_combination_as_one_sentence_and_three_keywords() -> None:
    combinations = product(
        BASE_CHARGING_CLAUSE,
        EMERGENCY_CHARGING_KEYWORD,
        MOTIVATION_TRIGGER_DESCRIPTION,
        SUPPORT_CHARGING_KEYWORD,
    )

    for holiday, cancellation, motivation, support in combinations:
        result = build_charging(holiday, cancellation, motivation, support)

        assert result.score == 90
        assert len(result.description) <= 55
        assert len(result.activities) == 3
        assert [activity.type for activity in result.activities] == [holiday, cancellation, support]
        assert all(len(activity.label) <= 10 for activity in result.activities)


def test_explains_resting_baseline_and_curiosity_trigger_together() -> None:
    result = build_charging(
        "stay_in_bed",
        "go_to_bed",
        "curiosity",
        "take_me_out",
    )

    assert result.description == (
        "아무것도 하지 않고 이불 속에서 푹 쉬고, 새로운 구경거리가 생기면 다시 기운이 올라와요."
    )
    assert [activity.label for activity in result.activities] == [
        "이불 속 휴식",
        "바로 더 쉬기",
        "맛있는 거 먹기",
    ]


def test_defines_matching_base_description_and_keyword_inputs() -> None:
    assert set(BASE_CHARGING_CLAUSE) == set(BASE_CHARGING_KEYWORD)
