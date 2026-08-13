from pakit.domain.assessment import MbtiType
from pakit.services.result_content import (
    COMBINATION_COPY,
    MBTI_FEATURE_COPY,
    MBTI_MOTIVATION_GROUP,
    MOTIVATION_COPY,
    MOTIVATION_DESCRIPTION,
    OPENING_TOOL_COPY,
    PACKAGING_COPY,
    RELATIONSHIP_ROLE_COPY,
    RESULT_CONTENT_VERSION,
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
        "set_direction",
        "lift_mood",
        "make_it_happen",
        "draw_people_out",
        "coordinate_opinions",
        "remember_and_care",
    }

    assert set(RELATIONSHIP_ROLE_COPY) == {
        (q01_value, q02_value) for q01_value in q01_values for q02_value in q02_values
    }
    assert len({copy.title for copy in RELATIONSHIP_ROLE_COPY.values()}) == 24
    assert len({copy.description for copy in RELATIONSHIP_ROLE_COPY.values()}) == 24
    assert all(len(copy.description) <= 50 for copy in RELATIONSHIP_ROLE_COPY.values())


def test_relationship_roles_do_not_repeat_answer_labels() -> None:
    answer_labels = {
        '다들 "아무거나"만 반복하고 결정을 못 할 때',
        "혼자 생각해도 답이 안 나는 고민이 생겼을 때",
        "심심한데 누구를 불러야 재밌을지 고민될 때",
        "검색해도 원하는 정보를 찾지 못했을 때",
        "다들 우왕좌왕하면 방향부터 정한다",
        "어색해지면 먼저 분위기를 푼다",
        "말만 나온 일을 실제 계획으로 만든다",
        "누가 이야기하면 잘 받아줘 더 말하게 한다",
        "의견이 부딪히면 중간에서 정리한다",
        "각자 좋아하는 걸 기억해 챙긴다",
    }

    rendered_copy = " ".join(
        f"{copy.title} {copy.description}" for copy in RELATIONSHIP_ROLE_COPY.values()
    )
    assert all(label not in rendered_copy for label in answer_labels)


def test_defines_two_features_for_every_mbti() -> None:
    assert set(MBTI_FEATURE_COPY) == set(MbtiType)
    assert all(len(features) == 2 for features in MBTI_FEATURE_COPY.values())


def test_defines_motivation_copy_and_grouped_descriptions_for_every_allowed_input() -> None:
    assert set(MOTIVATION_COPY) == {
        "curiosity",
        "needed_by_someone",
        "clear_goal",
        "responsibility",
        "last_chance",
        "fun",
    }
    assert set(MBTI_MOTIVATION_GROUP) == set(MbtiType)
    assert set(MBTI_MOTIVATION_GROUP.values()) == {"NT", "ST", "NF", "SF"}
    assert set(MOTIVATION_DESCRIPTION) == {
        (answer, group) for answer in MOTIVATION_COPY for group in {"NT", "ST", "NF", "SF"}
    }


def test_feature_titles_are_at_most_seven_characters() -> None:
    relationship_roles = list(RELATIONSHIP_ROLE_COPY.values())
    mbti_features = [feature for features in MBTI_FEATURE_COPY.values() for feature in features]

    assert all(len(feature.title) <= 7 for feature in (*relationship_roles, *mbti_features))
    assert all(len(copy.title) <= 7 for copy in MOTIVATION_COPY.values())


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


def test_defines_copy_for_all_opening_tools() -> None:
    assert {code: copy.type for code, copy in OPENING_TOOL_COPY.items()} == {
        "B1": "glove",
        "B2": "utility_knife",
        "B3": "magic_wand",
        "B4": "chainsaw",
    }
    assert all(len(copy.tags) == 2 and copy.reason for copy in OPENING_TOOL_COPY.values())


def test_result_content_has_explicit_version() -> None:
    assert RESULT_CONTENT_VERSION == "2026-08-14.5"
