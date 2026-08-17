from dataclasses import dataclass

from pakit.domain.assessment_submission import ChargingActivityData, ChargingData


@dataclass(frozen=True)
class ChargingCombinationCopy:
    description: str
    boost_label: str


BASE_CHARGING_ACTIVITY: dict[str, str] = {
    "sleep_until_noon": "늦잠으로 밀린 잠 갚기",
    "morning_run": "아침 공기 마시며 가볍게 뛰기",
    "brunch_cafe": "좋아하는 카페에서 느긋하게 브런치 먹기",
    "stay_in_bed": "이불 속에서 아무 일정 없이 늘어지기",
    "watch_streaming": "미뤄둔 콘텐츠를 마음껏 몰아보기",
    "self_development": "배우고 싶던 것에 조용히 몰입하기",
}


EMERGENCY_CHARGING_ACTIVITY: dict[str, str] = {
    "go_to_bed": "비어버린 약속만큼 푹 쉬기",
    "contact_others": "마음 맞는 친구를 불러 새 약속 만들기",
    "eat_alone": "먹고 싶던 메뉴를 혼자 느긋하게 즐기기",
    "go_for_drive": "좋아하는 음악을 틀고 낯선 길 달리기",
}


CHARGING_COMBINATION_COPY: dict[tuple[str, str], ChargingCombinationCopy] = {
    ("sleep_until_noon", "go_to_bed"): ChargingCombinationCopy(
        "일정이 비면 아쉬워하기보다 잠부터 보충해요. 누구의 속도에도 맞추지 않고 "
        "충분히 자야 배터리가 제대로 차는 타입이에요.",
        "휴대폰을 멀리 두고 알람 없이 푹 자기",
    ),
    ("sleep_until_noon", "contact_others"): ChargingCombinationCopy(
        "혼자 푹 쉬어야 기본 배터리가 차지만, 오래 혼자 있기보다는 결국 좋아하는 "
        "사람의 목소리에서 활기를 찾아요.",
        "늦잠 뒤 친한 친구와 느지막이 만나기",
    ),
    ("sleep_until_noon", "eat_alone"): ChargingCombinationCopy(
        "충전에는 잠과 맛있는 한 끼면 충분해요. 서두르지 않고 자고, 먹고 싶은 걸 "
        "내 속도로 즐길 때 컨디션이 돌아와요.",
        "늦잠 자고 혼자 좋아하는 메뉴 먹으러 가기",
    ),
    ("sleep_until_noon", "go_for_drive"): ChargingCombinationCopy(
        "몸은 충분히 쉬고 싶고 머리는 새로운 풍경으로 환기해야 해요. 푹 잔 뒤 익숙한 "
        "동네를 벗어나면 가장 빠르게 살아나요.",
        "늦잠으로 체력을 채운 뒤 해 질 무렵 드라이브하기",
    ),
    ("morning_run", "go_to_bed"): ChargingCombinationCopy(
        "가만히 쉬기보다 먼저 몸을 움직여야 머리가 맑아져요. 한 번 땀을 내고 완전히 "
        "쉬어야 몸과 생각이 함께 정리돼요.",
        "가볍게 뛴 뒤 샤워하고 낮잠 자기",
    ),
    ("morning_run", "contact_others"): ChargingCombinationCopy(
        "몸을 움직일 때 시동이 걸리고, 좋아하는 사람과 그 기운을 나눌 때 충전이 "
        "완성돼요. 함께 움직이고 웃는 시간이 잘 맞아요.",
        "친구와 산책하거나 가볍게 뛰고 맛있는 것 먹기",
    ),
    ("morning_run", "eat_alone"): ChargingCombinationCopy(
        "혼자 몸을 움직이며 복잡한 생각을 털어내고, 제대로 된 한 끼로 스스로를 "
        "챙겨요. 움직인 만큼 쉬는 맛도 커지는 타입이에요.",
        "아침 운동 뒤 혼자 제대로 된 한 끼 먹기",
    ),
    ("morning_run", "go_for_drive"): ChargingCombinationCopy(
        "바깥 공기를 마시며 움직일수록 에너지가 돌아와요. 한곳에 오래 머무르기보다 "
        "몸과 풍경을 함께 바꾸는 날에 충전이 빨라요.",
        "가볍게 뛴 뒤 차를 타고 교외로 빠져나가기",
    ),
    ("brunch_cafe", "go_to_bed"): ChargingCombinationCopy(
        "좋아하는 공간에서 느긋하게 한 끼를 먹으면 마음이 먼저 풀려요. 돌아온 뒤에는 "
        "아무 약속 없이 쉬어야 여유가 오래가요.",
        "조용한 카페에서 브런치를 먹고 집에서 푹 쉬기",
    ),
    ("brunch_cafe", "contact_others"): ChargingCombinationCopy(
        "좋은 공간과 맛있는 음식에 마음 맞는 사람까지 있으면 금세 살아나요. 거창한 "
        "일정보다 편하게 마주 앉아 웃는 시간이 고속 충전이에요.",
        "친한 사람과 가보고 싶던 카페에서 오래 수다 떨기",
    ),
    ("brunch_cafe", "eat_alone"): ChargingCombinationCopy(
        "누군가가 없어도 나를 위한 자리를 잘 만들어요. 좋아하는 공간에서 먹고 싶은 "
        "걸 천천히 즐기는 시간이 가장 깔끔한 회복이에요.",
        "혼자 카페 창가에 앉아 먹고 싶은 메뉴 천천히 즐기기",
    ),
    ("brunch_cafe", "go_for_drive"): ChargingCombinationCopy(
        "맛있는 것만큼 새로운 풍경에도 잘 충전돼요. 조금 멀더라도 마음에 드는 공간을 "
        "찾아가는 과정까지 휴식으로 만드는 타입이에요.",
        "교외의 가보고 싶던 카페까지 드라이브하기",
    ),
    ("stay_in_bed", "go_to_bed"): ChargingCombinationCopy(
        "지쳤을 때는 뭔가를 더하기보다 모든 일정을 꺼야 해요. 아무것도 하지 않아도 "
        "되는 시간이 충분해야 다시 움직일 마음이 생겨요.",
        "연락과 알림을 잠시 끄고 하루를 통째로 비워두기",
    ),
    ("stay_in_bed", "contact_others"): ChargingCombinationCopy(
        "먼저 혼자 늘어질 시간이 필요하지만, 기운이 조금 돌아오면 편한 사람을 찾아요. "
        "밖에서 애쓰기보다 익숙한 사람과 느슨하게 붙어 있을 때 회복돼요.",
        "한참 혼자 쉰 뒤 편한 친구와 동네에서 잠깐 만나기",
    ),
    ("stay_in_bed", "eat_alone"): ChargingCombinationCopy(
        "체력도 사회성도 바닥난 날에는 움직임을 최소화해야 해요. 가장 편한 자리에서 "
        "좋아하는 음식을 먹는 것만으로도 충분히 충전돼요.",
        "먹고 싶던 음식을 시켜 이불 속에서 천천히 먹기",
    ),
    ("stay_in_bed", "go_for_drive"): ChargingCombinationCopy(
        "평소에는 아무것도 하지 않는 시간이 있어야 회복돼요. 하지만 답답함까지 "
        "쌓인 날에는 익숙한 동네를 벗어날 때 훨씬 빨리 살아나요.",
        "충분히 늘어진 뒤 좋아하는 음악을 틀고 야간 드라이브하기",
    ),
    ("watch_streaming", "go_to_bed"): ChargingCombinationCopy(
        "현실 생각을 잠시 끄고 다른 이야기에 빠져드는 시간이 필요해요. 보고 싶던 걸 "
        "마음껏 본 뒤 푹 자고 나면 머릿속까지 조용해져요.",
        "좋아하는 시리즈를 보다가 졸리면 그대로 푹 자기",
    ),
    ("watch_streaming", "contact_others"): ChargingCombinationCopy(
        "재미있는 건 혼자 보는 데서 끝나지 않아요. 같은 장면에 웃어줄 사람과 감상을 "
        "주고받을 때 기분이 더 오래 살아 있어요.",
        "친구와 같은 콘텐츠를 보고 실시간으로 떠들기",
    ),
    ("watch_streaming", "eat_alone"): ChargingCombinationCopy(
        "좋아하는 이야기와 먹고 싶던 음식이 있으면 바깥 일정이 없어도 충분해요. "
        "누구에게도 방해받지 않는 몰입이 가장 편한 충전이에요.",
        "보고 싶던 콘텐츠와 좋아하는 음식 한 상 준비하기",
    ),
    ("watch_streaming", "go_for_drive"): ChargingCombinationCopy(
        "이야기 속에 푹 빠져 쉬다가도 답답해지면 풍경을 바꿔야 해요. 집에서 채운 "
        "여유를 들고 밤공기를 쐬러 나갈 때 기분이 완전히 전환돼요.",
        "한 편을 다 본 뒤 OST를 틀고 밤공기 쐬러 나가기",
    ),
    ("self_development", "go_to_bed"): ChargingCombinationCopy(
        "아무것도 안 한 날보다 작은 것이라도 해낸 날 마음이 편해져요. 목표를 조금 "
        "채운 뒤에는 미련 없이 쉬어야 다음 시동이 잘 걸려요.",
        "오늘 할 분량만 끝내고 남은 시간은 완전히 쉬기",
    ),
    ("self_development", "contact_others"): ChargingCombinationCopy(
        "배우고 성장하는 시간이 에너지가 되지만 혼자만의 성취로 끝내지는 않아요. "
        "새로 알게 된 걸 사람과 나눌 때 의욕이 더 커져요.",
        "친구와 각자 할 일에 몰입한 뒤 성과를 함께 나누기",
    ),
    ("self_development", "eat_alone"): ChargingCombinationCopy(
        "집중해서 하나를 끝내면 마음이 정돈돼요. 그 뒤 먹고 싶던 걸 천천히 즐기는 "
        "작은 보상까지 있어야 제대로 충전됐다고 느껴요.",
        "미뤄둔 일을 끝내고 혼자 좋아하는 식사로 보상하기",
    ),
    ("self_development", "go_for_drive"): ChargingCombinationCopy(
        "해야 할 일을 끝내야 마음 놓고 새로운 곳으로 움직일 수 있어요. 작은 성취 뒤에 "
        "오는 즉흥적인 외출이 머리를 가장 선명하게 환기해요.",
        "목표 하나를 끝낸 뒤 목적지 없이 드라이브하기",
    ),
}


def build_charging(holiday_choice: str, cancellation_choice: str) -> ChargingData:
    combination = CHARGING_COMBINATION_COPY[(holiday_choice, cancellation_choice)]
    return ChargingData(
        score=90,
        description=combination.description,
        activities=(
            ChargingActivityData(
                type=holiday_choice,
                label=BASE_CHARGING_ACTIVITY[holiday_choice],
            ),
            ChargingActivityData(
                type=cancellation_choice,
                label=EMERGENCY_CHARGING_ACTIVITY[cancellation_choice],
            ),
            ChargingActivityData(
                type=f"{holiday_choice}_{cancellation_choice}",
                label=combination.boost_label,
            ),
        ),
    )
