from pakit.services.result_content import (
    COMBINATION_COPY,
    OPENING_TOOL_COPY,
    PACKAGING_COPY,
    RESULT_CONTENT_VERSION,
)


def test_defines_copy_for_all_unboxing_combinations() -> None:
    expected_keys = {
        (f"A{packaging}", f"B{tool}") for packaging in range(1, 5) for tool in range(1, 5)
    }

    assert set(COMBINATION_COPY) == expected_keys
    assert len({copy.title for copy in COMBINATION_COPY.values()}) == 16
    assert len({copy.description for copy in COMBINATION_COPY.values()}) == 16


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
    assert RESULT_CONTENT_VERSION == "2026-08-13.7"
