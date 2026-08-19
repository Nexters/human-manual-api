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
) -> tuple[str, str, str, str]:
    """Build warnings in the stable result-page slot order."""
    return (
        COMMUNICATION_WARNING_COPY[mbti.value[2]],
        SOCIAL_ENERGY_WARNING_COPY[mbti.value[0]],
        ANGER_TRIGGER_WARNING_COPY[anger_trigger],
        MBTI_TRIGGER_WARNING_COPY[mbti],
    )
