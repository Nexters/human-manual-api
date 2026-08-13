from pakit.domain.assessment import MbtiType
from pakit.services.result_content import (
    MBTI_MOTIVATION_GROUP,
    MOTIVATION_COPY,
    MOTIVATION_DESCRIPTION,
    FeatureCopy,
)


def build_motivation_feature(answer: str, mbti: MbtiType) -> FeatureCopy:
    motivation = MOTIVATION_COPY[answer]
    group = MBTI_MOTIVATION_GROUP[mbti]
    return FeatureCopy(
        title=motivation.title,
        description=MOTIVATION_DESCRIPTION[(answer, group)],
    )
