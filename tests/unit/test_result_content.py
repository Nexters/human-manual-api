from pakit.domain.assessment import MbtiType
from pakit.services.result_content import (
    AFFECTION_RECOGNITION_COPY,
    ANGER_TRIGGER_WARNING_COPY,
    CHARACTER_STORY_COPY,
    COMBINATION_COPY,
    COMMUNICATION_WARNING_COPY,
    CONFLICT_SUPPORT_COPY,
    EMOTIONAL_PROCESSING_COPY,
    MBTI_MIDDLE_GROUP,
    MBTI_RARITY_COPY,
    MBTI_STRENGTH_COPY,
    MOTIVATION_COPY,
    MOTIVATION_DESCRIPTION,
    OPENING_TOOL_COPY,
    PACKAGING_COPY,
    PROTECTED_TIME_WARNING_COPY,
    RELATIONSHIP_DISTANCE_COPY,
    RELATIONSHIP_ROLE_COPY,
    RESULT_CONTENT_VERSION,
    SOCIAL_ENERGY_WARNING_COPY,
    SUPPORT_PREFERENCE_COPY,
)


def test_defines_one_distinct_character_story_for_every_mbti() -> None:
    assert set(CHARACTER_STORY_COPY) == set(MbtiType)
    assert len({copy.title for copy in CHARACTER_STORY_COPY.values()}) == len(MbtiType)
    assert len({copy.description for copy in CHARACTER_STORY_COPY.values()}) == len(MbtiType)
    assert all(copy.title and copy.description for copy in CHARACTER_STORY_COPY.values())


def test_uses_confirmed_estj_helicopter_story() -> None:
    story = CHARACTER_STORY_COPY[MbtiType.ESTJ]

    assert story.title == "정해진 순서를 건너뛰지 않고 현장을 책임지는 헬리콥터"
    assert story.description == (
        "헬리콥터는 급한 상황일수록 점검 순서를 먼저 밟아요. 늘 하던 방식으로 상태를 확인한 뒤 "
        "필요한 자리에 정확히 내려가, 누가 무엇을 언제 할지 분명하게 정리하죠. 검증된 방식으로 "
        "현장을 맡아 끝까지 책임지는 모습이 닮아 헬리콥터가 도착했습니다."
    )


def test_uses_confirmed_intp_telescope_story() -> None:
    story = CHARACTER_STORY_COPY[MbtiType.INTP]

    assert story.title == "원리를 알아야 비로소 초점이 잡히는 망원경"
    assert story.description == (
        "망원경은 눈에 대기만 한다고 바로 보이지 않아요. 렌즈가 어떤 원리로 상을 잡는지 "
        "이해하고 몇 번이고 직접 조절해야 흐릿하던 것이 선명해지죠. 남들이 당연하게 넘긴 것도 "
        "직접 뜯어보고 원리를 이해해야 넘어가는 모습이 닮아 망원경이 도착했습니다."
    )


def test_defines_copy_for_all_unboxing_combinations() -> None:
    expected_keys = {
        (f"A{packaging}", f"B{tool}") for packaging in range(1, 5) for tool in range(1, 5)
    }

    assert set(COMBINATION_COPY) == expected_keys
    assert len({copy.title for copy in COMBINATION_COPY.values()}) == 16
    assert len({copy.description for copy in COMBINATION_COPY.values()}) == 16


def test_defines_one_relationship_role_for_every_q01_q02_combination() -> None:
    q01_values = {"decision", "worries", "hangout", "information"}
    q02_values = {
        "organize_and_coordinate",
        "lift_mood",
        "make_it_happen",
        "care_for_others",
    }

    assert set(RELATIONSHIP_ROLE_COPY) == {
        (q01_value, q02_value) for q01_value in q01_values for q02_value in q02_values
    }
    assert len({copy.title for copy in RELATIONSHIP_ROLE_COPY.values()}) == 16
    assert len({copy.description for copy in RELATIONSHIP_ROLE_COPY.values()}) == 16
    assert all(len(copy.description) <= 50 for copy in RELATIONSHIP_ROLE_COPY.values())
    assert {key: copy.title for key, copy in RELATIONSHIP_ROLE_COPY.items()} == {
        ("decision", "organize_and_coordinate"): "결정 조율자",
        ("decision", "lift_mood"): "말문 트기왕",
        ("decision", "make_it_happen"): "실행 총무",
        ("decision", "care_for_others"): "의견 챙김왕",
        ("worries", "organize_and_coordinate"): "고민 길잡이",
        ("worries", "lift_mood"): "기분 환기담당",
        ("worries", "make_it_happen"): "현실 해결사",
        ("worries", "care_for_others"): "맞춤 위로왕",
        ("hangout", "organize_and_coordinate"): "모임 조율대장",
        ("hangout", "lift_mood"): "분위기 메이커",
        ("hangout", "make_it_happen"): "번개 추진왕",
        ("hangout", "care_for_others"): "모임 챙김대장",
        ("information", "organize_and_coordinate"): "정보 정리왕",
        ("information", "lift_mood"): "설명 예능인",
        ("information", "make_it_happen"): "실행 설계자",
        ("information", "care_for_others"): "맞춤 정보통",
    }


def test_relationship_roles_do_not_repeat_answer_labels() -> None:
    answer_labels = {
        "결정이 필요할 때",
        "고민 있을 때",
        "놀 사람 필요할 때",
        "정보 필요할 때",
        "잠깐, 의견 정리해서 방향부터 잡자.",
        "분위기 왜 이래ㅋㅋ 일단 웃고 보자.",
        "재밌겠다. 일단 해보고 생각하자!",
        "넌 뭐가 좋아? 말해주면 내가 챙길게.",
    }

    rendered_copy = " ".join(
        f"{copy.title} {copy.description}" for copy in RELATIONSHIP_ROLE_COPY.values()
    )
    assert all(label not in rendered_copy for label in answer_labels)


def test_defines_one_distinct_strength_for_every_mbti() -> None:
    assert set(MBTI_STRENGTH_COPY) == set(MbtiType)
    assert len({copy.title for copy in MBTI_STRENGTH_COPY.values()}) == len(MbtiType)
    assert len({copy.description for copy in MBTI_STRENGTH_COPY.values()}) == len(MbtiType)
    assert {mbti.value: copy.title for mbti, copy in MBTI_STRENGTH_COPY.items()} == {
        "INTJ": "큰그림을 봐요",
        "ISTJ": "끝까지 해내요",
        "ENTJ": "목표를 이뤄요",
        "ESTJ": "순서대로 해요",
        "INFJ": "마음을 읽어요",
        "ISFJ": "내편은 지켜요",
        "ENFJ": "용기를 줘요",
        "ESFJ": "모두를 챙겨요",
        "INFP": "소신을 지켜요",
        "ISFP": "감각을 믿어요",
        "ENFP": "가능성을 봐요",
        "ESFP": "지금을 즐겨요",
        "INTP": "원리를 따져요",
        "ISTP": "직접 해결해요",
        "ENTP": "다르게 봐요",
        "ESTP": "기회를 잡아요",
    }


def test_defines_confirmed_rarity_for_every_mbti() -> None:
    assert set(MBTI_RARITY_COPY) == set(MbtiType)
    assert {mbti.value: rarity for mbti, rarity in MBTI_RARITY_COPY.items()} == {
        "INFJ": "상위 1.5%",
        "ENTJ": "상위 1.8%",
        "INTJ": "상위 2.1%",
        "ENFJ": "상위 2.5%",
        "ENTP": "상위 3.2%",
        "INTP": "상위 3.3%",
        "ESTP": "상위 4.3%",
        "INFP": "상위 4.4%",
        "ISTP": "상위 5.4%",
        "ENFP": "상위 8.1%",
        "ESFP": "상위 8.5%",
        "ESTJ": "상위 8.7%",
        "ISFP": "상위 8.8%",
        "ISTJ": "상위 11.6%",
        "ESFJ": "상위 12.3%",
        "ISFJ": "상위 13.5%",
    }


def test_defines_every_emotional_processing_quadrant() -> None:
    assert set(EMOTIONAL_PROCESSING_COPY) == {
        ("explore", "egen"),
        ("direct", "egen"),
        ("explore", "teto"),
        ("direct", "teto"),
    }
    assert len({copy.title for copy in EMOTIONAL_PROCESSING_COPY.values()}) == 4
    assert len({copy.description for copy in EMOTIONAL_PROCESSING_COPY.values()}) == 4


def test_defines_motivation_copy_and_grouped_descriptions_for_every_allowed_input() -> None:
    assert set(MOTIVATION_COPY) == {
        "curiosity",
        "needed_by_someone",
        "clear_goal",
        "responsibility",
        "last_chance",
        "fun",
    }
    assert {value: copy.title for value, copy in MOTIVATION_COPY.items()} == {
        "curiosity": "궁금한 건 못 참아요",
        "needed_by_someone": "의리가 강해요",
        "clear_goal": "끝은 봐야 해요",
        "responsibility": "약속했으면 지켜요",
        "last_chance": "기회는 꼭 잡아요",
        "fun": "재밌는 건 해야 해요",
    }
    assert set(MBTI_MIDDLE_GROUP) == set(MbtiType)
    assert set(MBTI_MIDDLE_GROUP.values()) == {"NT", "ST", "NF", "SF"}
    assert set(MOTIVATION_DESCRIPTION) == {
        (answer, group) for answer in MOTIVATION_COPY for group in {"NT", "ST", "NF", "SF"}
    }


def test_defines_every_handling_guide_copy() -> None:
    support_preferences = {
        "listen_to_me",
        "take_me_out",
        "give_me_space",
        "solve_together",
        "make_me_laugh",
    }
    assert set(SUPPORT_PREFERENCE_COPY) == {
        (preference, group)
        for preference in support_preferences
        for group in {"NT", "ST", "NF", "SF"}
    }
    assert set(RELATIONSHIP_DISTANCE_COPY) == {"0_24", "25_49", "50_74", "75_100"}
    assert set(CONFLICT_SUPPORT_COPY) == {
        (conflict_style, message_style)
        for conflict_style in {"hint_and_wait", "resolve_immediately"}
        for message_style in {"rehearse_with_ai", "send_immediately"}
    }
    assert set(AFFECTION_RECOGNITION_COPY) == {
        "express_with_words",
        "express_with_actions",
    }


def test_uses_confirmed_give_me_space_copy_for_every_mbti_middle_group() -> None:
    assert {
        group: SUPPORT_PREFERENCE_COPY[("give_me_space", group)]
        for group in ("NT", "ST", "NF", "SF")
    } == {
        "NT": "생각이 정리될 때까지 혼자 생각할 시간을 주세요",
        "ST": "괜찮냐고 계속 묻기보다 평소처럼 지내주세요",
        "NF": "내가 마음을 꺼낼 준비가 됐을 때 알아봐주세요",
        "SF": "말은 안 걸어도 좋으니, 곁에 있다는 표시만 남겨주세요",
    }


def test_uses_confirmed_take_me_out_copy_for_st_group() -> None:
    assert SUPPORT_PREFERENCE_COPY[("take_me_out", "ST")] == (
        "왜 그러냐고 묻는 대신, 늘 가던 곳에 같이 가서 시간 보내주세요"
    )


def test_feature_titles_are_at_most_seven_characters() -> None:
    relationship_roles = list(RELATIONSHIP_ROLE_COPY.values())
    emotional_processing = list(EMOTIONAL_PROCESSING_COPY.values())
    mbti_features = list(MBTI_STRENGTH_COPY.values())

    assert all(
        len(feature.title) <= 7
        for feature in (*relationship_roles, *emotional_processing, *mbti_features)
    )
    assert all(len(copy.title) <= 11 for copy in MOTIVATION_COPY.values())


def test_uses_confirmed_titles_for_revised_combinations() -> None:
    assert COMBINATION_COPY[("A2", "B1")].title == "평소엔 절전, 중요한 순간엔 풀가동되는 사람"
    assert COMBINATION_COPY[("A3", "B2")].title == "말수는 아껴도 자리는 안 뜨는 사람"
    assert COMBINATION_COPY[("A4", "B2")].title == "연락은 뜸해도 관계는 안 끊기는 사람"
    assert COMBINATION_COPY[("A4", "B4")].title == "과정은 비공개, 결과로 증명하는 사람"


def test_defines_copy_for_all_packaging_types() -> None:
    assert {code: copy.type for code, copy in PACKAGING_COPY.items()} == {
        "A1": "fragile_box",
        "A2": "minimal_box",
        "A3": "matryoshka_box",
        "A4": "locked_box",
    }
    assert all(len(copy.tags) == 2 and copy.reason for copy in PACKAGING_COPY.values())
    assert all(len(copy.reason) <= 220 for copy in PACKAGING_COPY.values())


def test_defines_copy_for_all_opening_tools() -> None:
    assert {code: copy.type for code, copy in OPENING_TOOL_COPY.items()} == {
        "B1": "glove",
        "B2": "utility_knife",
        "B3": "magic_wand",
        "B4": "chainsaw",
    }
    assert all(len(copy.tags) == 2 and copy.reason for copy in OPENING_TOOL_COPY.values())
    assert all(len(copy.reason) <= 180 for copy in OPENING_TOOL_COPY.values())


def test_result_content_has_explicit_version() -> None:
    assert RESULT_CONTENT_VERSION == "2026-08-19.4"


def test_defines_all_warning_copy_variants() -> None:
    assert set(PROTECTED_TIME_WARNING_COPY) == {
        "after_waking",
        "during_meal",
        "after_work",
        "late_night",
    }
    assert set(ANGER_TRIGGER_WARNING_COPY) == {
        "rush",
        "interrupt",
        "take_food",
        "arrive_late",
        "nag",
        "change_plan",
    }
    assert set(SOCIAL_ENERGY_WARNING_COPY) == {"E", "I"}
    assert COMMUNICATION_WARNING_COPY == {
        "T": "해결하려고 꺼낸 말에 차갑다는 말이 돌아오면 억울해져요",
        "F": "속마음을 꺼냈는데 유난이라는 말이 돌아오면 오래 마음에 남아요",
    }
