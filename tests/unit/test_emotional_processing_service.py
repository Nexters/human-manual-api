import pytest

from pakit.services.emotional_processing_service import build_emotional_processing_feature


@pytest.mark.parametrize(
    ("expression", "egen", "expected_title"),
    [
        (0, 100, "혼자 곱씹어요"),
        (100, 100, "서운하면 직구"),
        (0, 0, "생각정리 먼저"),
        (100, 0, "바로 해결해요"),
    ],
)
def test_builds_every_emotional_processing_quadrant(
    expression: int, egen: int, expected_title: str
) -> None:
    result = build_emotional_processing_feature(expression, egen)

    assert result.title == expected_title


@pytest.mark.parametrize(
    ("expression", "egen", "expected_title"),
    [
        (49, 50, "혼자 곱씹어요"),
        (50, 50, "서운하면 직구"),
        (49, 49, "생각정리 먼저"),
        (50, 49, "바로 해결해요"),
    ],
)
def test_uses_fifty_point_axis_boundary(expression: int, egen: int, expected_title: str) -> None:
    result = build_emotional_processing_feature(expression, egen)

    assert result.title == expected_title
