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
class OverviewData:
    rarity: str
    adjective: str
    noun: str
    result_name: str
    character_id: str
    image_url: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class AxisScoresData:
    attachment: int
    expression: int
    routine: int
    egen: int


@dataclass(frozen=True)
class UnboxingItemData:
    type: str
    name: str
    image_url: str
    tags: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class UnboxingKitData:
    axis_scores: AxisScoresData
    title: str
    description: str
    packaging: UnboxingItemData
    opening_tool: UnboxingItemData


@dataclass(frozen=True)
class FeatureData:
    title: str
    description: str
    tag: str = ""


@dataclass(frozen=True)
class CharacterStoryData:
    title: str
    description: str


@dataclass(frozen=True)
class ChargingActivityData:
    type: str
    label: str


@dataclass(frozen=True)
class ChargingData:
    score: int
    description: str
    activities: tuple[ChargingActivityData, ...]


@dataclass(frozen=True)
class ResultParticipantData:
    nickname: str


@dataclass(frozen=True)
class CompatibilityProfileData:
    version: str
    mbti: str
    relationship_role: str
    motivation: str
    support_preference: str
    conflict_style: str
    affection_style: str


@dataclass(frozen=True)
class CompatibleFriendData:
    badge: str
    noun: str
    character_id: str
    image_url: str
    description: str


@dataclass(frozen=True)
class SubmissionResultData:
    result_code: str
    participant: ResultParticipantData | None
    overview: OverviewData
    unboxing_kit: UnboxingKitData
    features: tuple[FeatureData, ...]
    character_story: CharacterStoryData
    can_do: tuple[str, ...]
    warnings: tuple[str, ...]
    charging: ChargingData
    compatible_friends: tuple[CompatibleFriendData, ...]
    compatibility_profile: CompatibilityProfileData | None
