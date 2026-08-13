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
    assert RESULT_CONTENT_VERSION == "2026-08-13.4"
