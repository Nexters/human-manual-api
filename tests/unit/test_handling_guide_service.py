import pytest

from pakit.domain.assessment import MbtiType
from pakit.services.handling_guide_service import build_handling_guide
from pakit.services.result_content import ATTRACTION_GUIDE_COPY


def test_builds_four_handling_instructions_in_fixed_order() -> None:
    result = build_handling_guide(
        support_preference="solve_together",
        mbti=MbtiType.ENTP,
        attachment_score=50,
        conflict_style="resolve_immediately",
        conflict_message_style="send_immediately",
    )

    assert result == (
        "막힌 이유부터 함께 정리해주세요",
        "별일 없어도 가끔 안부를 나눠주세요. 짧은 한마디만으로도 연결되어 있다고 느낍니다.",
        "서운한 일은 돌려 넘기지 말고, 그 자리에서 바로 확인하고 풀어주세요.",
        "애매하게 재지 않고 궁금한 건 바로 물어보면 좋아해요. "
        "내 장난에 밀리지 않고 먼저 훅 들어오면 설레요.",
    )


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (
            0,
            "혼자 있는 시간을 넉넉히 주세요. 답장이 하루 늦어도 삐진 게 아니라 그저 충전 중입니다.",
        ),
        (
            24,
            "혼자 있는 시간을 넉넉히 주세요. 답장이 하루 늦어도 삐진 게 아니라 그저 충전 중입니다.",
        ),
        (
            25,
            "연락은 편하게 주고받되 각자의 속도도 존중해주세요. "
            "늘 붙어 있지 않아도 관계는 그대로입니다.",
        ),
        (
            49,
            "연락은 편하게 주고받되 각자의 속도도 존중해주세요. "
            "늘 붙어 있지 않아도 관계는 그대로입니다.",
        ),
        (
            50,
            "별일 없어도 가끔 안부를 나눠주세요. 짧은 한마디만으로도 연결되어 있다고 느낍니다.",
        ),
        (
            74,
            "별일 없어도 가끔 안부를 나눠주세요. 짧은 한마디만으로도 연결되어 있다고 느낍니다.",
        ),
        (
            75,
            "오늘 뭐 했는지 사소한 일까지 나눠주세요. "
            "별것 아닌 이야기를 주고받을수록 가까워졌다고 느낍니다.",
        ),
        (
            100,
            "오늘 뭐 했는지 사소한 일까지 나눠주세요. "
            "별것 아닌 이야기를 주고받을수록 가까워졌다고 느낍니다.",
        ),
    ],
)
def test_uses_four_attachment_score_bands(score: int, expected: str) -> None:
    result = build_handling_guide(
        support_preference="listen_to_me",
        mbti=MbtiType.ENTP,
        attachment_score=score,
        conflict_style="hint_and_wait",
        conflict_message_style="rehearse_with_ai",
    )

    assert result[1] == expected


@pytest.mark.parametrize("score", [-1, 101])
def test_rejects_invalid_attachment_score(score: int) -> None:
    with pytest.raises(ValueError, match="attachment_score must be between 0 and 100"):
        build_handling_guide(
            support_preference="listen_to_me",
            mbti=MbtiType.ENTP,
            attachment_score=score,
            conflict_style="hint_and_wait",
            conflict_message_style="rehearse_with_ai",
        )


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
        conflict_message_style="rehearse_with_ai",
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
            "괜찮냐고 계속 묻기보다 평소처럼 지내주세요",
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
        conflict_message_style="rehearse_with_ai",
    )

    assert result[0] == expected


@pytest.mark.parametrize(
    ("conflict_style", "conflict_message_style", "expected"),
    [
        (
            "hint_and_wait",
            "rehearse_with_ai",
            "평소와 다른 티가 나면 먼저 물어봐주고, 마음을 정리해 말할 때까지 기다려주세요.",
        ),
        (
            "hint_and_wait",
            "send_immediately",
            "평소와 다른 티가 나면 먼저 물어봐주세요. 대화의 문만 열어주면 속마음은 바로 나와요.",
        ),
        (
            "resolve_immediately",
            "rehearse_with_ai",
            "서운한 일은 바로 짚어주되, 할 말을 정리할 시간을 잠깐 주세요.",
        ),
        (
            "resolve_immediately",
            "send_immediately",
            "서운한 일은 돌려 넘기지 말고, 그 자리에서 바로 확인하고 풀어주세요.",
        ),
    ],
)
def test_combines_conflict_response_and_message_preparation(
    conflict_style: str,
    conflict_message_style: str,
    expected: str,
) -> None:
    result = build_handling_guide(
        support_preference="listen_to_me",
        mbti=MbtiType.ENTP,
        attachment_score=0,
        conflict_style=conflict_style,
        conflict_message_style=conflict_message_style,
    )

    assert result[2] == expected


@pytest.mark.parametrize("mbti", list(MbtiType))
def test_uses_mbti_specific_attraction_copy(mbti: MbtiType) -> None:
    result = build_handling_guide(
        support_preference="listen_to_me",
        mbti=mbti,
        attachment_score=0,
        conflict_style="hint_and_wait",
        conflict_message_style="rehearse_with_ai",
    )

    assert result[3] == ATTRACTION_GUIDE_COPY[mbti]
