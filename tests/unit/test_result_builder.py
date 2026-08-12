import pytest

from pakit.domain.assessment import AssessmentInput, AxisScores, MbtiType
from pakit.services.result_builder import NOUNS, build_assessment_result

EXPECTED_NOUNS = {
    MbtiType.INTJ: "큐브",
    MbtiType.ISTJ: "로봇",
    MbtiType.ENTJ: "불도저",
    MbtiType.ESTJ: "헬리콥터",
    MbtiType.INFJ: "비밀상자",
    MbtiType.ISFJ: "테디베어",
    MbtiType.ENFJ: "기차",
    MbtiType.ESFJ: "티포트",
    MbtiType.INFP: "쿠크다스",
    MbtiType.ISFP: "침대",
    MbtiType.ENFP: "연",
    MbtiType.ESFP: "실로폰",
    MbtiType.INTP: "망원경",
    MbtiType.ISTP: "공구함",
    MbtiType.ENTP: "팽이",
    MbtiType.ESTP: "RC카",
}


@pytest.mark.parametrize(
    ("scores", "expected"),
    [
        ((100, 0, 0, 0), ("A1", "B1")),
        ((100, 100, 100, 0), ("A2", "B2")),
        ((0, 0, 0, 100), ("A3", "B3")),
        ((0, 100, 100, 100), ("A4", "B4")),
    ],
)
def test_builds_all_axis_quadrants(
    scores: tuple[int, int, int, int], expected: tuple[str, str]
) -> None:
    expression, attachment, manner, novelty = scores
    data = AssessmentInput(
        mbti=MbtiType.ENTP,
        axes=AxisScores(
            expression=expression,
            attachment=attachment,
            manner=manner,
            novelty=novelty,
        ),
    )

    result = build_assessment_result(data)

    assert (
        result.classification.packaging_code,
        result.classification.opening_tool_code,
    ) == expected
    assert result.classification.noun == "팽이"
    assert result.product_name.endswith("팽이")


def test_all_mbti_characters_match_final_assets() -> None:
    assert NOUNS == EXPECTED_NOUNS


@pytest.mark.parametrize(("mbti", "noun"), EXPECTED_NOUNS.items())
def test_returns_final_character_without_content_warning(mbti: MbtiType, noun: str) -> None:
    result = build_assessment_result(
        AssessmentInput(
            mbti=mbti,
            axes=AxisScores(expression=0, attachment=0, manner=0, novelty=0),
        )
    )

    assert result.classification.noun == noun
    assert result.content_warnings == []
