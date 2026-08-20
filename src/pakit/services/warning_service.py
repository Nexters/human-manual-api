from pakit.domain.assessment import MbtiType
from pakit.services.result_content import (
    ANGER_TRIGGER_WARNING_COPY,
    COMMUNICATION_WARNING_COPY,
    MBTI_TRIGGER_WARNING_COPY,
    SOCIAL_ENERGY_WARNING_COPY,
)


def build_warnings(
    anger_trigger: str,
    mbti: MbtiType,
    expression_score: int,
    attachment_score: int,
) -> tuple[str, str, str, str]:
    """Build warnings in the stable result-page slot order."""
    if not 0 <= expression_score <= 100:
        raise ValueError("expression_score must be between 0 and 100")
    if not 0 <= attachment_score <= 100:
        raise ValueError("attachment_score must be between 0 and 100")
    expression_pole = "high" if expression_score >= 50 else "low"
    attachment_pole = "high" if attachment_score >= 50 else "low"
    return (
        COMMUNICATION_WARNING_COPY[(mbti.value[2], expression_pole)],
        SOCIAL_ENERGY_WARNING_COPY[(mbti.value[0], attachment_pole)],
        ANGER_TRIGGER_WARNING_COPY[anger_trigger],
        MBTI_TRIGGER_WARNING_COPY[mbti],
    )
