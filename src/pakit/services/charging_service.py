from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_submission import ChargingActivityData, ChargingData

BASE_CHARGING_CLAUSE: dict[str, str] = {
    "sleep_until_noon": "잠이 충분히 채워져야 나머지가 돌아가는 사람이에요",
    "morning_run": "에너지를 써야 오히려 채워지는 사람이에요",
    "brunch_cafe": "나한테 좋은 걸 제대로 챙겨줘야 채워지는 사람이에요",
    "stay_in_bed": "혼자 아무것도 안 하는 시간이 있어야 채워지는 사람이에요",
    "watch_streaming": "뭔가에 푹 빠져서 딴생각이 안 날 때 채워지는 사람이에요",
    "self_development": "마음의 짐을 덜어야 쉬어지는 사람이에요",
}


BASE_CHARGING_MECHANISM: dict[str, str] = {
    "sleep_until_noon": "수면 우선",
    "morning_run": "소모",
    "brunch_cafe": "감각 만족",
    "stay_in_bed": "차단",
    "watch_streaming": "몰입",
    "self_development": "청산",
}


MOTIVATION_TRIGGER_DESCRIPTION: dict[str, str] = {
    "curiosity": "새로운 구경거리가 생기면 다시 기운이 올라와요.",
    "needed_by_someone": "누군가 나를 필요로 하면 다시 힘이 나요.",
    "clear_goal": "끝낼 수 있는 목표가 보이면 다시 의욕이 생겨요.",
    "responsibility": "지켜야 할 약속이 생기면 다시 몸이 움직여요.",
    "last_chance": "놓치기 아까운 기회가 생기면 다시 활력이 돌아와요.",
    "fun": "재밌는 일이 생기면 다시 텐션이 올라와요.",
}


BASE_CHARGING_KEYWORD: dict[str, str] = {
    "sleep_until_noon": "충분한 휴식",
    "morning_run": "에너지 발산",
    "brunch_cafe": "소확행",
    "stay_in_bed": "침대와 한몸",
    "watch_streaming": "몰입",
    "self_development": "작은 성취",
}


EMERGENCY_CHARGING_KEYWORD: dict[str, str] = {
    "go_to_bed": "혼자만의 시간",
    "contact_others": "친구 만나기",
    "eat_alone": "맛있는 음식",
    "go_for_drive": "새로운 환경",
}


MBTI_CHARGING_KEYWORD: dict[MbtiType, str] = {
    MbtiType.INTJ: "관심 분야 탐구",
    MbtiType.ENTJ: "자기계발",
    MbtiType.INTP: "외부와 단절",
    MbtiType.ENTP: "호기심 충족",
    MbtiType.INFJ: "조용한 공간",
    MbtiType.ENFJ: "깊은 대화",
    MbtiType.INFP: "감성 충전",
    MbtiType.ENFP: "수다 떨기",
    MbtiType.ISTJ: "루틴 지키기",
    MbtiType.ESTJ: "정리정돈",
    MbtiType.ISTP: "관심사 몰입",
    MbtiType.ESTP: "새로운 자극",
    MbtiType.ISFJ: "익숙한 공간",
    MbtiType.ESFJ: "수다 떨기",
    MbtiType.ISFP: "독립된 공간",
    MbtiType.ESFP: "수다 떨기",
}


def build_charging(
    holiday_choice: str,
    cancellation_choice: str,
    motivation: str,
    mbti: MbtiType,
) -> ChargingData:
    base_description = BASE_CHARGING_CLAUSE[holiday_choice]
    trigger_description = MOTIVATION_TRIGGER_DESCRIPTION[motivation]
    return ChargingData(
        score=90,
        description=f"{base_description}. {trigger_description}",
        activities=(
            ChargingActivityData(
                type=holiday_choice,
                label=BASE_CHARGING_KEYWORD[holiday_choice],
            ),
            ChargingActivityData(
                type=cancellation_choice,
                label=EMERGENCY_CHARGING_KEYWORD[cancellation_choice],
            ),
            ChargingActivityData(
                type=mbti.value,
                label=MBTI_CHARGING_KEYWORD[mbti],
            ),
        ),
    )
