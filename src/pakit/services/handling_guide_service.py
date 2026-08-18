from pakit.domain.assessment import MbtiType
from pakit.services.result_content import (
    AFFECTION_RECOGNITION_COPY,
    CONFLICT_SUPPORT_COPY,
    MBTI_MIDDLE_GROUP,
    RELATIONSHIP_DISTANCE_COPY,
    SUPPORT_PREFERENCE_COPY,
)


def build_handling_guide(
    *,
    support_preference: str,
    mbti: MbtiType,
    attachment_score: int,
    conflict_style: str,
    conflict_message_style: str,
    affection_style: str,
) -> tuple[str, str, str, str]:
    mbti_group = MBTI_MIDDLE_GROUP[mbti]
    distance = "close" if attachment_score >= 50 else "independent"
    return (
        SUPPORT_PREFERENCE_COPY[(support_preference, mbti_group)],
        RELATIONSHIP_DISTANCE_COPY[distance],
        CONFLICT_SUPPORT_COPY[(conflict_style, conflict_message_style)],
        AFFECTION_RECOGNITION_COPY[affection_style],
    )
