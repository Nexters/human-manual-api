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
    "sleep_until_noon": "방해 없는 늦잠",
    "morning_run": "아침 러닝",
    "brunch_cafe": "느긋한 브런치",
    "stay_in_bed": "이불 속 휴식",
    "watch_streaming": "콘텐츠 몰아보기",
    "self_development": "작은 성취",
}


EMERGENCY_CHARGING_KEYWORD: dict[str, str] = {
    "go_to_bed": "혼자만의 시간",
    "contact_others": "친구 만나기",
    "eat_alone": "혼자 맛있는 한 끼",
    "go_for_drive": "즉흥 드라이브",
}


SUPPORT_CHARGING_KEYWORD: dict[str, str] = {
    "listen_to_me": "속마음 털어놓기",
    "take_me_out": "맛있는 거 먹기",
    "give_me_space": "혼자 생각 정리하기",
    "solve_together": "같이 답 찾기",
    "make_me_laugh": "웃으며 털어내기",
}


def build_charging(
    holiday_choice: str,
    cancellation_choice: str,
    motivation: str,
    support_preference: str,
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
                type=support_preference,
                label=SUPPORT_CHARGING_KEYWORD[support_preference],
            ),
        ),
    )
