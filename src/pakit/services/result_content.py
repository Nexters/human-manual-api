from dataclasses import dataclass

from pakit.domain.assessment import MbtiType

RESULT_CONTENT_VERSION = "2026-08-19.2"


@dataclass(frozen=True)
class CombinationCopy:
    title: str
    description: str


@dataclass(frozen=True)
class FeatureCopy:
    title: str
    description: str


@dataclass(frozen=True)
class CharacterStoryCopy:
    title: str
    description: str


@dataclass(frozen=True)
class MotivationCopy:
    title: str


@dataclass(frozen=True)
class UnboxingItemCopy:
    type: str
    name: str
    tags: tuple[str, str]
    reason: str


MOTIVATION_COPY: dict[str, MotivationCopy] = {
    "curiosity": MotivationCopy(
        "궁금한 건 못 참아요",
    ),
    "needed_by_someone": MotivationCopy(
        "의리가 강해요",
    ),
    "clear_goal": MotivationCopy(
        "끝은 봐야 해요",
    ),
    "responsibility": MotivationCopy(
        "약속했으면 지켜요",
    ),
    "last_chance": MotivationCopy(
        "기회는 꼭 잡아요",
    ),
    "fun": MotivationCopy(
        "재밌는 건 해야 해요",
    ),
}


MBTI_MIDDLE_GROUP: dict[MbtiType, str] = {
    MbtiType.INTJ: "NT",
    MbtiType.ENTJ: "NT",
    MbtiType.INTP: "NT",
    MbtiType.ENTP: "NT",
    MbtiType.ISTJ: "ST",
    MbtiType.ESTJ: "ST",
    MbtiType.ISTP: "ST",
    MbtiType.ESTP: "ST",
    MbtiType.INFJ: "NF",
    MbtiType.ENFJ: "NF",
    MbtiType.INFP: "NF",
    MbtiType.ENFP: "NF",
    MbtiType.ISFJ: "SF",
    MbtiType.ESFJ: "SF",
    MbtiType.ISFP: "SF",
    MbtiType.ESFP: "SF",
}


MBTI_RARITY_COPY: dict[MbtiType, str] = {
    MbtiType.INFJ: "상위 1.5%",
    MbtiType.ENTJ: "상위 1.8%",
    MbtiType.INTJ: "상위 2.1%",
    MbtiType.ENFJ: "상위 2.5%",
    MbtiType.ENTP: "상위 3.2%",
    MbtiType.INTP: "상위 3.3%",
    MbtiType.ESTP: "상위 4.3%",
    MbtiType.INFP: "상위 4.4%",
    MbtiType.ISTP: "상위 5.4%",
    MbtiType.ENFP: "상위 8.1%",
    MbtiType.ESFP: "상위 8.5%",
    MbtiType.ESTJ: "상위 8.7%",
    MbtiType.ISFP: "상위 8.8%",
    MbtiType.ISTJ: "상위 11.6%",
    MbtiType.ESFJ: "상위 12.3%",
    MbtiType.ISFJ: "상위 13.5%",
}


SUPPORT_PREFERENCE_COPY: dict[tuple[str, str], str] = {
    ("listen_to_me", "NT"): "내 말의 표면만 보지 말고, 왜 이런 말을 하는지까지 이해해주세요",
    ("listen_to_me", "ST"): "무슨 일이 있었는지 처음부터 차근차근 들어주세요",
    ("listen_to_me", "NF"): "해결책보다 지금 느끼는 마음부터 들어주세요",
    ("listen_to_me", "SF"): "말이 정리되지 않아도 중간에 판단하지 말고 끝까지 들어주세요",
    ("take_me_out", "NT"): "생각이 막히면 새로운 장소로 데려가주세요",
    ("take_me_out", "ST"): "왜 그러냐고 묻는 대신, 늘 가던 곳에 같이 가서 시간 보내주세요",
    ("take_me_out", "NF"): "마음이 답답해 보이면 내가 좋아할 만한 곳으로 함께 바람 쐬러 가주세요",
    ("take_me_out", "SF"): "무슨 일인지 캐묻기보다 좋아하는 걸 먹으러 슬쩍 불러내주세요",
    ("give_me_space", "NT"): "생각이 정리될 때까지 혼자 생각할 시간을 주세요",
    ("give_me_space", "ST"): "괜찮냐고 계속 묻기보다 평소처럼 지내주세요",
    ("give_me_space", "NF"): "내가 마음을 꺼낼 준비가 됐을 때 알아봐주세요",
    ("give_me_space", "SF"): "말은 안 걸어도 좋으니, 곁에 있다는 표시만 남겨주세요",
    ("solve_together", "NT"): "막힌 이유부터 함께 정리해주세요",
    ("solve_together", "ST"): "지금 할 일부터 함께 처리해주세요",
    ("solve_together", "NF"): "마음부터 확인하고 해결책을 찾아주세요",
    ("solve_together", "SF"): "당장 필요한 것부터 함께 챙겨주세요",
    ("make_me_laugh", "NT"): "복잡한 생각에서 잠깐 빠져나오게 엉뚱한 이야기를 던져주세요",
    ("make_me_laugh", "ST"): "길게 위로하기보다 바로 웃을 수 있는 사진이나 영상을 보내주세요",
    ("make_me_laugh", "NF"): "내가 좋아할 만한 농담으로 무거워진 마음을 살짝 풀어주세요",
    ("make_me_laugh", "SF"): "같이 웃으며 무거운 분위기를 바꿔주세요",
}


RELATIONSHIP_DISTANCE_COPY: dict[str, str] = {
    "close": "별일 없어도 자주 안부를 묻고 곁에 있어주세요",
    "independent": "연락이 뜸해도 각자의 시간을 믿어주세요",
}


CONFLICT_SUPPORT_COPY: dict[str, str] = {
    "hint_and_wait": "평소보다 말수가 줄면 모른 척 넘기지 말고 먼저 물어봐주세요",
    "resolve_immediately": "서운한 일은 피하지 말고 바로 이야기해주세요",
}


AFFECTION_RECOGNITION_COPY: dict[str, str] = {
    "express_with_words": "말과 리액션에 담긴 애정을 알아봐주세요",
    "express_with_actions": "말없이 챙기는 행동을 애정으로 알아봐주세요",
}


PROTECTED_TIME_WARNING_COPY: dict[str, str] = {
    "after_waking": "잠이 덜 깨면 첫 반응이 무뚝뚝해요",
    "during_meal": "밥 먹는 흐름이 끊기면 바로 예민해져요",
    "after_work": "퇴근 직후 할 일이 쏟아지면 바로 방전돼요",
    "late_night": "새벽 감성을 끊으면 괜히 더 예민해져요",
}


ANGER_TRIGGER_WARNING_COPY: dict[str, str] = {
    "rush": "재촉받으면 하려던 마음도 사라져요",
    "interrupt": "말을 끊으면 남은 이야기도 삼켜버려요",
    "take_food": "음식을 허락 없이 가져가면 한입보다 큰 서운함이 남아요",
    "arrive_late": "늦고도 태연하면 기다린 만큼 신뢰가 깎여요",
    "nag": "잔소리가 반복되면 귀부터 닫아요",
    "change_plan": "계획이 갑자기 바뀌면 기분부터 틀어져요",
}


SOCIAL_ENERGY_WARNING_COPY: dict[str, str] = {
    "E": "내 얘기에 반응이 없으면 신나서 하던 이야기도 금세 재미없어져요",
    "I": "혼자 정리할 틈이 없으면 대답이 점점 짧아져요",
}


COMMUNICATION_WARNING_COPY: dict[str, str] = {
    "T": "해결하려고 꺼낸 말에 차갑다는 말이 돌아오면 억울해져요",
    "F": "속마음을 꺼냈는데 유난이라는 말이 돌아오면 오래 마음에 남아요",
}


MOTIVATION_DESCRIPTION: dict[tuple[str, str], str] = {
    ("curiosity", "NT"): "궁금한 건 검색만으로 넘기지 않고, 원리와 다른 가능성까지 직접 확인해요.",
    ("curiosity", "ST"): "궁금한 건 설명만 듣지 않고, 직접 보고 해봐야 믿고 넘어가요.",
    ("curiosity", "NF"): "궁금한 건 정보만 찾지 않고, 그 안의 의미와 사람 이야기까지 들여다봐요.",
    ("curiosity", "SF"): "궁금한 건 직접 경험해보고, 그 순간의 느낌까지 확인해야 마음이 놓여요.",
    ("needed_by_someone", "NT"): (
        "누가 나를 꼭 찾으면 문제부터 파악하고, 가장 확실한 해결책을 들고 나서요."
    ),
    ("needed_by_someone", "ST"): (
        "누가 나를 꼭 찾으면 말보다 몸부터 움직여, 필요한 일을 바로 처리해요."
    ),
    ("needed_by_someone", "NF"): (
        "누가 나를 꼭 찾으면 왜 힘든지부터 살피고, 혼자 두지 않으려고 나서요."
    ),
    ("needed_by_someone", "SF"): (
        "누가 나를 꼭 찾으면 하던 걸 멈추고, 당장 필요한 것부터 챙겨 나서요."
    ),
    ("clear_goal", "NT"): (
        "시작한 일은 끝을 봐야 하는 편이라, 마무리 전에 더 나은 방법이 없는지 한 번 더 따져봐요."
    ),
    ("clear_goal", "ST"): (
        "시작한 일은 끝을 봐야 하는 편이라, 정한 순서대로 밀어붙여 기어이 끝을 내요."
    ),
    ("clear_goal", "NF"): (
        "시작한 일은 끝을 봐야 하는 편이라, 지칠 때도 처음 마음을 떠올리며 밀고 나가요."
    ),
    ("clear_goal", "SF"): (
        "시작한 일은 끝을 봐야 하는 편이라, 하나씩 지워가는 뿌듯함으로 마지막까지 채워요."
    ),
    ("responsibility", "NT"): (
        "하기로 한 일은 방법을 다시 짜서라도, 결과가 나올 때까지 자기 몫을 해요."
    ),
    ("responsibility", "ST"): "하기로 한 일은 귀찮아도 빠지지 않고, 맡은 순서대로 끝까지 해요.",
    ("responsibility", "NF"): "하기로 한 일은 누가 기다리는지 알기에, 마음을 다해 끝까지 지켜요.",
    ("responsibility", "SF"): (
        "하기로 한 일은 주변에 필요한 것까지 살피며, 자기 몫을 끝까지 챙겨요."
    ),
    ("last_chance", "NT"): (
        "지금뿐인 기회는 가능성을 빠르게 따져보고, 잡을 가치가 있으면 바로 움직여요."
    ),
    ("last_chance", "ST"): "지금뿐인 기회는 오래 재지 않고, 놓치기 전에 몸부터 움직여요.",
    ("last_chance", "NF"): "지금뿐인 기회는 오래 남을 의미를 느끼면, 미루던 마음도 접고 움직여요.",
    ("last_chance", "SF"): "지금뿐인 기회는 그 순간의 끌림을 따라, 직접 경험하는 쪽을 골라요.",
    ("fun", "NT"): "재밌는 일이 시작되면 구경만 하지 않고, 더 재밌게 만들 방법까지 보태요.",
    ("fun", "ST"): "재밌는 일이 시작되면 오래 고민하지 않고, 지금 즐길 수 있는 자리부터 찾아가요.",
    ("fun", "NF"): "재밌는 일이 시작되면 마음 맞는 사람도 불러, 함께 웃을 판에 합류해요.",
    ("fun", "SF"): "재밌는 일이 시작되면 그 순간의 분위기를 타고, 같이 있는 사람까지 챙겨요.",
}


RELATIONSHIP_ROLE_COPY: dict[tuple[str, str], FeatureCopy] = {
    ("decision", "organize_and_coordinate"): FeatureCopy(
        "결정 조율자",
        "친구들 의견이 갈리면 기준과 공통점을 정리해 모두가 납득할 방향을 만드는 사람이에요.",
    ),
    ("decision", "lift_mood"): FeatureCopy(
        "말문 트기왕",
        "의견이 안 모여 답답해질 때 농담 한마디로 다시 말문을 트는 사람이에요.",
    ),
    ("decision", "make_it_happen"): FeatureCopy(
        "실행 총무",
        "아이디어가 나오면 누가 언제 움직일지 정해 결정을 실제 행동으로 옮기는 사람이에요.",
    ),
    ("decision", "care_for_others"): FeatureCopy(
        "의견 챙김왕",
        "말 없는 친구에게도 원하는 걸 물어보고 누구도 빠지지 않는 선택을 만드는 사람이에요.",
    ),
    ("worries", "organize_and_coordinate"): FeatureCopy(
        "고민 길잡이",
        "친구의 생각이 엉켜 있으면 상황을 정리하고 지금 할 수 있는 일부터 짚어주는 사람이에요.",
    ),
    ("worries", "lift_mood"): FeatureCopy(
        "기분 환기담당",
        "고민은 가볍게 넘기지 않으면서도 웃을 틈을 만들어주는 사람이에요.",
    ),
    ("worries", "make_it_happen"): FeatureCopy(
        "현실 해결사",
        "친구가 고민만 맴돌면 당장 해볼 수 있는 방법을 찾아 함께 움직이는 사람이에요.",
    ),
    ("worries", "care_for_others"): FeatureCopy(
        "맞춤 위로왕",
        "서두르지 않고 이야기를 들어주며 그 친구에게 필요한 방식으로 위로하는 사람이에요.",
    ),
    ("hangout", "organize_and_coordinate"): FeatureCopy(
        "모임 조율대장",
        "하고 싶은 게 제각각이어도 모두가 즐기도록 장소와 순서를 정리하는 사람이에요.",
    ),
    ("hangout", "lift_mood"): FeatureCopy(
        "분위기 메이커",
        "친구들이 모이면 먼저 웃길 거리를 꺼내 그 자리를 신나게 만드는 사람이에요.",
    ),
    ("hangout", "make_it_happen"): FeatureCopy(
        "번개 추진왕",
        "재밌는 얘기가 나오면 다음으로 미루지 않고 바로 사람을 모아 움직이는 사람이에요.",
    ),
    ("hangout", "care_for_others"): FeatureCopy(
        "모임 챙김대장",
        "누구 하나 겉돌지 않게 살피고 모두가 편하게 즐기도록 챙기는 사람이에요.",
    ),
    ("information", "organize_and_coordinate"): FeatureCopy(
        "정보 정리왕",
        "정보가 많거나 서로 엇갈려도 확인된 사실과 핵심부터 정리해주는 사람이에요.",
    ),
    ("information", "lift_mood"): FeatureCopy(
        "설명 예능인",
        "어려운 내용도 비유와 농담을 섞어 재미있게 이해시키는 사람이에요.",
    ),
    ("information", "make_it_happen"): FeatureCopy(
        "실행 설계자",
        "찾은 정보를 그래서 뭘 하면 되는지까지 정리해주는 사람이에요.",
    ),
    ("information", "care_for_others"): FeatureCopy(
        "맞춤 정보통",
        "친구의 상황을 살펴 그 사람에게 꼭 필요한 정보만 골라 알려주는 사람이에요.",
    ),
}


EMOTIONAL_PROCESSING_COPY: dict[tuple[str, str], FeatureCopy] = {
    ("explore", "egen"): FeatureCopy(
        "혼자 곱씹어요",
        "마음이 복잡하면 바로 꺼내기보다 충분히 들여다보고, 준비가 되면 차근차근 말해요.",
    ),
    ("direct", "egen"): FeatureCopy(
        "서운하면 직구",
        "서운한 건 쌓아두지 않고 바로 꺼내, 서로의 마음을 확인해야 풀려요.",
    ),
    ("explore", "teto"): FeatureCopy(
        "생각정리 먼저",
        "마음이 복잡할수록 먼저 상황을 정리하고, 말보다 필요한 행동으로 풀어내요.",
    ),
    ("direct", "teto"): FeatureCopy(
        "바로 해결해요",
        "걸리는 건 바로 확인하고, 해결할 일을 끝낸 뒤 다음 행동으로 넘어가요.",
    ),
}


MBTI_STRENGTH_COPY: dict[MbtiType, FeatureCopy] = {
    MbtiType.INTJ: FeatureCopy(
        "큰그림을 봐요", "흩어진 조각을 연결해 전체가 맞아떨어지는 구조를 봐요."
    ),
    MbtiType.ISTJ: FeatureCopy("끝까지 해내요", "맡은 일은 빠뜨리는 것 없이 마지막 칸까지 채워요."),
    MbtiType.ENTJ: FeatureCopy(
        "목표를 이뤄요", "멀리 있는 목표도 사람과 자원을 모아 앞으로 끌고 가요."
    ),
    MbtiType.ESTJ: FeatureCopy(
        "순서대로 해요", "엉킨 상황에서도 역할과 순서를 빠르게 다시 세워요."
    ),
    MbtiType.INFJ: FeatureCopy(
        "마음을 읽어요", "겉으로 한 말보다 그 안에 숨은 의도와 마음을 먼저 읽어요."
    ),
    MbtiType.ISFJ: FeatureCopy(
        "내편은 지켜요", "한번 자기 사람으로 받아들이면 필요한 순간을 지켜줘요."
    ),
    MbtiType.ENFJ: FeatureCopy("용기를 줘요", "상대도 몰랐던 장점을 발견해 스스로 보게 해줘요."),
    MbtiType.ESFJ: FeatureCopy(
        "모두를 챙겨요", "작은 안부와 배려로 사람 사이가 부드럽게 돌아가게 해요."
    ),
    MbtiType.INFP: FeatureCopy(
        "소신을 지켜요", "남의 기준보다 자신이 진짜 중요하게 여기는 것을 지켜요."
    ),
    MbtiType.ISFP: FeatureCopy(
        "감각을 믿어요", "말로 설명하기 전에도 자신에게 맞는 결을 알아봐요."
    ),
    MbtiType.ENFP: FeatureCopy(
        "가능성을 봐요", "사람과 상황에서 아직 펼쳐지지 않은 재미를 먼저 발견해요."
    ),
    MbtiType.ESFP: FeatureCopy(
        "지금을 즐겨요", "지금 이 순간의 즐거움을 찾아 주변 사람과 함께 나눠요."
    ),
    MbtiType.INTP: FeatureCopy(
        "원리를 따져요", "당연해 보이는 것도 작동 원리를 알 때까지 파고들어요."
    ),
    MbtiType.ISTP: FeatureCopy(
        "직접 해결해요", "설명만 늘이기보다 직접 만져 가장 빠른 해결책을 찾아요."
    ),
    MbtiType.ENTP: FeatureCopy(
        "다르게 봐요", "모두가 당연하다고 넘긴 곳에서 다른 가능성을 발견해요."
    ),
    MbtiType.ESTP: FeatureCopy(
        "기회를 잡아요", "눈앞의 변화를 빠르게 읽고 잡을 수 있을 때 움직여요."
    ),
}


CHARACTER_STORY_COPY: dict[MbtiType, CharacterStoryCopy] = {
    MbtiType.INTJ: CharacterStoryCopy(
        "흩어진 면이 맞아떨어질 때까지 돌아가는 큐브",
        (
            "큐브는 섞여 있을수록 아무렇게나 돌리지 않아요. 지금 맞추는 한 면이 다음 면에 어떤 "
            "영향을 줄지 머릿속으로 그린 뒤, 가장 정확한 순서로 움직이죠. 복잡한 상황에서도 전체 "
            "구조를 보고 자기만의 답을 완성하는 모습이 닮아 큐브가 도착했습니다."
        ),
    ),
    MbtiType.ISTJ: CharacterStoryCopy(
        "맡은 임무는 마지막 칸까지 수행하는 로봇",
        (
            "로봇은 기분에 따라 순서를 건너뛰거나 약속된 동작을 빼먹지 않아요. 해야 할 일을 "
            "정확히 기억하고, 눈앞의 한 단계씩 처리해 결국 임무를 끝내죠. 말보다 꾸준한 결과로 "
            "신뢰를 쌓는 모습이 닮아 로봇이 도착했습니다."
        ),
    ),
    MbtiType.ENTJ: CharacterStoryCopy(
        "목표가 생기면 길부터 만들어버리는 불도저",
        (
            "불도저는 길이 없다는 말을 멈춰야 할 이유로 듣지 않아요. 목적지를 정하면 흩어진 힘을 "
            "한곳에 모으고, 앞을 막는 문제부터 밀어내며 길을 만들죠. 큰 목표를 현실의 결과로 "
            "바꾸는 추진력이 닮아 불도저가 도착했습니다."
        ),
    ),
    MbtiType.ESTJ: CharacterStoryCopy(
        "정해진 순서를 건너뛰지 않고 현장을 책임지는 헬리콥터",
        (
            "헬리콥터는 급한 상황일수록 점검 순서를 먼저 밟아요. 늘 하던 방식으로 상태를 확인한 뒤 "
            "필요한 자리에 정확히 내려가, 누가 무엇을 언제 할지 분명하게 정리하죠. 검증된 방식으로 "
            "현장을 맡아 끝까지 책임지는 모습이 닮아 헬리콥터가 도착했습니다."
        ),
    ),
    MbtiType.INFJ: CharacterStoryCopy(
        "겉보다 안쪽에 더 많은 이야기가 든 비밀상자",
        (
            "비밀상자는 겉만 훑어본 사람에게 내용물을 쉽게 보여주지 않아요. 조용히 오래 들여다보고 "
            "알맞은 열쇠를 찾은 사람에게만 안쪽의 의미를 한 겹씩 내어주죠. 말보다 마음속 의도와 "
            "이야기를 깊이 읽는 모습이 닮아 비밀상자가 도착했습니다."
        ),
    ),
    MbtiType.ISFJ: CharacterStoryCopy(
        "말없이 곁을 지키며 오래 닳아가는 테디베어",
        (
            "테디베어는 가장 화려하게 놀아주는 장난감은 아니지만, 힘든 밤이면 늘 같은 자리에서 "
            "기다리고 있어요. 오래 안고 지낼수록 손때와 추억이 쌓여 쉽게 바꿀 수 없는 존재가 되죠. "
            "자기 사람의 곁을 꾸준히 지키는 모습이 닮아 테디베어가 도착했습니다."
        ),
    ),
    MbtiType.ENFJ: CharacterStoryCopy(
        "사람을 태우고 더 나은 곳으로 향하는 기차",
        (
            "기차는 혼자 빠르게 달리는 대신 여러 사람을 한 칸씩 태우고 같은 목적지로 나아가요. "
            "뒤처진 사람이 없는지 살피면서도, 모두가 지금보다 먼 곳에 닿도록 힘차게 이끌죠. 다른 "
            "사람의 가능성을 발견하고 함께 성장하는 모습이 닮아 기차가 도착했습니다."
        ),
    ),
    MbtiType.ESFJ: CharacterStoryCopy(
        "사람이 모이면 온기를 따라주는 티포트",
        (
            "티포트는 혼자 뜨거운 채로 있기보다 잔마다 알맞게 온기를 나눠요. 누군가의 잔이 비지는 "
            "않았는지 살피고, 어색한 자리도 천천히 대화가 흐르는 자리로 만들죠. 작은 배려로 사람 "
            "사이를 따뜻하게 이어주는 모습이 닮아 티포트가 도착했습니다."
        ),
    ),
    MbtiType.INFP: CharacterStoryCopy(
        "아무렇게나 다룰 수 없는 자기만의 결, 쿠크다스",
        (
            "쿠크다스는 단단한 척 버티기보다 섬세한 결을 그대로 가지고 있어요. 작은 자극도 깊이 "
            "느끼지만, 그만큼 평범한 순간에서 남들이 놓친 의미와 상상을 발견하죠. 여린 마음을 "
            "숨기지 않고 자기만의 소중한 기준을 지키는 모습이 닮아 쿠크다스가 도착했습니다."
        ),
    ),
    MbtiType.ISFP: CharacterStoryCopy(
        "세상의 속도보다 내 리듬을 지키는 침대",
        (
            "침대는 더 빨리 달리라고 재촉하지 않아요. 몸과 마음이 편안해지는 온도와 자세를 찾아, "
            "자기 속도로 다시 움직일 힘을 돌려주죠. 경쟁에 휩쓸리기보다 지금의 감각과 평온을 "
            "소중히 누리는 모습이 닮아 침대가 도착했습니다."
        ),
    ),
    MbtiType.ENFP: CharacterStoryCopy(
        "새로운 바람을 만나면 더 높이 오르는 연",
        (
            "연은 바람의 방향이 바뀔 때마다 떨어질 걱정보다 어디까지 날아갈 수 있을지 먼저 "
            "궁금해해요. 자유롭게 움직이면서도 손에 쥔 실을 통해 사람과 계속 연결되어 있죠. 새로운 "
            "가능성을 발견하고 함께 설레는 쪽으로 날아가는 모습이 닮아 연이 도착했습니다."
        ),
    ),
    MbtiType.ESFP: CharacterStoryCopy(
        "건드리는 곳마다 분위기가 살아나는 실로폰",
        (
            "실로폰은 누군가 한 음을 두드리는 순간 바로 밝은 소리로 대답해요. 서로 다른 음도 "
            "이어지면 어느새 모두가 따라 하고 싶은 리듬이 되죠. 지금의 즐거움을 크게 울려 주변 "
            "사람까지 신나게 만드는 모습이 닮아 실로폰이 도착했습니다."
        ),
    ),
    MbtiType.INTP: CharacterStoryCopy(
        "원리를 알아야 비로소 초점이 잡히는 망원경",
        (
            "망원경은 눈에 대기만 한다고 바로 보이지 않아요. 렌즈가 어떤 원리로 상을 잡는지 "
            "이해하고 몇 번이고 직접 조절해야 흐릿하던 것이 선명해지죠. 남들이 당연하게 넘긴 것도 "
            "직접 뜯어보고 원리를 이해해야 넘어가는 모습이 닮아 망원경이 도착했습니다."
        ),
    ),
    MbtiType.ISTP: CharacterStoryCopy(
        "문제가 생기면 필요한 도구부터 꺼내는 공구함",
        (
            "공구함은 긴 설명보다 지금 문제에 맞는 도구가 무엇인지 알고 있어요. 직접 열어보고, "
            "조이고, 다시 움직여보며 가장 간단한 해결책을 찾아내죠. 간섭 없이 자기 손으로 기술을 "
            "익히고 문제를 해결하는 모습이 닮아 공구함이 도착했습니다."
        ),
    ),
    MbtiType.ENTP: CharacterStoryCopy(
        "한번 돌기 시작하면 새로운 판을 만드는 팽이",
        (
            "팽이는 얌전히 세워두는 순간보다 힘껏 돌기 시작할 때 진짜 재미가 보여요. 정해진 "
            "자리만 맴돌지 않고 이쪽저쪽 부딪치며, 예상하지 못한 방향에서도 자기 균형을 찾아내죠. "
            "당연한 답에 멈추지 않고 새로운 가능성을 시험하는 모습이 닮아 팽이가 도착했습니다."
        ),
    ),
    MbtiType.ESTP: CharacterStoryCopy(
        "길이 보이면 먼저 달려가 확인하는 RC카",
        (
            "RC카는 완벽한 지도를 그릴 때까지 출발을 미루지 않아요. 앞에 길이 보이면 먼저 "
            "달려가고, 급한 모퉁이도 그 자리에서 방향을 틀며 빠져나오죠. 눈앞의 기회를 빠르게 읽고 "
            "몸으로 부딪쳐 자기 것으로 만드는 모습이 닮아 RC카가 도착했습니다."
        ),
    ),
}


COMBINATION_COPY: dict[tuple[str, str], CombinationCopy] = {
    ("A1", "B1"): CombinationCopy(
        title="애정도 안부도 정기배송으로 오는 사람",
        description=(
            '"밥 먹었어?"로 하루를 열고, 좋아하면 프사부터 바뀌어서 온 동네가 다 알아요. '
            "어제도 오늘도 같은 시간에 연락하고, 같은 방식으로 꾸준히 챙기죠. 과하다는 말도 "
            "듣지만 이 사람 옆자리는 한겨울에도 안 식어요."
        ),
    ),
    ("A1", "B2"): CombinationCopy(
        title="팩트로 때리고 밥으로 치료하는 사람",
        description=(
            "고민을 털어놓으면 위로 대신 해결책 세 줄 요약이 먼저 도착해요. 근데 정리가 끝나면 "
            '"밥은 먹었냐"며 숟가락부터 쥐여주죠. 말은 직구, 챙김은 루틴 잔소리의 총량이 곧 '
            "애정의 총량인 타입이에요."
        ),
    ),
    ("A1", "B3"): CombinationCopy(
        title="음소거가 안 되는 사람",
        description=(
            "신나는 일이 생기면 3초 안에 단톡방이 먼저 알고, 좋아하는 사람은 새벽 2시 카톡 "
            "폭탄으로 알게 돼요. 재밌는 걸 발견하면 혼자 못 있고 바로 끌고 가죠. 텐션도 애정도 "
            "볼륨 조절이 안 되는데 그 시끄러움이 다정해서 미워할 수가 없어요."
        ),
    ),
    ("A1", "B4"): CombinationCopy(
        title="브레이크가 고장 난 게 아니라 원래 없는 사람",
        description=(
            '"우리 이거 하자"가 곧 출발 신호예요. 꽂히면 그날 연락처를 받아내고, 좋다 싶으면 '
            "주말 여행이 이미 예약돼 있죠. 속도에 놀란 상대가 정신 차려 보면 어느새 옆에서 같이 "
            "웃고 있는 동반 탑승형 추진력입니다."
        ),
    ),
    ("A2", "B1"): CombinationCopy(
        title="평소엔 절전, 중요한 순간엔 풀가동되는 사람",
        description=(
            "평소엔 각자 잘 살자 주의라 연락이 뜸해요. 근데 중요한 날짜, 힘든 시기, 필요한 순간은 "
            "귀신같이 기억하고 조용히 나타나죠. 애정을 상시 방송하지 않을 뿐 필요한 말은 "
            "정확하게, 챙길 건 빠짐없이 하는 저전력 고효율 타입이에요."
        ),
    ),
    ("A2", "B2"): CombinationCopy(
        title="리액션은 'ㅇㅇ' 두 글자, 신뢰도는 국밥인 사람",
        description=(
            "할 말은 하고, 선은 지키고, 한다고 한 건 무조건 해요. 화려한 이벤트는 없지만 "
            "실망시킨 적도 없죠. 정해둔 흐름이 갑자기 바뀌는 것만 조심하면 10년을 옆에 둬도 "
            "질리지 않는 검증된 스테디셀러입니다."
        ),
    ),
    ("A2", "B3"): CombinationCopy(
        title="화려하게 나타나 분위기 다 살리고 쿨하게 사라지는 사람",
        description=(
            '모임에선 제일 빛나는데 끝나면 제일 먼저 증발해요. "언제 한번 밥 먹자"를 3만 번 '
            "말하지만, 그 언젠가가 진짜로 오면 세상 누구보다 재밌게 놀아주죠. 가까움과 자유를 "
            "동시에 굴리는 기간 한정 팝업 같은 사람이에요."
        ),
    ),
    ("A2", "B4"): CombinationCopy(
        title="고백도 통보로 하는 사람",
        description=(
            "하고 싶은 말은 직구로 하고, 하고 싶은 일은 이미 실행 중이에요. "
            '"어디야"라고 물으면 높은 확률로 다른 도시에 있고, 어제 말한 계획이 오늘 스토리로 '
            "인증되죠. 잡히지 않는 대신 숨기지도 않아서 예측은 포기하고 구경하는 재미로 곁에 "
            "있게 되는 타입입니다."
        ),
    ),
    ("A3", "B1"): CombinationCopy(
        title="안 친한 척하면서 안부는 꼬박꼬박 챙기는 사람",
        description=(
            "좋아하는 티는 죽어도 안 내는데, 행동이 이미 다 말하고 있어요. 지나가듯 한 말을 "
            "기억했다가 슬쩍 내밀고, 익숙해진 옆자리는 조용히 지키죠. 가까워지는 덴 느려도 한번 "
            "데워지면 안 식는 은은한 온돌 타입이에요."
        ),
    ),
    ("A3", "B2"): CombinationCopy(
        title="말수는 아껴도 자리는 안 뜨는 사람",
        description=(
            "표현도 짧고 속마음 꺼내는 것도 느린데, 자리는 안 떠요. 무심해 보인다고요? 지금 우산 "
            "씌워주고 집 앞까지 같이 걷고 있는 사람이 이 사람이에요. 말수와 애정이 반비례하는 "
            "대표 사례입니다."
        ),
    ),
    ("A3", "B3"): CombinationCopy(
        title="서프라이즈 준비하다 본인이 먼저 들키는 사람",
        description=(
            "조용히 좋아하는 중인데, 신나면 숨긴 게 다 티 나요. 3년 전 게시물에 좋아요를 "
            "눌러버리고, 몰래 준비한 선물은 포장 전에 들통나죠. 위장은 늘 실패하는데 그 어설픈 "
            "들킴이 귀여워서 다들 모른 척해주는 타입이에요."
        ),
    ),
    ("A3", "B4"): CombinationCopy(
        title="겉은 얌전한데 속으론 별짓 다 해본 순정파",
        description=(
            "조용해 보이는데 혼자 안 해본 게 없어요. 상상은 오만 번, 실행은 마음 정한 그날 예상 "
            "밖 스케일로 하죠. 아는 사람만 아는 반전이 매력인데 정작 마음 준 사람 옆에는 의외로 "
            "붙박이입니다."
        ),
    ),
    ("A4", "B1"): CombinationCopy(
        title="낯가림 3개월, 그 뒤로는 수다 10년인 사람",
        description=(
            "데워지는 데 오래 걸리는데, 한번 데워지면 안 식어요. 이 사람이 먼저 농담하고 말 "
            "많아지는 모습을 본 사람은 소수 정예뿐이죠. 재촉하지 않고 기다려준 사람에게만 열리는 "
            "슬로우쿠커 타입이에요."
        ),
    ),
    ("A4", "B2"): CombinationCopy(
        title="연락은 뜸해도 관계는 안 끊기는 사람",
        description=(
            "연락 텀은 길고 반응은 최소인데, 이상하게 관계는 안 끊겨요. 1년 만에 연락해도 어제 본 "
            "것처럼 받아주고, 필요할 때 보면 늘 그 자리에 있죠. 유행도 변덕도 없는 소장각 "
            "클래식입니다."
        ),
    ),
    ("A4", "B3"): CombinationCopy(
        title="잠수 타다 갑자기 나타나서 세상 다정한 사람",
        description=(
            "혼자 여기저기 다니느라 연락은 어려운데, 만나면 그동안 발견한 걸 보따리째 풀어놔요. "
            "새로운 건 먼저 혼자 충분히 겪어보고, 진짜 좋은 것만 골라서 곁을 내주죠. 드물게 "
            "출몰해서 더 반가운 타입이에요."
        ),
    ),
    ("A4", "B4"): CombinationCopy(
        title="과정은 비공개, 결과로 증명하는 사람",
        description=(
            '말없이 혼자 지르고, 물어보면 "그냥 뭐"가 답의 전부예요. 근데 어느 날 보면 새로 '
            "시작한 취미가 이미 프로급이죠. 파악 불가라 다들 포기했지만 간섭 없이 지켜봐 주는 "
            "사람에게는 의외로 먼저 문을 여는 자유인입니다."
        ),
    ),
}


PACKAGING_COPY: dict[str, UnboxingItemCopy] = {
    "A1": UnboxingItemCopy(
        type="fragile_box",
        name="취급주의 상자",
        tags=("직진형", "밀착형"),
        reason=(
            "이 상자는 겉면부터 조용할 생각이 없어요. 좋으면 좋다, 서운하면 서운하다 마음이 "
            "생기는 즉시 밖으로 나오고, 좋아하는 사람 옆엔 이미 가서 앉아 있거든요. 포장 "
            "담당자는 취급주의 한 장이면 충분할 줄 알았지만, 상자를 돌릴 때마다 다른 면에서 "
            "마음이 툭툭 튀어나와 결국 앞뒤옆면을 스티커로 도배했어요. 뭐가 들었는지 겉만 봐도 "
            "다 아는, 취급주의 상자입니다."
        ),
    ),
    "A2": UnboxingItemCopy(
        type="minimal_box",
        name="미니멀 상자",
        tags=("직진형", "거리조절형"),
        reason=(
            "하고 싶은 말은 바로바로 직구로 날려서, 친구나 연인이 가끔 놀랄 때가 있어요. 그렇다고 "
            "늘 붙어 있어야 가깝다고 느끼는 타입은 아니에요. 각자의 하루를 잘 보내다 만나도 "
            "충분하거든요. 포장 담당자가 리본과 하트 스티커를 붙여봤지만 죄다 미끄러져 떨어졌고, "
            "끝까지 남은 건 할 말이 또박또박 적힌 라벨 한 장뿐이었어요. 덧붙일 것 없이 완성된, "
            "미니멀 상자입니다."
        ),
    ),
    "A3": UnboxingItemCopy(
        type="matryoshka_box",
        name="마트료시카 상자",
        tags=("탐색형", "밀착형"),
        reason=(
            "좋아하는 마음을 바로 보여주진 못해요. 티 안 나게 챙기고 속마음은 몇 번을 접어 안쪽에 "
            "넣지만, 한번 곁을 준 사람 옆엔 조용히 오래 머물러요. 포장 담당자가 뚜껑을 열자 "
            "안에서 상자가 또 나왔고, 안쪽으로 갈수록 메모와 하트가 빼곡했어요. 서두르지 않고 한 "
            "겹씩 열어주는 사람만 알맹이까지 만나는, 마트료시카 상자입니다."
        ),
    ),
    "A4": UnboxingItemCopy(
        type="locked_box",
        name="자물쇠 상자",
        tags=("탐색형", "거리조절형"),
        reason=(
            "속마음도 자기 시간도 아무에게나 내주지 않아요. 바로 다가가기보다 믿을 만한 사람인지 "
            "천천히 살피는 편이죠. 포장 담당자가 마스터키와 비밀번호로 애써도 꿈쩍 않던 상자는, "
            "재촉을 멈추고 기다리자 스스로 뚜껑을 슬쩍 열었어요. 억지로 따는 사람이 아니라 "
            "기다려주는 사람에게 열리는, 자물쇠 상자입니다."
        ),
    ),
}


OPENING_TOOL_COPY: dict[str, UnboxingItemCopy] = {
    "B1": UnboxingItemCopy(
        type="glove",
        name="장갑",
        tags=("루틴형", "에겐형"),
        reason=(
            "새로운 방법이 많아도 좋은 건 늘 하던 방식으로 해요. 인사는 다정하게, 챙길 건 "
            "꼬박꼬박, 어제처럼 오늘도요. 상자가 다칠까 장갑부터 끼고, 익숙한 순서대로 모서리를 "
            "하나씩 살펴 열어요. 서두르지 않고 내용물까지 다정하게 지켜내는 당신에게 주어진 "
            "도구는 포근한 장갑입니다."
        ),
    ),
    "B2": UnboxingItemCopy(
        type="utility_knife",
        name="커터칼",
        tags=("루틴형", "테토형"),
        reason=(
            "말도 행동도 군더더기가 없어요. 리액션은 짧아도 챙김은 행동으로 정확히 보여주고, "
            "검증된 방식의 든든함을 믿어요. 커터칼 날은 딱 한 칸, 테이프 중앙을 따라 스윽 한 번. "
            "누가 한눈판 사이 흠집 없이 개봉을 끝내는 당신에게 주어진 도구는 커터칼입니다."
        ),
    ),
    "B3": UnboxingItemCopy(
        type="magic_wand",
        name="마술봉",
        tags=("탐험형", "에겐형"),
        reason=(
            "새로운 건 일단 해보고, 신기한 건 사람들과 나눠야 직성이 풀려요. 다들 칼과 가위를 "
            "찾을 때 마술봉으로 상자를 톡톡 두드리자, 테이프가 리본처럼 풀리고 상자가 꽃잎처럼 "
            "열렸어요. 평범한 개봉도 작은 이벤트로 바꿔 다음을 기다리게 만드는 당신에게 주어진 "
            "도구는 마술봉입니다."
        ),
    ),
    "B4": UnboxingItemCopy(
        type="chainsaw",
        name="전기톱",
        tags=("탐험형", "테토형"),
        reason=(
            "고민은 짧고 실행은 빨라요. 꽂히면 바로 시작하고, 말은 투박해도 방향은 확실하죠. "
            "전기톱을 꺼내자 모두가 말리려 했지만, 0.3초 뒤 상자는 이미 반듯하게 열려 있었어요. "
            "모두가 놀라는 사이 화끈하게 시작해 결과는 정확하게 만드는 당신에게 주어진 도구는 "
            "전기톱입니다."
        ),
    ),
}
