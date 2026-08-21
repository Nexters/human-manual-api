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
from pakit.domain.characters import CHARACTERS
from pakit.services.compatibility_service import (
    CARE_DELIVERY_MATCH,
    CARE_MATCH,
    COMPATIBILITY_PROFILE_VERSION,
    COMPATIBLE_FRIEND_DESCRIPTION,
    MISMATCHED_FRIEND_DESCRIPTION,
    RELATIONSHIP_ROLE_BY_ANSWERS,
    CompatibilityScores,
    CompatibilityUnavailableError,
    build_compatibility,
    build_compatibility_profile,
    build_compatible_friends,
    calculate_scores,
    compatibility_headline,
)


def test_weights_relationship_answers_at_ninety_percent_and_mbti_at_ten_percent() -> None:
    scores = CompatibilityScores(distance=100, conflict=80, care=60, pace=40, mbti=20)

    assert scores.total == 67


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
            "organize_and_coordinate",
            "lift_mood",
            "make_it_happen",
            "care_for_others",
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


def test_maps_every_q1_q2_combination_to_the_confirmed_compatibility_role() -> None:
    assert RELATIONSHIP_ROLE_BY_ANSWERS == {
        ("decision", "organize_and_coordinate"): "guide",
        ("decision", "lift_mood"): "connector",
        ("decision", "make_it_happen"): "organizer",
        ("decision", "care_for_others"): "supporter",
        ("worries", "organize_and_coordinate"): "guide",
        ("worries", "lift_mood"): "energizer",
        ("worries", "make_it_happen"): "guide",
        ("worries", "care_for_others"): "supporter",
        ("hangout", "organize_and_coordinate"): "organizer",
        ("hangout", "lift_mood"): "energizer",
        ("hangout", "make_it_happen"): "organizer",
        ("hangout", "care_for_others"): "supporter",
        ("information", "organize_and_coordinate"): "guide",
        ("information", "lift_mood"): "connector",
        ("information", "make_it_happen"): "guide",
        ("information", "care_for_others"): "supporter",
    }


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
    assert result.relationship_tip.description == (
        "지은님과 선우님은 서운한 일이 생겨도 대화를 다시 이어가는 힘이 있어요. "
        "연락이 뜸해질 때 쓸 짧은 신호 하나를 정해두면 각자의 시간도 더 편하게 믿을 수 있어요."
    )


def test_distance_detail_keeps_two_independent_people_in_the_same_type() -> None:
    mine = _result(
        code="mine0001",
        nickname="박종하",
        mbti="ENTP",
        scores=AxisScoresData(45, 50, 50, 50),
    )
    friend = _result(
        code="frnd0001",
        nickname="이해선",
        mbti="ENTP",
        scores=AxisScoresData(0, 50, 50, 50),
    )

    distance = build_compatibility(mine, friend).details[0]

    assert distance.description == (
        "박종하님과 이해선님은 모두 각자의 시간을 중요하게 생각해요. 다만 "
        "박종하님은 이해선님보다 조금 더 자주 안부를 나눌 때 관계가 편해져요."
    )


def test_distance_detail_keeps_two_close_people_in_the_same_type() -> None:
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=AxisScoresData(100, 50, 50, 50),
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ENTP",
        scores=AxisScoresData(55, 50, 50, 50),
    )

    distance = build_compatibility(mine, friend).details[0]

    assert "모두 자주 연결될 때 관계가 편해져요" in distance.description
    assert "선우님은 가까운 사이에서도 잠깐의 여유가 필요해요" in distance.description


@pytest.mark.parametrize(("independent_score", "close_score"), [(48, 50), (35, 50)])
def test_distance_detail_treats_a_cross_boundary_gap_up_to_fifteen_as_naturally_close(
    independent_score: int,
    close_score: int,
) -> None:
    mine = _result(
        code="mine0001",
        nickname="거리조절",
        mbti="ENTP",
        scores=AxisScoresData(independent_score, 50, 50, 50),
    )
    friend = _result(
        code="frnd0001",
        nickname="밀착",
        mbti="ENTP",
        scores=AxisScoresData(close_score, 50, 50, 50),
    )

    distance = build_compatibility(mine, friend).details[0]

    assert distance.description == (
        "원하는 간격의 차이가 크지 않아 자연스럽게 맞는 사이예요. 다만 상대적으로 "
        "밀착님은 안부를 조금 더 자주 나누는 게 편하고, 거리조절님은 혼자 쉬는 틈이 "
        "조금 더 필요해요."
    )


def test_distance_detail_explains_a_cross_boundary_gap_over_fifteen_as_needing_adjustment() -> None:
    mine = _result(
        code="mine0001",
        nickname="거리조절",
        mbti="ENTP",
        scores=AxisScoresData(32, 50, 50, 50),
    )
    friend = _result(
        code="frnd0001",
        nickname="밀착",
        mbti="ENTP",
        scores=AxisScoresData(50, 50, 50, 50),
    )

    distance = build_compatibility(mine, friend).details[0]

    assert distance.description == (
        "서로 원하는 관계의 간격이 달라 조금씩 맞춰갈 필요가 있는 사이예요. 밀착님은 "
        "자주 연락하고 함께 있을 때 안정감을 느끼고, 거리조절님은 가까운 사이에서도 혼자 "
        "보내는 시간이 필요해요."
    )


@pytest.mark.parametrize(
    ("conflict_style", "mine_expression", "friend_expression", "shared_copy"),
    [
        ("resolve_immediately", 100, 33, "모두 서운한 일을 바로 풀고 싶어 해요"),
        ("hint_and_wait", 67, 0, "모두 마음을 먼저 정리할 시간이 필요해요"),
    ],
)
def test_conflict_detail_explains_degree_within_the_shared_conflict_type(
    conflict_style: str,
    mine_expression: int,
    friend_expression: int,
    shared_copy: str,
) -> None:
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=AxisScoresData(50, mine_expression, 50, 50),
        conflict=conflict_style,
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ENTP",
        scores=AxisScoresData(50, friend_expression, 50, 50),
        conflict=conflict_style,
    )

    conflict = build_compatibility(mine, friend).details[1]

    assert shared_copy in conflict.description


@pytest.mark.parametrize(
    ("mine_routine", "friend_routine", "shared_copy"),
    [
        (33, 0, "모두 새로운 변화를 즐겨요"),
        (100, 67, "모두 계획이 있을 때 편해요"),
    ],
)
def test_pace_detail_explains_degree_within_the_shared_routine_type(
    mine_routine: int,
    friend_routine: int,
    shared_copy: str,
) -> None:
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=AxisScoresData(50, 50, mine_routine, 50),
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ENTP",
        scores=AxisScoresData(50, 50, friend_routine, 50),
    )

    pace = build_compatibility(mine, friend).details[3]

    assert shared_copy in pace.description


@pytest.mark.parametrize(
    ("mine_routine", "friend_routine", "expected_copy"),
    [
        (35, 50, "실제 속도 차이는 크지 않아 자연스럽게 맞출 수 있어요"),
        (34, 50, "계획과 익숙한 흐름이 있을 때 편하고"),
    ],
)
def test_pace_detail_uses_the_fifteen_point_boundary_across_routine_types(
    mine_routine: int,
    friend_routine: int,
    expected_copy: str,
) -> None:
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=AxisScoresData(50, 50, mine_routine, 50),
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ENTP",
        scores=AxisScoresData(50, 50, friend_routine, 50),
    )

    pace = build_compatibility(mine, friend).details[3]

    assert expected_copy in pace.description


@pytest.mark.parametrize(
    ("mine_role", "friend_role", "expected_copy"),
    [
        ("guide", "guide", "모두 관계에서 방향을 잡는 역할에 먼저 손이 가는 편이에요"),
        ("guide", "supporter", "함께할 때 역할이 자연스럽게 나뉘어요"),
        ("guide", "energizer", "잘하는 일을 미리 나누면 함께 움직이기 편해요"),
    ],
)
def test_pace_detail_describes_each_relationship_role_pair(
    mine_role: str,
    friend_role: str,
    expected_copy: str,
) -> None:
    axes = AxisScoresData(50, 50, 50, 50)
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=axes,
        role=mine_role,
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ENTP",
        scores=axes,
        role=friend_role,
    )

    pace = build_compatibility(mine, friend).details[3]

    assert expected_copy in pace.description


def test_pace_score_uses_routine_and_relationship_role_only() -> None:
    axes = AxisScoresData(50, 50, 50, 50)
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=axes,
        role="guide",
        motivation="fun",
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ENTP",
        scores=axes,
        role="supporter",
        motivation="achievement",
    )
    friend_with_other_motivation = _result(
        code="frnd0002",
        nickname="선우",
        mbti="ENTP",
        scores=axes,
        role="supporter",
        motivation="novelty",
    )

    assert calculate_scores(mine, friend).pace == 99
    assert calculate_scores(mine, friend_with_other_motivation).pace == 99


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
    assert "서로 원하는 관계의 간격이 달라" in details[0].description
    assert "질문은 공격이 아니고" in details[1].description
    assert details[2].title == "마음을 주고받는 방식"
    assert "같이 웃으며 분위기를 바꿀 때" in details[2].description
    assert details[3].title == "함께 움직이는 방식"
    assert "지은님은 새로운 제안과 즉흥적인 변화가 있을 때 힘이 나요" in details[3].description
    assert "함께할 때 역할이 자연스럽게 나뉘어요" in details[3].description
    assert "재밌는 일이 생겨야" not in details[3].description


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

    assert care.label == "한쪽에는 바로 닿아요"
    assert care.description == (
        "잉뿌삐님과 이해선님은 모두 이야기를 충분히 들어줄 때 마음이 풀려요. "
        "잉뿌삐님은 말과 반응으로 마음을 보여주는 편이에요. 이해선님은 말보다 행동으로 "
        "마음을 보여주는 편이에요. 이해선님에게는 상대의 챙김이 잘 닿지만, 잉뿌삐님에게는 "
        "원하는 위로가 바로 전달되지 않을 수 있어요."
    )


def test_recognizes_when_support_and_affection_are_both_shared() -> None:
    axes = AxisScoresData(50, 50, 50, 50)
    mine = _result(code="mine0001", nickname="지은", mbti="ENTP", scores=axes)
    friend = _result(code="frnd0001", nickname="선우", mbti="ENTP", scores=axes)

    care = build_compatibility(mine, friend).details[2]

    assert care.label == "서로의 챙김이 잘 닿아요"
    assert "각자가 원하는 위로로 자연스럽게 닿아요" in care.description


@pytest.mark.parametrize(
    ("mine_affection", "friend_affection", "expected_label", "expected_copy"),
    [
        (
            "express_with_words",
            "express_with_words",
            "서로의 챙김이 잘 닿아요",
            "각자가 원하는 위로로 자연스럽게 닿아요",
        ),
        (
            "express_with_actions",
            "express_with_words",
            "한쪽에는 바로 닿아요",
            "지은님에게는 상대의 챙김이 잘 닿지만",
        ),
        (
            "express_with_words",
            "express_with_actions",
            "한쪽에는 바로 닿아요",
            "선우님에게는 상대의 챙김이 잘 닿지만",
        ),
        (
            "express_with_actions",
            "express_with_actions",
            "챙김에 번역이 필요해요",
            "서로 챙기고도 원하는 위로가 바로 전달되지 않을 수 있어요",
        ),
    ],
)
def test_describes_whether_care_reaches_each_person(
    mine_affection: str,
    friend_affection: str,
    expected_label: str,
    expected_copy: str,
) -> None:
    axes = AxisScoresData(50, 50, 50, 50)
    mine = _result(
        code="mine0001",
        nickname="지은",
        mbti="ENTP",
        scores=axes,
        support="listen_to_me",
        affection=mine_affection,
    )
    friend = _result(
        code="frnd0001",
        nickname="선우",
        mbti="ENTP",
        scores=axes,
        support="listen_to_me",
        affection=friend_affection,
    )

    care = build_compatibility(mine, friend).details[2]

    assert care.label == expected_label
    assert expected_copy in care.description


def test_covers_every_support_and_affection_pair_in_both_directions() -> None:
    axes = AxisScoresData(50, 50, 50, 50)
    labels_seen: set[str] = set()

    for mine_support in CARE_MATCH:
        for mine_affection in ("express_with_words", "express_with_actions"):
            for friend_support in CARE_MATCH:
                for friend_affection in ("express_with_words", "express_with_actions"):
                    mine = _result(
                        code="mine0001",
                        nickname="지은",
                        mbti="ENTP",
                        scores=axes,
                        support=mine_support,
                        affection=mine_affection,
                    )
                    friend = _result(
                        code="frnd0001",
                        nickname="선우",
                        mbti="ISFJ",
                        scores=axes,
                        support=friend_support,
                        affection=friend_affection,
                    )

                    care = build_compatibility(mine, friend).details[2]
                    reverse_care = build_compatibility(friend, mine).details[2]
                    mine_receives = friend_affection in CARE_DELIVERY_MATCH[mine_support]
                    friend_receives = mine_affection in CARE_DELIVERY_MATCH[friend_support]
                    expected_label = (
                        "서로의 챙김이 잘 닿아요"
                        if mine_receives and friend_receives
                        else "한쪽에는 바로 닿아요"
                        if mine_receives or friend_receives
                        else "챙김에 번역이 필요해요"
                    )
                    expected_score = round(
                        (
                            CARE_MATCH[mine_support][friend_affection]
                            + CARE_MATCH[friend_support][mine_affection]
                        )
                        / 2
                    )

                    assert care.score == expected_score
                    assert care.label == expected_label
                    assert reverse_care.score == expected_score
                    assert reverse_care.label == expected_label
                    assert "지은" in care.description and "선우" in care.description
                    labels_seen.add(care.label)

    assert labels_seen == {
        "서로의 챙김이 잘 닿아요",
        "한쪽에는 바로 닿아요",
        "챙김에 번역이 필요해요",
    }


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


@pytest.mark.parametrize(
    ("mbti", "compatible", "mismatched"),
    [
        (MbtiType.INTJ, MbtiType.ENFP, MbtiType.ESFP),
        (MbtiType.INTP, MbtiType.ENTJ, MbtiType.ESFJ),
        (MbtiType.ENTJ, MbtiType.INTP, MbtiType.ISFP),
        (MbtiType.ENTP, MbtiType.INFJ, MbtiType.ISFJ),
        (MbtiType.INFJ, MbtiType.ENTP, MbtiType.ESTP),
        (MbtiType.INFP, MbtiType.ENFJ, MbtiType.ESTJ),
        (MbtiType.ENFJ, MbtiType.INFP, MbtiType.ISTP),
        (MbtiType.ENFP, MbtiType.INTJ, MbtiType.ISTJ),
        (MbtiType.ISTJ, MbtiType.ESFP, MbtiType.ENFP),
        (MbtiType.ISFJ, MbtiType.ESTP, MbtiType.ENTP),
        (MbtiType.ESTJ, MbtiType.ISFP, MbtiType.INFP),
        (MbtiType.ESFJ, MbtiType.ISTP, MbtiType.INTP),
        (MbtiType.ISTP, MbtiType.ESFJ, MbtiType.ENFJ),
        (MbtiType.ISFP, MbtiType.ESTJ, MbtiType.ENTJ),
        (MbtiType.ESTP, MbtiType.ISFJ, MbtiType.INFJ),
        (MbtiType.ESFP, MbtiType.ISTJ, MbtiType.INTJ),
    ],
)
def test_builds_one_matching_and_one_mismatched_card_from_the_fixed_table(
    mbti: MbtiType,
    compatible: MbtiType,
    mismatched: MbtiType,
) -> None:
    friends = build_compatible_friends(mbti)

    assert len(friends) == 2
    assert [friend.character_id for friend in friends] == [
        CHARACTERS[compatible].code,
        CHARACTERS[mismatched].code,
    ]
    assert [friend.badge for friend in friends] == [
        "환상의 장난감",
        "환장의 장난감",
    ]
    assert [friend.description for friend in friends] == [
        COMPATIBLE_FRIEND_DESCRIPTION[mbti],
        MISMATCHED_FRIEND_DESCRIPTION[mbti],
    ]
    assert all(friend.image_url.startswith("/assets/characters/") for friend in friends)


def test_defines_friend_descriptions_for_every_mbti() -> None:
    assert set(COMPATIBLE_FRIEND_DESCRIPTION) == set(MbtiType)
    assert set(MISMATCHED_FRIEND_DESCRIPTION) == set(MbtiType)
    descriptions = (
        *COMPATIBLE_FRIEND_DESCRIPTION.values(),
        *MISMATCHED_FRIEND_DESCRIPTION.values(),
    )
    assert all("당신" in description for description in descriptions)
    assert all(description.endswith("요.") for description in descriptions)
