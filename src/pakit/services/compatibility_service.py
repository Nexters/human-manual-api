from dataclasses import dataclass
from typing import Literal

from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_submission import (
    AxisScoresData,
    CompatibilityProfileData,
    CompatibleFriendData,
    SubmissionResultData,
)
from pakit.domain.characters import CHARACTERS
from pakit.services.result_repository import ResultRepository

COMPATIBILITY_PROFILE_VERSION = "2026-08-19.1"

PRIMARY_COMPATIBLE_MBTI: dict[MbtiType, MbtiType] = {
    MbtiType.INTJ: MbtiType.ENFP,
    MbtiType.ENFP: MbtiType.INTJ,
    MbtiType.ISTJ: MbtiType.ESFP,
    MbtiType.ESFP: MbtiType.ISTJ,
    MbtiType.ENTJ: MbtiType.INFP,
    MbtiType.INFP: MbtiType.ENTJ,
    MbtiType.ESTJ: MbtiType.ISFP,
    MbtiType.ISFP: MbtiType.ESTJ,
    MbtiType.INFJ: MbtiType.ENTP,
    MbtiType.ENTP: MbtiType.INFJ,
    MbtiType.ISFJ: MbtiType.ESTP,
    MbtiType.ESTP: MbtiType.ISFJ,
    MbtiType.ENFJ: MbtiType.INTP,
    MbtiType.INTP: MbtiType.ENFJ,
    MbtiType.ESFJ: MbtiType.ISTP,
    MbtiType.ISTP: MbtiType.ESFJ,
}

OPPOSITE_MBTI: dict[MbtiType, MbtiType] = {
    mbti: MbtiType(
        "".join(
            {"E": "I", "I": "E", "S": "N", "N": "S", "T": "F", "F": "T", "J": "P", "P": "J"}[letter]
            for letter in mbti.value
        )
    )
    for mbti in MbtiType
}


class CompatibilityNotFoundError(LookupError):
    pass


class CompatibilityUnavailableError(RuntimeError):
    pass


@dataclass(frozen=True)
class CompatibilityPersonData:
    nickname: str
    noun: str
    character_id: str
    image_url: str


@dataclass(frozen=True)
class SynergyData:
    score: int
    title: str
    description: str
    tags: tuple[str, ...]


@dataclass(frozen=True)
class CompatibilityTipData:
    target: Literal["mine", "friend"]
    character_id: str
    image_url: str
    title: str
    description: str


@dataclass(frozen=True)
class RelationshipTipData:
    title: str
    description: str


@dataclass(frozen=True)
class CompatibilityDetailData:
    key: Literal["distance", "conflict", "care", "pace"]
    score: int
    title: str
    label: str
    description: str


@dataclass(frozen=True)
class CompatibilityData:
    mine: CompatibilityPersonData
    friend: CompatibilityPersonData
    headline: str
    description: str
    synergy: SynergyData
    details: tuple[CompatibilityDetailData, ...]
    tips: tuple[CompatibilityTipData, ...]
    relationship_tip: RelationshipTipData


@dataclass(frozen=True)
class CompatibilityScores:
    distance: int
    conflict: int
    care: int
    pace: int
    mbti: int

    @property
    def total(self) -> int:
        return round(
            self.distance * 0.20
            + self.conflict * 0.20
            + self.care * 0.15
            + self.pace * 0.15
            + self.mbti * 0.30
        )


RELATIONSHIP_ROLE_BY_ANSWERS: dict[tuple[str, str], str] = {
    ("decision", "organize_and_coordinate"): "guide",
    ("decision", "lift_mood"): "connector",
    ("decision", "make_it_happen"): "organizer",
    ("decision", "care_for_others"): "supporter",
    ("worries", "organize_and_coordinate"): "guide",
    ("worries", "lift_mood"): "energizer",
    ("worries", "make_it_happen"): "guide",
    ("worries", "care_for_others"): "supporter",
    ("hangout", "organize_and_coordinate"): "organizer",
    ("hangout", "lift_mood"): "energizer",
    ("hangout", "make_it_happen"): "organizer",
    ("hangout", "care_for_others"): "supporter",
    ("information", "organize_and_coordinate"): "guide",
    ("information", "lift_mood"): "connector",
    ("information", "make_it_happen"): "guide",
    ("information", "care_for_others"): "supporter",
}

MOTIVATION_GROUPS = {
    "curiosity": "novelty",
    "last_chance": "novelty",
    "fun": "fun",
    "needed_by_someone": "people_duty",
    "responsibility": "people_duty",
    "clear_goal": "achievement",
}

CARE_MATCH: dict[str, dict[str, int]] = {
    "listen_to_me": {"express_with_words": 95, "express_with_actions": 68},
    "take_me_out": {"express_with_words": 72, "express_with_actions": 95},
    "give_me_space": {"express_with_words": 82, "express_with_actions": 82},
    "solve_together": {"express_with_words": 75, "express_with_actions": 95},
    "make_me_laugh": {"express_with_words": 92, "express_with_actions": 76},
}

ROLE_COMPLEMENTS = {
    frozenset(("guide", "supporter")),
    frozenset(("organizer", "connector")),
    frozenset(("energizer", "supporter")),
}

MOTIVATION_COMPLEMENTS = {
    frozenset(("novelty", "fun")),
    frozenset(("people_duty", "achievement")),
}

DIMENSION_COPY = {
    "distance": (
        "편안한 거리감",
        "가까이 있고 싶은 순간과 각자의 시간이 필요한 순간을 비슷하게 알아봐요.",
        "거리감이 잘 맞아요",
    ),
    "conflict": (
        "대화 복구력",
        "마음이 걸렸을 때 대화를 풀어가는 속도가 비슷해 오래 묵히지 않아요.",
        "대화가 잘 통해요",
    ),
    "care": (
        "챙김 번역기",
        "한 사람이 필요로 하는 위로를 다른 사람이 알아들을 방식으로 건넬 수 있어요.",
        "챙김이 잘 통해요",
    ),
    "pace": (
        "함께 굴러가는 힘",
        "계획을 세우고 움직이는 속도가 맞아 함께할 때 일이 자연스럽게 이어져요.",
        "함께 잘 움직여요",
    ),
}

RELATIONSHIP_STRENGTH_COPY = {
    "distance": "서로 편한 간격을 알아보는 감각이 좋아요.",
    "conflict": "서운한 일이 생겨도 대화를 다시 이어가는 힘이 있어요.",
    "care": "필요한 순간에 서로의 마음을 챙기는 감각이 잘 통해요.",
    "pace": "함께 무언가를 시작하고 이어가는 호흡이 좋아요.",
}

RELATIONSHIP_HABIT_COPY = {
    "distance": (
        "연락이 뜸해질 때 쓸 짧은 신호 하나를 정해두면 각자의 시간도 더 편하게 믿을 수 있어요."
    ),
    "conflict": (
        "서운한 날에는 바로 말할지 시간을 둘지만 먼저 알려주면 좋은 호흡을 오래 지킬 수 있어요."
    ),
    "care": ("힘든 날 원하는 위로를 한마디로 알려주는 습관을 만들면 서로의 마음을 놓치지 않아요."),
    "pace": (
        "약속을 잡을 때 즉흥 제안인지 미리 정할 계획인지만 맞추면 함께하는 일이 더 즐거워져요."
    ),
}

SUPPORT_TIPS = {
    "listen_to_me": "해결책부터 꺼내기보다 이야기를 끝까지 들어주면 마음이 먼저 풀려요.",
    "take_me_out": "기분이 가라앉을 때는 밖으로 불러내 함께 움직여주면 금방 살아나요.",
    "give_me_space": "바로 답을 재촉하지 않고 혼자 정리할 시간을 주면 다시 편하게 돌아와요.",
    "solve_together": "공감만 하고 끝내기보다 지금 할 수 있는 일을 함께 찾으면 든든해해요.",
    "make_me_laugh": "분위기가 무거워질 때 취향 맞는 웃음을 건네면 마음의 문이 빨리 열려요.",
}

SUPPORT_NEED_COPY = {
    "listen_to_me": "이야기를 충분히 들어줄 때",
    "take_me_out": "밖으로 불러내 함께 움직일 때",
    "give_me_space": "혼자 정리할 시간을 받을 때",
    "solve_together": "같이 해결책을 찾을 때",
    "make_me_laugh": "같이 웃으며 분위기를 바꿀 때",
}

AFFECTION_STYLE_COPY = {
    "express_with_words": "말과 반응으로 마음을 보여주는 편이에요.",
    "express_with_actions": "말보다 행동으로 마음을 보여주는 편이에요.",
}

RELATIONSHIP_ROLE_COPY = {
    "guide": "방향을 잡는",
    "connector": "사람과 이야기를 이어주는",
    "organizer": "말 나온 일을 실제로 만드는",
    "supporter": "주변 사람을 살피고 챙기는",
    "energizer": "분위기를 끌어올리는",
}

MOTIVATION_COPY = {
    "novelty": "새로운 게 보여야",
    "fun": "재밌는 일이 생겨야",
    "people_duty": "필요로 하는 사람이나 지킬 약속이 있어야",
    "achievement": "끝낼 목표가 보여야",
}


def _primary_friend_description(mbti: MbtiType) -> str:
    return {
        "NT": "당신이 꺼낸 아이디어를 깊이 이해하고, 생각의 다음 방향을 함께 찾아줘요.",
        "NF": "당신의 상상과 감정선을 알아보고, 떠오른 가능성에 선명한 방향을 더해줘요.",
        "ST": "당신의 현실적인 판단을 존중하면서, 놓치기 쉬운 마음까지 살펴줘요.",
        "SF": "당신의 세심한 마음을 알아보고, 망설이는 순간엔 다음 행동을 잡아줘요.",
    }[mbti.value[1:3]]


def _opposite_friend_description(scores: AxisScoresData) -> str:
    if scores.routine < 50 and scores.attachment < 50:
        return "새로운 곳으로 먼저 달리는 당신 곁에서, 필요한 순간에 차분히 중심을 잡아줘요."
    if scores.routine < 50:
        return "신나는 속도를 함께 타면서, 미처 놓친 약속과 사람을 챙겨줘요."
    if scores.attachment < 50:
        return "익숙한 흐름을 지키는 당신에게, 부담스럽지 않은 새 선택지를 열어줘요."
    return "꾸준히 관계를 챙기는 당신에게, 다른 리듬과 새로운 재미를 더해줘요."


def build_compatible_friends(
    mbti: MbtiType,
    scores: AxisScoresData,
) -> tuple[CompatibleFriendData, ...]:
    recommended = (
        (PRIMARY_COMPATIBLE_MBTI[mbti], _primary_friend_description(mbti)),
        (OPPOSITE_MBTI[mbti], _opposite_friend_description(scores)),
    )
    return tuple(
        CompatibleFriendData(
            badge="환상의 장난감",
            noun=CHARACTERS[recommended_mbti].noun,
            character_id=CHARACTERS[recommended_mbti].code,
            image_url=f"/assets/{CHARACTERS[recommended_mbti].asset_key}",
            description=description,
        )
        for recommended_mbti, description in recommended
    )


def build_compatibility_profile(
    *,
    mbti: MbtiType,
    relationship_moment: str,
    relationship_strength: str,
    motivation: str,
    support_preference: str,
    conflict_style: str,
    affection_style: str,
) -> CompatibilityProfileData:
    return CompatibilityProfileData(
        version=COMPATIBILITY_PROFILE_VERSION,
        mbti=mbti.value,
        relationship_role=RELATIONSHIP_ROLE_BY_ANSWERS[
            (relationship_moment, relationship_strength)
        ],
        motivation=MOTIVATION_GROUPS[motivation],
        support_preference=support_preference,
        conflict_style=conflict_style,
        affection_style=affection_style,
    )


def _role_score(left: str, right: str) -> int:
    if left == right:
        return 88
    if frozenset((left, right)) in ROLE_COMPLEMENTS:
        return 96
    return 82


def _motivation_score(left: str, right: str) -> int:
    if left == right:
        return 92
    if frozenset((left, right)) in MOTIVATION_COMPLEMENTS:
        return 95
    return 80


def _mbti_score(left: str, right: str) -> int:
    return 76 + sum(
        6 for left_axis, right_axis in zip(left, right, strict=True) if left_axis == right_axis
    )


def calculate_scores(
    mine: SubmissionResultData,
    friend: SubmissionResultData,
) -> CompatibilityScores:
    mine_profile = mine.compatibility_profile
    friend_profile = friend.compatibility_profile
    if mine_profile is None or friend_profile is None:
        raise CompatibilityUnavailableError

    mine_scores = mine.unboxing_kit.axis_scores
    friend_scores = friend.unboxing_kit.axis_scores
    distance = 100 - abs(mine_scores.attachment - friend_scores.attachment)
    expression_alignment = 100 - abs(mine_scores.expression - friend_scores.expression)
    conflict_style = 100 if mine_profile.conflict_style == friend_profile.conflict_style else 55
    conflict = round(expression_alignment * 0.6 + conflict_style * 0.4)
    care = round(
        (
            CARE_MATCH[mine_profile.support_preference][friend_profile.affection_style]
            + CARE_MATCH[friend_profile.support_preference][mine_profile.affection_style]
        )
        / 2
    )
    routine_alignment = 100 - abs(mine_scores.routine - friend_scores.routine)
    pace = round(
        routine_alignment * 0.6
        + _role_score(mine_profile.relationship_role, friend_profile.relationship_role) * 0.2
        + _motivation_score(mine_profile.motivation, friend_profile.motivation) * 0.2
    )
    return CompatibilityScores(
        distance=distance,
        conflict=conflict,
        care=care,
        pace=pace,
        mbti=_mbti_score(mine_profile.mbti, friend_profile.mbti),
    )


def compatibility_headline(score: int) -> tuple[str, str]:
    if score >= 88:
        return (
            "찰떡궁합 환상의 장난감",
            "설명서를 길게 읽지 않아도 자연스럽게 맞물리는 사이예요.",
        )
    if score >= 76:
        return (
            "다른 맛이 잘 섞이는 장난감",
            "닮은 부분은 편안하고 다른 부분은 서로의 빈틈을 채워줘요.",
        )
    if score >= 64:
        return (
            "맞춰갈수록 좋은 장난감",
            "처음엔 속도가 달라도 서로의 사용법을 알수록 편해지는 사이예요.",
        )
    return (
        "사용설명서가 필요한 장난감",
        "서로 편한 방식이 달라, 각자의 사용법을 알아갈 시간이 필요한 사이예요.",
    )


def _mbti_tag(left: str, right: str) -> str:
    if left[1:3] == right[1:3]:
        return {
            "NT": "아이디어가 통해요",
            "ST": "현실 감각이 맞아요",
            "NF": "마음의 결이 맞아요",
            "SF": "다정함이 닮았어요",
        }[left[1:3]]
    if left[2] != right[2]:
        return "공감과 해결의 조합"
    return "상상과 현실의 조합"


def _distance_tip(target: SubmissionResultData, other: SubmissionResultData) -> str:
    target_attachment = target.unboxing_kit.axis_scores.attachment
    other_attachment = other.unboxing_kit.axis_scores.attachment
    assert other.participant is not None
    if target_attachment > other_attachment:
        return (
            f"{other.participant.nickname}님이 연락이 뜸한 순간을 마음이 멀어진 신호로 "
            "단정하지 않으면 훨씬 편해져요."
        )
    return (
        f"혼자만의 시간이 필요해도 {other.participant.nickname}님에게 짧게 안부를 남기면 "
        "관계를 더 편하게 믿을 수 있어요."
    )


def _conflict_tip(target: SubmissionResultData, other: SubmissionResultData) -> str:
    profile = target.compatibility_profile
    other_profile = other.compatibility_profile
    assert profile is not None and other_profile is not None
    if profile.conflict_style == "resolve_immediately":
        return "바로 풀고 싶어도 상대가 생각을 정리할 시간을 조금 주면 대화가 덜 엇갈려요."
    return "혼자 정리하는 동안 다시 이야기할 시간을 먼저 알려주면 상대가 답답해하지 않아요."


def _pace_tip(target: SubmissionResultData, other: SubmissionResultData) -> str:
    target_routine = target.unboxing_kit.axis_scores.routine
    other_routine = other.unboxing_kit.axis_scores.routine
    if target_routine > other_routine:
        return "계획 밖의 제안을 무책임함으로 단정하지 않고 작은 여지를 남겨두면 더 즐거워져요."
    return "갑작스러운 제안은 짧게라도 미리 알려주면 상대도 마음 편히 함께 움직여요."


def _tip_for(
    weakest: str,
    target: SubmissionResultData,
    other: SubmissionResultData,
) -> str:
    if weakest == "distance":
        return _distance_tip(target, other)
    if weakest == "conflict":
        return _conflict_tip(target, other)
    if weakest == "pace":
        return _pace_tip(target, other)
    other_profile = other.compatibility_profile
    assert other_profile is not None
    return SUPPORT_TIPS[other_profile.support_preference]


def _detail_label(score: int) -> str:
    if score >= 88:
        return "자연스럽게 맞아요"
    if score >= 74:
        return "다름이 잘 섞여요"
    if score >= 60:
        return "조금 맞춰가면 돼요"
    return "서로의 설명서가 필요해요"


def _distance_detail(
    mine: SubmissionResultData,
    friend: SubmissionResultData,
    score: int,
) -> CompatibilityDetailData:
    assert mine.participant is not None and friend.participant is not None
    mine_name = mine.participant.nickname
    friend_name = friend.participant.nickname
    mine_attachment = mine.unboxing_kit.axis_scores.attachment
    friend_attachment = friend.unboxing_kit.axis_scores.attachment
    if abs(mine_attachment - friend_attachment) <= 15:
        if (mine_attachment + friend_attachment) / 2 >= 50:
            description = (
                f"{mine_name}님과 {friend_name}님은 모두 자주 안부를 나누고 가까이 있을 때 "
                "관계가 단단하다고 느껴요."
            )
        else:
            description = (
                f"{mine_name}님과 {friend_name}님은 연락이 잠시 뜸해도 각자의 시간을 "
                "편하게 믿을 수 있어요."
            )
    else:
        closer_name, independent_name = (
            (mine_name, friend_name)
            if mine_attachment > friend_attachment
            else (friend_name, mine_name)
        )
        description = (
            f"{closer_name}님은 자주 연결될수록 안심하고, {independent_name}님은 각자의 시간을 "
            "보장받을수록 편해져요. 애정의 크기보다 편한 간격이 다른 사이예요."
        )
    return CompatibilityDetailData(
        key="distance",
        score=score,
        title="우리 사이의 거리감",
        label=_detail_label(score),
        description=description,
    )


def _conflict_detail(
    mine: SubmissionResultData,
    friend: SubmissionResultData,
    score: int,
) -> CompatibilityDetailData:
    assert mine.participant is not None and friend.participant is not None
    mine_profile = mine.compatibility_profile
    friend_profile = friend.compatibility_profile
    assert mine_profile is not None and friend_profile is not None
    mine_name = mine.participant.nickname
    friend_name = friend.participant.nickname
    if mine_profile.conflict_style == friend_profile.conflict_style:
        if mine_profile.conflict_style == "resolve_immediately":
            description = (
                f"{mine_name}님과 {friend_name}님은 서운한 일을 오래 묵히기보다 바로 확인해야 "
                "마음이 풀려요. 솔직한 대신 말의 온도만 챙기면 회복이 빠른 조합이에요."
            )
        else:
            description = (
                f"{mine_name}님과 {friend_name}님은 마음을 먼저 정리한 뒤 이야기하는 편이에요. "
                "침묵이 길어질 때 다시 대화할 시점만 알려주면 오해가 줄어요."
            )
    else:
        direct_name, pause_name = (
            (mine_name, friend_name)
            if mine_profile.conflict_style == "resolve_immediately"
            else (friend_name, mine_name)
        )
        description = (
            f"{direct_name}님은 바로 확인해야 마음이 놓이고, {pause_name}님은 생각을 정리할 "
            "시간이 필요해요. 한쪽의 질문은 공격이 아니고, 다른 쪽의 침묵은 회피가 아니에요."
        )
    return CompatibilityDetailData(
        key="conflict",
        score=score,
        title="서운함을 푸는 속도",
        label=_detail_label(score),
        description=description,
    )


def _care_detail(
    mine: SubmissionResultData,
    friend: SubmissionResultData,
    score: int,
) -> CompatibilityDetailData:
    assert mine.participant is not None and friend.participant is not None
    mine_profile = mine.compatibility_profile
    friend_profile = friend.compatibility_profile
    assert mine_profile is not None and friend_profile is not None
    mine_name = mine.participant.nickname
    friend_name = friend.participant.nickname
    same_support = mine_profile.support_preference == friend_profile.support_preference
    same_affection = mine_profile.affection_style == friend_profile.affection_style
    if same_support:
        shared_need = SUPPORT_NEED_COPY[mine_profile.support_preference]
        if same_affection:
            description = (
                f"{mine_name}님과 {friend_name}님은 모두 {shared_need} 마음이 풀려요. 애정을 "
                f"표현할 때도 둘 다 {AFFECTION_STYLE_COPY[mine_profile.affection_style]} "
                "서로의 챙김을 비교적 쉽게 알아보는 조합이에요."
            )
            label = "위로도 표현도 닮았어요"
        else:
            description = (
                f"{mine_name}님과 {friend_name}님은 모두 {shared_need} 마음이 풀려요. 다만 "
                f"{mine_name}님은 {AFFECTION_STYLE_COPY[mine_profile.affection_style]} "
                f"{friend_name}님은 {AFFECTION_STYLE_COPY[friend_profile.affection_style]} "
                "원하는 위로는 같지만 애정이 보이는 모양은 달라요."
            )
            label = "원하는 위로는 같아요"
    else:
        description = (
            f"{mine_name}님은 {SUPPORT_NEED_COPY[mine_profile.support_preference]} 마음이 풀리고, "
            f"{friend_name}님은 {SUPPORT_NEED_COPY[friend_profile.support_preference]} 마음이 "
            f"풀려요. {mine_name}님은 {AFFECTION_STYLE_COPY[mine_profile.affection_style]} "
            f"{friend_name}님은 {AFFECTION_STYLE_COPY[friend_profile.affection_style]} 서로 원하는 "
            "위로를 미리 말해두면 애정이 엇갈리지 않아요."
        )
        label = "서로의 위로법을 알아가요"
    return CompatibilityDetailData(
        key="care",
        score=score,
        title="마음을 주고받는 방식",
        label=label,
        description=description,
    )


def _pace_detail(
    mine: SubmissionResultData,
    friend: SubmissionResultData,
    score: int,
) -> CompatibilityDetailData:
    assert mine.participant is not None and friend.participant is not None
    mine_profile = mine.compatibility_profile
    friend_profile = friend.compatibility_profile
    assert mine_profile is not None and friend_profile is not None
    mine_name = mine.participant.nickname
    friend_name = friend.participant.nickname
    description = (
        f"{mine_name}님은 관계에서 {RELATIONSHIP_ROLE_COPY[mine_profile.relationship_role]} 역할을 "
        f"맡고, {MOTIVATION_COPY[mine_profile.motivation]} 잘 움직여요. {friend_name}님은 "
        f"{RELATIONSHIP_ROLE_COPY[friend_profile.relationship_role]} 역할을 맡고, "
        f"{MOTIVATION_COPY[friend_profile.motivation]} 힘이 나요."
    )
    return CompatibilityDetailData(
        key="pace",
        score=score,
        title="약속과 행동의 리듬",
        label=_detail_label(score),
        description=description,
    )


def _compatibility_details(
    mine: SubmissionResultData,
    friend: SubmissionResultData,
    scores: CompatibilityScores,
) -> tuple[CompatibilityDetailData, ...]:
    return (
        _distance_detail(mine, friend, scores.distance),
        _conflict_detail(mine, friend, scores.conflict),
        _care_detail(mine, friend, scores.care),
        _pace_detail(mine, friend, scores.pace),
    )


def _person(result: SubmissionResultData) -> CompatibilityPersonData:
    if result.participant is None:
        raise CompatibilityUnavailableError
    return CompatibilityPersonData(
        nickname=result.participant.nickname,
        noun=result.overview.noun,
        character_id=result.overview.character_id,
        image_url=result.overview.image_url,
    )


def _relationship_tip_description(
    mine: CompatibilityPersonData,
    friend: CompatibilityPersonData,
    strongest: str,
    weakest: str,
    dimensions: dict[str, int],
) -> str:
    names = f"{mine.nickname}님과 {friend.nickname}님은"
    if strongest == weakest:
        if dimensions[strongest] >= 74:
            return (
                f"{names} 네 가지 관계 리듬이 고르게 잘 맞는 편이에요. 서로 필요한 거리와 "
                "위로가 달라지는 순간만 가끔 확인해보세요."
            )
        return (
            f"{names} 한 가지보다 여러 관계 리듬을 천천히 알아가는 것이 중요한 사이예요. "
            "연락·대화·위로 중 그날 가장 필요한 것부터 한마디로 알려주세요."
        )
    return f"{names} {RELATIONSHIP_STRENGTH_COPY[strongest]} {RELATIONSHIP_HABIT_COPY[weakest]}"


def build_compatibility(
    mine: SubmissionResultData,
    friend: SubmissionResultData,
) -> CompatibilityData:
    mine_person = _person(mine)
    friend_person = _person(friend)
    scores = calculate_scores(mine, friend)
    dimensions = {
        "distance": scores.distance,
        "conflict": scores.conflict,
        "care": scores.care,
        "pace": scores.pace,
    }
    strongest = max(dimensions, key=dimensions.__getitem__)
    weakest = min(dimensions, key=dimensions.__getitem__)
    mine_profile = mine.compatibility_profile
    friend_profile = friend.compatibility_profile
    assert mine_profile is not None and friend_profile is not None
    synergy_title, synergy_description, synergy_tag = DIMENSION_COPY[strongest]
    headline, description = compatibility_headline(scores.total)
    mine_tip = _tip_for(weakest, mine, friend)
    friend_tip = _tip_for(weakest, friend, mine)

    return CompatibilityData(
        mine=mine_person,
        friend=friend_person,
        headline=headline,
        description=description,
        synergy=SynergyData(
            score=scores.total,
            title=synergy_title,
            description=synergy_description,
            tags=(synergy_tag, _mbti_tag(mine_profile.mbti, friend_profile.mbti)),
        ),
        details=_compatibility_details(mine, friend, scores),
        tips=(
            CompatibilityTipData(
                target="mine",
                character_id=mine_person.character_id,
                image_url=mine_person.image_url,
                title=f"{mine_person.nickname}님에게",
                description=mine_tip,
            ),
            CompatibilityTipData(
                target="friend",
                character_id=friend_person.character_id,
                image_url=friend_person.image_url,
                title=f"{friend_person.nickname}님에게",
                description=friend_tip,
            ),
        ),
        relationship_tip=RelationshipTipData(
            title="더 오래 잘 지내려면",
            description=_relationship_tip_description(
                mine_person,
                friend_person,
                strongest,
                weakest,
                dimensions,
            ),
        ),
    )


async def get_compatibility(
    mine_code: str,
    friend_code: str,
    repository: ResultRepository,
) -> CompatibilityData:
    mine = await repository.get(mine_code)
    friend = await repository.get(friend_code)
    if mine is None or friend is None:
        raise CompatibilityNotFoundError
    return build_compatibility(mine, friend)
