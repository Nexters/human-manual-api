from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_submission import AxisScoresData

MBTI_OVERVIEW_TAG: dict[MbtiType, str] = {
    MbtiType.INTJ: "큰그림 설계자",
    MbtiType.ISTJ: "약속 지킴이",
    MbtiType.ENTJ: "목표 직진",
    MbtiType.ESTJ: "실행 대장",
    MbtiType.INFJ: "마음 해석가",
    MbtiType.ISFJ: "조용한 챙김러",
    MbtiType.ENFJ: "응원단장",
    MbtiType.ESFJ: "분위기 케어",
    MbtiType.INFP: "감성 세계관",
    MbtiType.ISFP: "취향 수집가",
    MbtiType.ENFP: "설렘 발전기",
    MbtiType.ESFP: "흥 스위치",
    MbtiType.INTP: "생각 무한루프",
    MbtiType.ISTP: "척척 해결사",
    MbtiType.ENTP: "장난꾸러기",
    MbtiType.ESTP: "일단 해보는 편",
}

AXIS_OVERVIEW_TAG: dict[tuple[str, str], str] = {
    ("attachment", "low"): "혼자서도 잘 놀아요",
    ("attachment", "high"): "같이 있어야 든든해요",
    ("expression", "low"): "속마음은 천천히",
    ("expression", "high"): "마음은 바로 표현",
    ("routine", "low"): "도파민 MAX",
    ("routine", "high"): "익숙한 게 최고",
    ("egen", "low"): "행동으로 말해요",
    ("egen", "high"): "감정 레이더 ON",
}

AXIS_TIE_PRIORITY = ("attachment", "expression", "routine", "egen")


def build_overview_tags(mbti: MbtiType, scores: AxisScoresData) -> tuple[str, str, str]:
    axis_scores = {
        "attachment": scores.attachment,
        "expression": scores.expression,
        "routine": scores.routine,
        "egen": scores.egen,
    }
    strongest_axes = sorted(
        AXIS_TIE_PRIORITY,
        key=lambda axis: (-abs(axis_scores[axis] - 50), AXIS_TIE_PRIORITY.index(axis)),
    )[:2]
    axis_tags = tuple(
        AXIS_OVERVIEW_TAG[(axis, "high" if axis_scores[axis] >= 50 else "low")]
        for axis in strongest_axes
    )
    return (MBTI_OVERVIEW_TAG[mbti], axis_tags[0], axis_tags[1])
