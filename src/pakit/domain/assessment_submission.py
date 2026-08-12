from dataclasses import dataclass

from pakit.domain.assessment import MbtiType


@dataclass(frozen=True)
class SubmittedAnswer:
    question_id: str
    value: str | int


@dataclass(frozen=True)
class AssessmentSubmission:
    assessment_version: str
    nickname: str
    answers: tuple[SubmittedAnswer, ...]
    mbti: MbtiType


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
