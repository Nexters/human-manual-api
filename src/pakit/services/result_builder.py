from pakit.domain.assessment import (
    AssessmentInput,
    AssessmentResult,
    Classification,
    MbtiType,
)
from pakit.domain.characters import NOUNS as CHARACTER_NOUNS
from pakit.services.assessment_classifier import ADJECTIVES

NOUNS = CHARACTER_NOUNS

CONTENT_WARNINGS: dict[MbtiType, str] = {}


def _packaging_code(expression: int, attachment: int) -> str:
    if expression >= 50:
        return "A2" if attachment >= 50 else "A1"
    return "A4" if attachment >= 50 else "A3"


def _opening_tool_code(novelty: int, manner: int) -> str:
    if novelty >= 50:
        return "B4" if manner >= 50 else "B3"
    return "B2" if manner >= 50 else "B1"


def build_assessment_result(data: AssessmentInput) -> AssessmentResult:
    packaging_code = _packaging_code(data.axes.expression, data.axes.attachment)
    opening_tool_code = _opening_tool_code(data.axes.novelty, data.axes.manner)
    noun = NOUNS[data.mbti]
    descriptor = ADJECTIVES[(packaging_code, opening_tool_code)]
    warning = CONTENT_WARNINGS.get(data.mbti)

    return AssessmentResult(
        product_name=f"{descriptor} {noun}",
        classification=Classification(
            packaging_code=packaging_code,
            opening_tool_code=opening_tool_code,
            noun=noun,
            descriptor=descriptor,
        ),
        provisional=True,
        content_warnings=[warning] if warning else [],
    )
