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
        (MbtiType.ENTP, "내 말의 표면만 보지 말고, 왜 이런 말을 하는지까지 이해해주세요"),
        (MbtiType.ESTP, "무슨 일이 있었는지 처음부터 차근차근 들어주세요"),
        (MbtiType.ENFP, "해결책보다 지금 느끼는 마음부터 들어주세요"),
        (MbtiType.ESFP, "말이 정리되지 않아도 중간에 판단하지 말고 끝까지 들어주세요"),
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


@pytest.mark.parametrize(
    ("support_preference", "mbti", "expected"),
    [
        (
            "take_me_out",
            MbtiType.ENFP,
            "마음이 답답해 보이면 내가 좋아할 만한 곳으로 함께 바람 쐬러 가주세요",
        ),
        (
            "take_me_out",
            MbtiType.ESFP,
            "무슨 일인지 캐묻기보다 좋아하는 걸 먹으러 슬쩍 불러내주세요",
        ),
        (
            "give_me_space",
            MbtiType.ESTP,
            "괜찮냐고 계속 묻기보다 혼자 정리할 시간을 주세요",
        ),
        (
            "make_me_laugh",
            MbtiType.ENTP,
            "복잡한 생각에서 잠깐 빠져나오게 엉뚱한 이야기를 던져주세요",
        ),
        (
            "make_me_laugh",
            MbtiType.ESTP,
            "길게 위로하기보다 바로 웃을 수 있는 사진이나 영상을 보내주세요",
        ),
        (
            "make_me_laugh",
            MbtiType.ENFP,
            "내가 좋아할 만한 농담으로 무거워진 마음을 살짝 풀어주세요",
        ),
    ],
)
def test_uses_confirmed_support_copy(
    support_preference: str,
    mbti: MbtiType,
    expected: str,
) -> None:
    result = build_handling_guide(
        support_preference=support_preference,
        mbti=mbti,
        attachment_score=0,
        conflict_style="hint_and_wait",
        affection_style="express_with_words",
    )

    assert result[0] == expected


def test_uses_confirmed_hint_and_wait_copy() -> None:
    result = build_handling_guide(
        support_preference="listen_to_me",
        mbti=MbtiType.ENTP,
        attachment_score=0,
        conflict_style="hint_and_wait",
        affection_style="express_with_words",
    )

    assert result[2] == "평소보다 말수가 줄면 모른 척 넘기지 말고 먼저 물어봐주세요"
