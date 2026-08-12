from dataclasses import dataclass

from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_contract import AnswerKind


@dataclass(frozen=True)
class SubmittedAnswer:
    question_id: str
    kind: AnswerKind
    selected_id: str | None = None
    value: int | None = None


@dataclass(frozen=True)
class MbtiScores:
    introversion: int
    intuition: int
    feeling: int
    perceiving: int


@dataclass(frozen=True)
class AssessmentSubmission:
    assessment_version: str
    nickname: str
    answers: tuple[SubmittedAnswer, ...]
    mbti_scores: MbtiScores


@dataclass(frozen=True)
class ProductData:
    name: str
    noun: str
    character_code: str
    character_asset_key: str


@dataclass(frozen=True)
class UnboxingData:
    packaging_code: str
    opening_tool_code: str


@dataclass(frozen=True)
class IntroductionData:
    model_name: str
    summary: str
    version: str


@dataclass(frozen=True)
class CompatibilityData:
    compatible: tuple[str, ...]
    incompatible: tuple[str, ...]


@dataclass(frozen=True)
class RarityData:
    grade: str | None
    percentage: float | None


@dataclass(frozen=True)
class ManualData:
    introduction: IntroductionData
    core_features: tuple[str, ...]
    precautions: tuple[str, ...]
    bugs: tuple[str, ...]
    compatibility: CompatibilityData
    rarity: RarityData
    charging: tuple[str, ...]


@dataclass(frozen=True)
class SubmissionResultData:
    result_id: str | None
    persisted: bool
    mode: str
    assessment_version: str
    content_version: str
    product: ProductData
    unboxing: UnboxingData
    manual: ManualData
    provisional_fields: tuple[str, ...]


def classify_mbti(scores: MbtiScores) -> MbtiType:
    energy = "I" if scores.introversion >= 50 else "E"
    perception = "N" if scores.intuition >= 50 else "S"
    judgment = "F" if scores.feeling >= 50 else "T"
    lifestyle = "P" if scores.perceiving >= 50 else "J"
    return MbtiType(f"{energy}{perception}{judgment}{lifestyle}")
