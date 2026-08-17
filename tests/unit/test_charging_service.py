from itertools import product

from pakit.domain.assessment import MbtiType
from pakit.services.charging_service import (
    BASE_CHARGING_CLAUSE,
    BASE_CHARGING_KEYWORD,
    BASE_CHARGING_MECHANISM,
    EMERGENCY_CHARGING_KEYWORD,
    MBTI_CHARGING_KEYWORD,
    MOTIVATION_TRIGGER_DESCRIPTION,
    build_charging,
)


def test_builds_every_charging_combination_as_one_sentence_and_three_keywords() -> None:
    combinations = product(
        BASE_CHARGING_CLAUSE,
        EMERGENCY_CHARGING_KEYWORD,
        MOTIVATION_TRIGGER_DESCRIPTION,
        MbtiType,
    )

    for holiday, cancellation, motivation, mbti in combinations:
        result = build_charging(holiday, cancellation, motivation, mbti)

        assert result.score == 90
        assert len(result.description) <= 61
        assert len(result.activities) == 3
        assert [activity.type for activity in result.activities] == [
            holiday,
            cancellation,
            mbti.value,
        ]
        assert all(len(activity.label) <= 10 for activity in result.activities)


def test_explains_resting_baseline_and_curiosity_trigger_together() -> None:
    result = build_charging(
        "stay_in_bed",
        "go_to_bed",
        "curiosity",
        MbtiType.ENTP,
    )

    assert result.description == (
        "혼자 아무것도 안 하는 시간이 있어야 채워지는 사람이에요. 새로운 구경거리가 생기면 "
        "다시 기운이 올라와요."
    )
    assert [activity.label for activity in result.activities] == [
        "침대와 한몸",
        "혼자만의 시간",
        "호기심 충족",
    ]


def test_defines_one_charging_keyword_for_every_mbti() -> None:
    assert MBTI_CHARGING_KEYWORD == {
        MbtiType.INTJ: "관심 분야 탐구",
        MbtiType.ENTJ: "자기계발",
        MbtiType.INTP: "외부와 단절",
        MbtiType.ENTP: "호기심 충족",
        MbtiType.INFJ: "조용한 공간",
        MbtiType.ENFJ: "깊은 대화",
        MbtiType.INFP: "감성 충전",
        MbtiType.ENFP: "수다 떨기",
        MbtiType.ISTJ: "루틴 지키기",
        MbtiType.ESTJ: "정리정돈",
        MbtiType.ISTP: "관심사 몰입",
        MbtiType.ESTP: "새로운 자극",
        MbtiType.ISFJ: "익숙한 공간",
        MbtiType.ESFJ: "수다 떨기",
        MbtiType.ISFP: "독립된 공간",
        MbtiType.ESFP: "수다 떨기",
    }


def test_defines_matching_base_description_and_keyword_inputs() -> None:
    assert set(BASE_CHARGING_CLAUSE) == set(BASE_CHARGING_KEYWORD)
    assert set(BASE_CHARGING_CLAUSE) == set(BASE_CHARGING_MECHANISM)


def test_uses_confirmed_charging_keyword_labels() -> None:
    assert BASE_CHARGING_KEYWORD["sleep_until_noon"] == "방해 없는 늦잠"
    assert BASE_CHARGING_KEYWORD["stay_in_bed"] == "침대와 한몸"
    assert EMERGENCY_CHARGING_KEYWORD["go_to_bed"] == "혼자만의 시간"


def test_defines_confirmed_q07_charging_mechanisms_and_descriptions() -> None:
    assert BASE_CHARGING_MECHANISM == {
        "sleep_until_noon": "수면 우선",
        "morning_run": "소모",
        "brunch_cafe": "감각 만족",
        "stay_in_bed": "차단",
        "watch_streaming": "몰입",
        "self_development": "청산",
    }
    assert BASE_CHARGING_CLAUSE == {
        "sleep_until_noon": "잠이 충분히 채워져야 나머지가 돌아가는 사람이에요",
        "morning_run": "에너지를 써야 오히려 채워지는 사람이에요",
        "brunch_cafe": "나한테 좋은 걸 제대로 챙겨줘야 채워지는 사람이에요",
        "stay_in_bed": "혼자 아무것도 안 하는 시간이 있어야 채워지는 사람이에요",
        "watch_streaming": "뭔가에 푹 빠져서 딴생각이 안 날 때 채워지는 사람이에요",
        "self_development": "마음의 짐을 덜어야 쉬어지는 사람이에요",
    }
