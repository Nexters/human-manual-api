from enum import StrEnum

from pydantic import BaseModel, Field


class MbtiType(StrEnum):
    INTJ = "INTJ"
    ISTJ = "ISTJ"
    ENTJ = "ENTJ"
    ESTJ = "ESTJ"
    INFJ = "INFJ"
    ISFJ = "ISFJ"
    ENFJ = "ENFJ"
    ESFJ = "ESFJ"
    INFP = "INFP"
    ISFP = "ISFP"
    ENFP = "ENFP"
    ESFP = "ESFP"
    INTP = "INTP"
    ISTP = "ISTP"
    ENTP = "ENTP"
    ESTP = "ESTP"


class AxisScores(BaseModel):
    """Scores use the PRD's left pole at 0 and right pole at 100."""

    expression: int = Field(ge=0, le=100, description="탐색형 0 ↔ 직진형 100")
    attachment: int = Field(ge=0, le=100, description="밀착형 0 ↔ 거리조절형 100")
    manner: int = Field(ge=0, le=100, description="에겐형 0 ↔ 테토형 100")
    novelty: int = Field(ge=0, le=100, description="루틴형 0 ↔ 탐험형 100")


class AssessmentInput(BaseModel):
    mbti: MbtiType
    axes: AxisScores


class Classification(BaseModel):
    packaging_code: str
    opening_tool_code: str
    noun: str
    descriptor: str


class AssessmentResult(BaseModel):
    product_name: str
    classification: Classification
    provisional: bool
    content_warnings: list[str]
