from pakit.domain.assessment_submission import ChargingActivityData, ChargingData

BASE_CHARGING_CLAUSE: dict[str, str] = {
    "sleep_until_noon": "알람 없이 늦잠을 자며 먼저 푹 쉬고,",
    "morning_run": "몸에 땀이 날 만큼 움직이며 머리를 비우고,",
    "brunch_cafe": "느긋하게 맛있는 걸 먹으며 기분을 채우고,",
    "stay_in_bed": "아무것도 하지 않고 이불 속에서 푹 쉬고,",
    "watch_streaming": "밀린 콘텐츠를 몰아보며 현실을 잠시 잊고,",
    "self_development": "미뤄둔 일을 하나 끝내며 개운함을 채우고,",
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
    "sleep_until_noon": "알람 없는 늦잠",
    "morning_run": "아침 러닝",
    "brunch_cafe": "느긋한 브런치",
    "stay_in_bed": "이불 속 휴식",
    "watch_streaming": "콘텐츠 몰아보기",
    "self_development": "작은 성취",
}


EMERGENCY_CHARGING_KEYWORD: dict[str, str] = {
    "go_to_bed": "바로 더 쉬기",
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
        description=f"{base_description} {trigger_description}",
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
