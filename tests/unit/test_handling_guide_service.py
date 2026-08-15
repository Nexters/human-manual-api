import pytest

from pakit.domain.assessment import MbtiType
from pakit.services.handling_guide_service import build_handling_guide


def test_builds_four_handling_instructions_in_fixed_order() -> None:
    result = build_handling_guide(
        support_preference="solve_together",
        mbti=MbtiType.ENTP,
        attachment_score=50,
        conflict_style="resolve_immediately",
        affection_style="express_with_actions",
    )

    assert result == (
        "막힌 이유부터 함께 정리해주세요",
        "별일 없어도 자주 안부를 묻고 곁에 있어주세요",
        "서운한 일은 피하지 말고 바로 이야기해주세요",
        "말없이 챙기는 행동을 애정으로 알아봐주세요",
    )


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (49, "연락이 뜸해도 각자의 시간을 믿어주세요"),
        (50, "별일 없어도 자주 안부를 묻고 곁에 있어주세요"),
    ],
)
def test_uses_50_point_attachment_boundary(score: int, expected: str) -> None:
    result = build_handling_guide(
        support_preference="listen_to_me",
        mbti=MbtiType.ENTP,
        attachment_score=score,
        conflict_style="hint_and_wait",
        affection_style="express_with_words",
    )

    assert result[1] == expected


@pytest.mark.parametrize(
    ("mbti", "expected"),
    [
        (MbtiType.ENTP, "결론을 재촉하지 말고 생각의 흐름을 들어주세요"),
        (MbtiType.ESTP, "무슨 일이 있었는지 처음부터 차근차근 들어주세요"),
        (MbtiType.ENFP, "해결책보다 지금 느끼는 마음부터 들어주세요"),
        (MbtiType.ESFP, "편하게 말할 수 있도록 곁에서 들어주세요"),
    ],
)
def test_refines_support_preference_with_middle_mbti_group(mbti: MbtiType, expected: str) -> None:
    result = build_handling_guide(
        support_preference="listen_to_me",
        mbti=mbti,
        attachment_score=0,
        conflict_style="hint_and_wait",
        affection_style="express_with_words",
    )

    assert result[0] == expected
