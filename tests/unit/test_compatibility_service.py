from dataclasses import replace

import pytest

from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_submission import (
    AxisScoresData,
    CharacterStoryData,
    ChargingData,
    CompatibilityProfileData,
    OverviewData,
    ResultParticipantData,
    SubmissionResultData,
    UnboxingItemData,
    UnboxingKitData,
)
from pakit.services.compatibility_service import (
    COMPATIBILITY_PROFILE_VERSION,
    CompatibilityUnavailableError,
    build_compatibility,
    build_compatibility_profile,
    build_compatible_friends,
    calculate_scores,
    compatibility_headline,
)


def _result(
    *,
    code: str,
    nickname: str,
    mbti: str,
    scores: AxisScoresData,
    support: str = "listen_to_me",
    conflict: str = "resolve_immediately",
    affection: str = "express_with_words",
    role: str = "guide",
    motivation: str = "achievement",
) -> SubmissionResultData:
    profile = CompatibilityProfileData(
        version=COMPATIBILITY_PROFILE_VERSION,
        mbti=mbti,
        relationship_role=role,
        motivation=motivation,
        support_preference=support,
        conflict_style=conflict,
        affection_style=affection,
    )
    return SubmissionResultData(
        result_code=code,
        participant=ResultParticipantData(nickname),
        overview=OverviewData("상위 4%", "형용사", "팽이", "형용사 팽이", "top", "", ()),
        unboxing_kit=UnboxingKitData(
            axis_scores=scores,
            title="제목",
            description="설명",
            packaging=UnboxingItemData("box", "상자", "/assets/box.png", (), "설명"),
            opening_tool=UnboxingItemData("tool", "도구", "/assets/tool.png", (), "설명"),
        ),
        features=(),
        character_story=CharacterStoryData("제목", "설명"),
        can_do=(),
        warnings=(),
        charging=ChargingData(90, "설명", ()),
        compatible_friends=(),
        compatibility_profile=profile,
    )


@pytest.mark.parametrize(
    ("moment", "strength"),
    [
        (moment, strength)
        for moment in ("decision", "worries", "hangout", "information")
        for strength in (
            "set_direction",
            "lift_mood",
            "make_it_happen",
            "draw_people_out",
            "coordinate_opinions",
            "remember_and_care",
        )
    ],
)
def test_builds_a_relationship_role_for_every_q1_q2_combination(
    moment: str,
    strength: str,
) -> None:
    profile = build_compatibility_profile(
        mbti=MbtiType.ENTP,
        relationship_moment=moment,
        relationship_strength=strength,
        motivation="fun",
        support_preference="make_me_laugh",
        conflict_style="resolve_immediately",
        affection_style="express_with_actions",
    )

    assert profile.relationship_role in {
        "guide",
        "connector",
        "organizer",
        "supporter",
        "energizer",
    }
    assert profile.version == COMPATIBILITY_PROFILE_VERSION


@pytest.mark.parametrize(
    ("friend_mbti", "expected_mbti_score"),
    [("ENTP", 100), ("INTP", 94), ("ISTP", 88), ("ISFP", 82), ("ISFJ", 76)],
)
def test_mbti_score_uses_each_matching_axis(
    friend_mbti: str,
    expected_mbti_score: int,
) -> None:
    axes = AxisScoresData(50, 50, 50, 50)
    mine = _result(code="mine0001", nickname="나", mbti="ENTP", scores=axes)
    friend = _result(code="frnd0001", nickname="친구", mbti=friend_mbti, scores=axes)

    assert calculate_scores(mine, friend).mbti == expected_mbti_score


def test_compatibility_score_is_symmetric_and_keeps_each_person_target() -> None:
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=AxisScoresData(20, 100, 0, 33),
        support="make_me_laugh",
        affection="express_with_actions",
        role="energizer",
        motivation="fun",
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ISFJ",
        scores=AxisScoresData(80, 20, 100, 100),
        support="give_me_space",
        conflict="hint_and_wait",
        role="supporter",
        motivation="people_duty",
    )

    forward = build_compatibility(mine, friend)
    reverse = build_compatibility(friend, mine)

    assert forward.synergy.score == reverse.synergy.score
    assert 0 <= forward.synergy.score <= 100
    assert forward.tips[0].target == "mine"
    assert forward.tips[0].title == "지은님에게"
    assert forward.tips[0].image_url == mine.overview.image_url
    assert forward.tips[1].target == "friend"
    assert forward.tips[1].title == "선우님에게"
    assert forward.tips[1].image_url == friend.overview.image_url


def test_distance_tip_names_the_person_whose_contact_may_slow_down() -> None:
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=AxisScoresData(0, 50, 50, 50),
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ENTP",
        scores=AxisScoresData(100, 50, 50, 50),
    )

    result = build_compatibility(mine, friend)

    assert result.tips[0].description == (
        "혼자만의 시간이 필요해도 선우님에게 짧게 안부를 남기면 관계를 더 편하게 믿을 수 있어요."
    )
    assert result.tips[1].description == (
        "지은님이 연락이 뜸한 순간을 마음이 멀어진 신호로 단정하지 않으면 훨씬 편해져요."
    )


def test_returns_four_detailed_conversation_topics() -> None:
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=AxisScoresData(20, 100, 0, 33),
        support="make_me_laugh",
        affection="express_with_words",
        role="energizer",
        motivation="fun",
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ISFJ",
        scores=AxisScoresData(80, 20, 100, 100),
        support="give_me_space",
        conflict="hint_and_wait",
        affection="express_with_actions",
        role="supporter",
        motivation="people_duty",
    )

    details = build_compatibility(mine, friend).details

    assert [detail.key for detail in details] == ["distance", "conflict", "care", "pace"]
    assert all(0 <= detail.score <= 100 for detail in details)
    assert all("지은" in detail.description for detail in details)
    assert all("선우" in detail.description for detail in details)
    assert "애정의 크기보다 편한 간격" in details[0].description
    assert "질문은 공격이 아니고" in details[1].description
    assert details[2].title == "마음을 주고받는 방식"
    assert "같이 웃으며 분위기를 바꿀 때" in details[2].description
    assert "재밌는 일이 생겨야" in details[3].description


def test_summarizes_a_shared_support_need_without_repeating_each_person() -> None:
    axes = AxisScoresData(50, 50, 50, 50)
    mine = _result(
        code="mine0001",
        nickname="잉뿌삐",
        mbti="INFP",
        scores=axes,
        support="listen_to_me",
        affection="express_with_words",
    )
    friend = _result(
        code="frnd0001",
        nickname="이해선",
        mbti="ENTP",
        scores=axes,
        support="listen_to_me",
        affection="express_with_actions",
    )

    care = build_compatibility(mine, friend).details[2]

    assert care.label == "원하는 위로는 같아요"
    assert care.description == (
        "잉뿌삐님과 이해선님은 모두 이야기를 충분히 들어줄 때 마음이 풀려요. 다만 "
        "잉뿌삐님은 말과 반응으로 마음을 보여주는 편이에요. 이해선님은 말보다 행동으로 "
        "마음을 보여주는 편이에요. 원하는 위로는 같지만 애정이 보이는 모양은 달라요."
    )


def test_recognizes_when_support_and_affection_are_both_shared() -> None:
    axes = AxisScoresData(50, 50, 50, 50)
    mine = _result(code="mine0001", nickname="지은", mbti="ENTP", scores=axes)
    friend = _result(code="frnd0001", nickname="선우", mbti="ENTP", scores=axes)

    care = build_compatibility(mine, friend).details[2]

    assert care.label == "위로도 표현도 닮았어요"
    assert "서로의 챙김을 비교적 쉽게 알아보는 조합" in care.description


def test_rejects_a_legacy_result_without_a_compatibility_profile() -> None:
    axes = AxisScoresData(50, 50, 50, 50)
    mine = _result(code="mine0001", nickname="나", mbti="ENTP", scores=axes)
    legacy = replace(
        _result(code="old00001", nickname="친구", mbti="ISFJ", scores=axes),
        compatibility_profile=None,
    )

    with pytest.raises(CompatibilityUnavailableError):
        build_compatibility(mine, legacy)


@pytest.mark.parametrize(
    ("score", "expected_title"),
    [
        (63, "사용설명서가 필요한 장난감"),
        (64, "맞춰갈수록 좋은 장난감"),
        (75, "맞춰갈수록 좋은 장난감"),
        (76, "다른 맛이 잘 섞이는 장난감"),
        (87, "다른 맛이 잘 섞이는 장난감"),
        (88, "찰떡궁합 환상의 장난감"),
    ],
)
def test_compatibility_headline_boundaries(score: int, expected_title: str) -> None:
    assert compatibility_headline(score)[0] == expected_title


def test_low_compatibility_headline_explains_the_difference_without_judging_the_pair() -> None:
    assert compatibility_headline(63) == (
        "사용설명서가 필요한 장난감",
        "서로 편한 방식이 달라, 각자의 사용법을 알아갈 시간이 필요한 사이예요.",
    )


@pytest.mark.parametrize("mbti", list(MbtiType))
def test_builds_two_distinct_compatible_friend_cards_for_every_mbti(mbti: MbtiType) -> None:
    friends = build_compatible_friends(mbti, AxisScoresData(50, 50, 50, 50))

    assert len(friends) == 2
    assert friends[0].character_id != friends[1].character_id
    assert all(friend.badge == "환상의 장난감" for friend in friends)
    assert all(friend.image_url.startswith("/assets/characters/") for friend in friends)


@pytest.mark.parametrize(
    ("scores", "expected_phrase"),
    [
        (AxisScoresData(0, 50, 0, 50), "먼저 달리는"),
        (AxisScoresData(100, 50, 0, 50), "놓친 약속과 사람"),
        (AxisScoresData(0, 50, 100, 50), "새 선택지"),
        (AxisScoresData(100, 50, 100, 50), "새로운 재미"),
    ],
)
def test_personalizes_the_second_friend_card_with_axis_quadrants(
    scores: AxisScoresData,
    expected_phrase: str,
) -> None:
    friends = build_compatible_friends(MbtiType.ENTP, scores)

    assert expected_phrase in friends[1].description
