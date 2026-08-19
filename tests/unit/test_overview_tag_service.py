import pytest

from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_submission import AxisScoresData
from pakit.services.overview_tag_service import (
    AXIS_OVERVIEW_TAG,
    MBTI_OVERVIEW_TAG,
    build_overview_tags,
)


def test_defines_one_overview_tag_for_every_mbti() -> None:
    assert set(MBTI_OVERVIEW_TAG) == set(MbtiType)
    assert len(set(MBTI_OVERVIEW_TAG.values())) == len(MbtiType)


def test_defines_copy_for_both_poles_of_every_axis() -> None:
    assert AXIS_OVERVIEW_TAG == {
        ("attachment", "low"): "혼자서도 잘 놀아요",
        ("attachment", "high"): "같이 있어야 든든해요",
        ("expression", "low"): "속마음은 천천히",
        ("expression", "high"): "마음은 바로 표현",
        ("routine", "low"): "도파민 MAX",
        ("routine", "high"): "익숙한 게 최고",
        ("egen", "low"): "행동으로 말해요",
        ("egen", "high"): "감정 레이더 ON",
    }


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        (
            AxisScoresData(attachment=20, expression=65, routine=0, egen=75),
            ("장난꾸러기", "도파민 MAX", "혼자서도 잘 놀아요"),
        ),
        (
            AxisScoresData(attachment=100, expression=0, routine=67, egen=33),
            ("장난꾸러기", "같이 있어야 든든해요", "속마음은 천천히"),
        ),
    ],
)
def test_builds_mbti_tag_and_two_strongest_axis_tags(
    scores: AxisScoresData,
    expected: tuple[str, str, str],
) -> None:
    assert build_overview_tags(MbtiType.ENTP, scores) == expected


def test_uses_stable_axis_priority_when_strengths_are_tied() -> None:
    scores = AxisScoresData(attachment=0, expression=100, routine=0, egen=100)

    assert build_overview_tags(MbtiType.INTJ, scores) == (
        "큰그림 설계자",
        "혼자서도 잘 놀아요",
        "마음은 바로 표현",
    )
