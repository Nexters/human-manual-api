from pakit.domain.assessment import (
    AssessmentInput,
    AssessmentResult,
    Classification,
    MbtiType,
)
from pakit.domain.characters import NOUNS as CHARACTER_NOUNS

NOUNS = CHARACTER_NOUNS

# PRD 07의 문구 후보이며, 형용사 확정 시 콘텐츠 저장소로 이동할 대상이다.
DESCRIPTORS: dict[tuple[str, str], str] = {
    ("A1", "B1"): "좋아하면 대놓고 자랑하는",
    ("A1", "B2"): "팩트부터 날리고 밥은 사주는",
    ("A1", "B3"): "좋으면 새벽에도 카톡 폭탄 보내는",
    ("A1", "B4"): "꽂히면 그날 바로 번호 따는",
    ("A2", "B1"): "먼저 연락은 안 해도 생일은 챙기는",
    ("A2", "B2"): "지적도 매뉴얼인",
    ("A2", "B3"): "언제 밥 먹자는 말을 자주 하는",
    ("A2", "B4"): "물을 때마다 다른 곳에 있는",
    ("A3", "B1"): "꾸미고 플러팅했다고 생각하는",
    ("A3", "B2"): "답장은 짧아도 읽씹은 안 하는",
    ("A3", "B3"): "오래전 게시물도 보고 안부를 묻는",
    ("A3", "B4"): "직진하는 상상만 많이 해본",
    ("A4", "B1"): "낯가리지만 친해지면 말 많은",
    ("A4", "B2"): "답장이 늦고 프사도 안 바꾸는",
    ("A4", "B3"): "시뮬레이션을 마치고 데이트하는",
    ("A4", "B4"): "뭐 하고 사는지 아무도 모르는",
}

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
    descriptor = DESCRIPTORS[(packaging_code, opening_tool_code)]
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
