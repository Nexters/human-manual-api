from pakit.domain.assessment import MbtiType
from pakit.services.result_content import (
    ATTRACTION_GUIDE_COPY,
    CONFLICT_SUPPORT_COPY,
    MBTI_MIDDLE_GROUP,
    RELATIONSHIP_DISTANCE_COPY,
    SUPPORT_PREFERENCE_COPY,
)


def _relationship_distance_key(attachment_score: int) -> str:
    if not 0 <= attachment_score <= 100:
        raise ValueError("attachment_score must be between 0 and 100")
    if attachment_score <= 24:
        return "0_24"
    if attachment_score <= 49:
        return "25_49"
    if attachment_score <= 74:
        return "50_74"
    return "75_100"


def build_handling_guide(
    *,
    support_preference: str,
    mbti: MbtiType,
    attachment_score: int,
    conflict_style: str,
    conflict_message_style: str,
) -> tuple[str, str, str, str]:
    mbti_group = MBTI_MIDDLE_GROUP[mbti]
    distance = _relationship_distance_key(attachment_score)
    return (
        SUPPORT_PREFERENCE_COPY[(support_preference, mbti_group)],
        RELATIONSHIP_DISTANCE_COPY[distance],
        CONFLICT_SUPPORT_COPY[(conflict_style, conflict_message_style)],
        ATTRACTION_GUIDE_COPY[mbti],
    )
