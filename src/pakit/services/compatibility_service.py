from dataclasses import dataclass
from typing import Literal

from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_submission import (
    CompatibilityProfileData,
    CompatibleFriendData,
    SubmissionResultData,
)
from pakit.domain.characters import CHARACTERS
from pakit.services.result_repository import ResultRepository

COMPATIBILITY_PROFILE_VERSION = "2026-08-19.1"

COMPATIBLE_MBTI: dict[MbtiType, MbtiType] = {
    MbtiType.INTJ: MbtiType.ENFP,
    MbtiType.INTP: MbtiType.ENTJ,
    MbtiType.ENTJ: MbtiType.INTP,
    MbtiType.ENTP: MbtiType.INFJ,
    MbtiType.INFJ: MbtiType.ENTP,
    MbtiType.INFP: MbtiType.ENFJ,
    MbtiType.ENFJ: MbtiType.INFP,
    MbtiType.ENFP: MbtiType.INTJ,
    MbtiType.ISTJ: MbtiType.ESFP,
    MbtiType.ISFJ: MbtiType.ESTP,
    MbtiType.ESTJ: MbtiType.ISFP,
    MbtiType.ESFJ: MbtiType.ISTP,
    MbtiType.ISTP: MbtiType.ESFJ,
    MbtiType.ISFP: MbtiType.ESTJ,
    MbtiType.ESTP: MbtiType.ISFJ,
    MbtiType.ESFP: MbtiType.ISTJ,
}

MISMATCHED_MBTI: dict[MbtiType, MbtiType] = {
    MbtiType.INTJ: MbtiType.ESFP,
    MbtiType.INTP: MbtiType.ESFJ,
    MbtiType.ENTJ: MbtiType.ISFP,
    MbtiType.ENTP: MbtiType.ISFJ,
    MbtiType.INFJ: MbtiType.ESTP,
    MbtiType.INFP: MbtiType.ESTJ,
    MbtiType.ENFJ: MbtiType.ISTP,
    MbtiType.ENFP: MbtiType.ISTJ,
    MbtiType.ISTJ: MbtiType.ENFP,
    MbtiType.ISFJ: MbtiType.ENTP,
    MbtiType.ESTJ: MbtiType.INFP,
    MbtiType.ESFJ: MbtiType.INTP,
    MbtiType.ISTP: MbtiType.ENFJ,
    MbtiType.ISFP: MbtiType.ENTJ,
    MbtiType.ESTP: MbtiType.INFJ,
    MbtiType.ESFP: MbtiType.INTJ,
}

COMPATIBLE_FRIEND_DESCRIPTION: dict[MbtiType, str] = {
    MbtiType.INTJ: (
        "큰 그림을 차분히 완성하는 당신 곁에서, 새로운 가능성을 꺼내 생각의 폭을 넓혀줘요."
    ),
    MbtiType.ISTJ: (
        "익숙한 일상을 단단히 지키는 당신 곁에서, 평범한 하루에도 생기와 즐거움을 더해줘요."
    ),
    MbtiType.ENTJ: (
        "목표를 향해 빠르게 나아가는 당신 곁에서, 놓친 논리와 더 나은 방법을 차분히 찾아줘요."
    ),
    MbtiType.ESTJ: (
        "일의 순서와 기준을 세우는 당신 곁에서, 사람의 마음과 분위기까지 놓치지 않게 해줘요."
    ),
    MbtiType.INFJ: (
        "사람과 상황의 숨은 의미를 읽는 당신 곁에서, 엉뚱한 질문으로 생각의 문을 더 크게 열어줘요."
    ),
    MbtiType.ISFJ: (
        "익숙한 사람과 일상을 세심히 챙기는 당신 곁에서, "
        "망설이던 순간에도 가볍게 첫발을 내딛게 해줘요."
    ),
    MbtiType.ENFJ: (
        "사람의 가능성을 먼저 발견하는 당신 곁에서, "
        "쉽게 지나칠 수 있는 진짜 마음을 조용히 들려줘요."
    ),
    MbtiType.ESFJ: (
        "주변 사람을 빠짐없이 챙기는 당신 곁에서, "
        "복잡한 문제를 말보다 행동으로 든든하게 해결해줘요."
    ),
    MbtiType.INFP: (
        "마음속에 소중한 가능성을 품은 당신 곁에서, "
        "그 마음을 세상 밖으로 꺼낼 용기와 추진력을 더해줘요."
    ),
    MbtiType.ISFP: (
        "자신의 속도로 편안한 분위기를 만드는 당신 곁에서, "
        "미뤄둔 일을 실제로 끝낼 안정감과 힘을 더해줘요."
    ),
    MbtiType.ENFP: (
        "떠오르는 가능성을 자유롭게 펼치는 당신 곁에서, "
        "흩어진 생각에 선명한 구조와 방향을 더해줘요."
    ),
    MbtiType.ESFP: (
        "지금 이 순간의 즐거움을 나누는 당신 곁에서, "
        "약속과 중요한 일을 빠짐없이 챙겨 중심을 잡아줘요."
    ),
    MbtiType.INTP: (
        "원리와 가능성을 끝까지 파고드는 당신 곁에서, "
        "생각의 핵심을 골라 실제 결과로 이어지게 해줘요."
    ),
    MbtiType.ISTP: (
        "말보다 행동으로 문제를 해결하는 당신 곁에서, "
        "표현하지 않은 마음까지 알아보고 관계를 따뜻하게 이어줘요."
    ),
    MbtiType.ENTP: (
        "새로운 생각을 끝없이 펼치는 당신 곁에서, "
        "그 안의 의미를 알아보고 더 깊은 방향으로 이어줘요."
    ),
    MbtiType.ESTP: ("새로운 곳으로 먼저 달리는 당신 곁에서, 필요한 순간에 차분히 중심을 잡아줘요."),
}

MISMATCHED_FRIEND_DESCRIPTION: dict[MbtiType, str] = {
    MbtiType.INTJ: (
        "정해둔 흐름대로 움직이고 싶은 당신에게, "
        "순간의 재미를 따라 자꾸 방향을 바꾸는 모습은 불안하게 느껴져요."
    ),
    MbtiType.ISTJ: (
        "한 가지를 확실히 마무리하고 싶은 당신에게, "
        "새로운 관심사로 계속 방향을 트는 모습은 정신없게 느껴져요."
    ),
    MbtiType.ENTJ: (
        "분명한 목표와 속도가 중요한 당신에게, "
        "마음이 움직일 때까지 기다리는 방식은 답답하게 느껴질 수 있어요."
    ),
    MbtiType.ESTJ: (
        "정해진 기준으로 결론을 내고 싶은 당신에게, "
        "각자의 의미와 가능성을 먼저 살피는 방식은 막막하게 느껴져요."
    ),
    MbtiType.INFJ: (
        "충분히 생각하고 마음을 확인하고 싶은 당신에게, "
        "일단 부딪혀보는 빠른 속도는 벅차게 느껴져요."
    ),
    MbtiType.ISFJ: (
        "안정된 흐름과 약속을 지키고 싶은 당신에게, "
        "계속 새로운 방법을 시험하는 모습은 피곤하게 느껴져요."
    ),
    MbtiType.ENFJ: (
        "마음을 나누며 가까워지고 싶은 당신에게, "
        "필요한 말만 남기고 혼자 해결하는 방식은 멀게 느껴져요."
    ),
    MbtiType.ESFJ: (
        "표정과 반응을 주고받으며 안심하는 당신에게, "
        "혼자 생각 속으로 깊이 들어가는 모습은 거리감 있게 느껴져요."
    ),
    MbtiType.INFP: (
        "내 마음과 의미를 충분히 알아주길 바라는 당신에게, "
        "현실적인 기준으로 답부터 정하는 방식은 차갑게 느껴져요."
    ),
    MbtiType.ISFP: (
        "마음이 움직이는 속도를 지키고 싶은 당신에게, "
        "목표부터 정하고 빠르게 밀어붙이는 방식은 부담스럽게 느껴져요."
    ),
    MbtiType.ENFP: (
        "새로운 방향을 마음껏 탐색하고 싶은 당신에게, "
        "정해진 절차와 익숙한 방식을 먼저 확인하는 모습은 답답하게 느껴져요."
    ),
    MbtiType.ESFP: (
        "함께 반응하고 바로 즐기고 싶은 당신에게, "
        "계획과 분석부터 차분히 쌓는 방식은 멀게 느껴질 수 있어요."
    ),
    MbtiType.INTP: (
        "혼자 충분히 생각할 시간이 필요한 당신에게, "
        "계속 반응과 감정 표현을 기대하는 모습은 부담스럽게 느껴져요."
    ),
    MbtiType.ISTP: (
        "문제를 조용히 정리하고 싶은 당신에게, "
        "감정을 계속 꺼내 함께 나누려는 방식은 벅차게 느껴져요."
    ),
    MbtiType.ENTP: (
        "새로운 방식을 자유롭게 시험하고 싶은 당신에게, "
        "익숙한 기준과 안전한 순서를 먼저 지키는 모습은 답답하게 느껴져요."
    ),
    MbtiType.ESTP: (
        "눈앞의 기회를 바로 잡고 싶은 당신에게, "
        "의미와 마음을 오래 들여다보는 방식은 긴 기다림처럼 느껴져요."
    ),
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
            self.distance * 0.25
            + self.conflict * 0.25
            + self.care * 0.20
            + self.pace * 0.20
            + self.mbti * 0.10
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

CARE_DELIVERY_MATCH = {
    "listen_to_me": {"express_with_words"},
    "take_me_out": {"express_with_actions"},
    "give_me_space": {"express_with_words", "express_with_actions"},
    "solve_together": {"express_with_actions"},
    "make_me_laugh": {"express_with_words"},
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
        "함께 노는 방식",
        "새로움에 대한 취향과 함께 있을 때 편한 분위기가 비슷해요.",
        "노는 결이 잘 맞아요",
    ),
}

RELATIONSHIP_STRENGTH_COPY = {
    "distance": "서로 편한 간격을 알아보는 감각이 좋아요.",
    "conflict": "서운한 일이 생겨도 대화를 다시 이어가는 힘이 있어요.",
    "care": "필요한 순간에 서로의 마음을 챙기는 감각이 잘 통해요.",
    "pace": "함께할 장소와 분위기를 고르는 감각이 잘 맞아요.",
}

RELATIONSHIP_HABIT_COPY = {
    "distance": (
        "연락이 뜸해질 때 쓸 짧은 신호 하나를 정해두면 각자의 시간도 더 편하게 믿을 수 있어요."
    ),
    "conflict": (
        "서운한 날에는 바로 말할지 시간을 둘지만 먼저 알려주면 좋은 호흡을 오래 지킬 수 있어요."
    ),
    "care": ("힘든 날 원하는 위로를 한마디로 알려주는 습관을 만들면 서로의 마음을 놓치지 않아요."),
    "pace": ("새로운 곳과 익숙한 곳, 북적이는 자리와 조용한 시간을 번갈아 고르면 더 즐거워져요."),
}

SUPPORT_TIPS = {
    "listen_to_me": "해결책부터 꺼내기보다 이야기를 끝까지 들어주면 마음이 먼저 풀려요.",
    "take_me_out": "기분이 가라앉을 때는 밖으로 불러내 함께 움직여주면 금방 살아나요.",
    "give_me_space": "바로 답을 재촉하지 않고 혼자 정리할 시간을 주면 다시 편하게 돌아와요.",
    "solve_together": "공감만 하고 끝내기보다 지금 할 수 있는 일을 함께 찾으면 든든해해요.",
    "make_me_laugh": "분위기가 무거워질 때 취향 맞는 웃음을 건네면 마음의 문이 빨리 열려요.",
}

PLAY_STYLE_TIP_COPY = {
    (("E", "explore"), ("E", "explore")): (
        "둘 다 새로운 곳을 좋아하니, 다음에 가볼 장소를 번갈아 하나씩 골라보세요!"
    ),
    (("E", "explore"), ("E", "routine")): ("가끔은 상대가 좋아하는 단골 코스를 함께 따라가보세요!"),
    (("E", "explore"), ("I", "explore")): (
        "가끔은 북적임을 벗어나, 둘만 조용히 놀 수 있는 곳으로 데려가보세요!"
    ),
    (("E", "explore"), ("I", "routine")): (
        "가끔은 상대가 좋아하는 단골 코스에서 둘만 조용히 보내보세요!"
    ),
    (("E", "routine"), ("E", "explore")): ("가끔은 새로운 곳을 골라 상대를 데려가보세요!"),
    (("E", "routine"), ("E", "routine")): (
        "둘 다 익숙한 곳을 좋아하니, 함께 자주 갈 단골 코스를 하나 더 만들어보세요!"
    ),
    (("E", "routine"), ("I", "explore")): ("가끔은 둘이 조용히 둘러볼 새로운 곳으로 데려가보세요!"),
    (("E", "routine"), ("I", "routine")): (
        "가끔은 북적임을 벗어나, 둘만 조용히 놀 수 있는 곳으로 데려가보세요!"
    ),
    (("I", "explore"), ("E", "explore")): (
        "가보고 싶은 새로운 곳이 생기면 먼저 연락해 같이 가자고 해보세요!"
    ),
    (("I", "explore"), ("E", "routine")): (
        "상대가 좋아하는 단골 코스가 생각나면 먼저 연락해 약속을 잡아보세요!"
    ),
    (("I", "explore"), ("I", "explore")): (
        "둘 다 새로운 경험을 좋아하니, 함께 궁금했던 곳을 하나씩 골라 가보세요!"
    ),
    (("I", "explore"), ("I", "routine")): ("가끔은 상대가 좋아하는 단골 코스를 함께 따라가보세요!"),
    (("I", "routine"), ("E", "explore")): (
        "가끔은 상대가 가보고 싶어 한 새로운 곳으로 먼저 연락해 불러내보세요!"
    ),
    (("I", "routine"), ("E", "routine")): (
        "상대가 자주 가는 편한 곳에서 만나자고 먼저 연락해보세요!"
    ),
    (("I", "routine"), ("I", "explore")): ("가끔은 새로운 곳을 골라 상대를 데려가보세요!"),
    (("I", "routine"), ("I", "routine")): (
        "둘 다 익숙하고 조용한 시간을 좋아하니, 편한 단골 코스를 마음껏 즐겨보세요!"
    ),
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


def build_compatible_friends(mbti: MbtiType) -> tuple[CompatibleFriendData, ...]:
    recommendations = (
        (
            "환상의 장난감",
            COMPATIBLE_MBTI[mbti],
            COMPATIBLE_FRIEND_DESCRIPTION[mbti],
        ),
        (
            "환장의 장난감",
            MISMATCHED_MBTI[mbti],
            MISMATCHED_FRIEND_DESCRIPTION[mbti],
        ),
    )
    return tuple(
        CompatibleFriendData(
            badge=badge,
            noun=CHARACTERS[friend_mbti].noun,
            character_id=CHARACTERS[friend_mbti].code,
            image_url=f"/assets/{CHARACTERS[friend_mbti].asset_key}",
            description=description,
        )
        for badge, friend_mbti, description in recommendations
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
    ei_alignment = 100 if mine_profile.mbti[0] == friend_profile.mbti[0] else 80
    return CompatibilityScores(
        distance=distance,
        conflict=conflict,
        care=care,
        pace=round(routine_alignment * 0.80 + ei_alignment * 0.20),
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


def _play_style(
    result: SubmissionResultData,
) -> tuple[Literal["E", "I"], Literal["explore", "routine"]]:
    profile = result.compatibility_profile
    assert profile is not None
    energy: Literal["E", "I"] = "E" if profile.mbti.startswith("E") else "I"
    novelty: Literal["explore", "routine"] = (
        "routine" if result.unboxing_kit.axis_scores.routine >= 50 else "explore"
    )
    return energy, novelty


def _pace_tip(target: SubmissionResultData, other: SubmissionResultData) -> str:
    return PLAY_STYLE_TIP_COPY[(_play_style(target), _play_style(other))]


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
    attachment_gap = abs(mine_attachment - friend_attachment)
    both_close = mine_attachment >= 50 and friend_attachment >= 50
    both_independent = mine_attachment < 50 and friend_attachment < 50
    if both_close:
        if attachment_gap <= 15:
            description = (
                f"{mine_name}님과 {friend_name}님은 모두 자주 안부를 나누고 가까이 있을 때 "
                "관계가 단단하다고 느껴요."
            )
        else:
            more_connected_name, more_spacious_name = (
                (mine_name, friend_name)
                if mine_attachment > friend_attachment
                else (friend_name, mine_name)
            )
            description = (
                f"{mine_name}님과 {friend_name}님은 모두 자주 연결될 때 관계가 편해져요. 다만 "
                f"{more_connected_name}님은 안부를 더 자주 나누고 싶어 하고, "
                f"{more_spacious_name}님은 가까운 사이에서도 잠깐의 여유가 필요해요."
            )
    elif both_independent:
        if attachment_gap <= 15:
            description = (
                f"{mine_name}님과 {friend_name}님은 연락이 잠시 뜸해도 각자의 시간을 "
                "편하게 믿을 수 있어요."
            )
        else:
            more_connected_name, more_independent_name = (
                (mine_name, friend_name)
                if mine_attachment > friend_attachment
                else (friend_name, mine_name)
            )
            description = (
                f"{mine_name}님과 {friend_name}님은 모두 각자의 시간을 중요하게 생각해요. 다만 "
                f"{more_connected_name}님은 {more_independent_name}님보다 조금 더 자주 안부를 "
                "나눌 때 관계가 편해져요."
            )
    else:
        closer_name, independent_name = (
            (mine_name, friend_name)
            if mine_attachment > friend_attachment
            else (friend_name, mine_name)
        )
        if attachment_gap <= 15:
            description = (
                "원하는 간격의 차이가 크지 않아 자연스럽게 맞는 사이예요. 다만 상대적으로 "
                f"{closer_name}님은 안부를 조금 더 자주 나누는 게 편하고, {independent_name}님은 "
                "혼자 쉬는 틈이 조금 더 필요해요."
            )
        else:
            description = (
                "서로 원하는 관계의 간격이 달라 조금씩 맞춰갈 필요가 있는 사이예요. "
                f"{closer_name}님은 자주 연락하고 함께 있을 때 안정감을 느끼고, "
                f"{independent_name}님은 가까운 사이에서도 혼자 보내는 시간이 필요해요."
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
        mine_expression = mine.unboxing_kit.axis_scores.expression
        friend_expression = friend.unboxing_kit.axis_scores.expression
        expression_gap = abs(mine_expression - friend_expression)
        if mine_profile.conflict_style == "resolve_immediately":
            if expression_gap <= 15:
                description = (
                    f"{mine_name}님과 {friend_name}님은 서운한 일을 오래 묵히기보다 바로 확인해야 "
                    "마음이 풀려요. 솔직한 대신 말의 온도만 챙기면 회복이 빠른 조합이에요."
                )
            else:
                more_direct_name, more_deliberate_name = (
                    (mine_name, friend_name)
                    if mine_expression > friend_expression
                    else (friend_name, mine_name)
                )
                description = (
                    f"{mine_name}님과 {friend_name}님은 모두 서운한 일을 바로 풀고 싶어 해요. 다만 "
                    f"{more_direct_name}님은 생각난 말을 먼저 꺼내고, {more_deliberate_name}님은 "
                    "표현을 한 번 정리한 뒤 이야기하는 편이에요."
                )
        else:
            if expression_gap <= 15:
                description = (
                    f"{mine_name}님과 {friend_name}님은 마음을 먼저 정리한 뒤 이야기하는 편이에요. "
                    "침묵이 길어질 때 다시 대화할 시점만 알려주면 오해가 줄어요."
                )
            else:
                earlier_name, more_deliberate_name = (
                    (mine_name, friend_name)
                    if mine_expression > friend_expression
                    else (friend_name, mine_name)
                )
                description = (
                    f"{mine_name}님과 {friend_name}님은 모두 마음을 먼저 정리할 시간이 필요해요. "
                    f"다만 {earlier_name}님은 정리되면 비교적 먼저 말을 꺼내고, "
                    f"{more_deliberate_name}님은 할 말을 충분히 고른 뒤 이야기하는 편이에요."
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
        need_copy = f"{mine_name}님과 {friend_name}님은 모두 {shared_need} 마음이 풀려요."
    else:
        need_copy = (
            f"{mine_name}님은 {SUPPORT_NEED_COPY[mine_profile.support_preference]} 마음이 풀리고, "
            f"{friend_name}님은 {SUPPORT_NEED_COPY[friend_profile.support_preference]} 마음이 "
            "풀려요."
        )

    if same_affection:
        affection_copy = f"두 사람 모두 {AFFECTION_STYLE_COPY[mine_profile.affection_style]}"
    else:
        affection_copy = (
            f"{mine_name}님은 {AFFECTION_STYLE_COPY[mine_profile.affection_style]} "
            f"{friend_name}님은 {AFFECTION_STYLE_COPY[friend_profile.affection_style]}"
        )

    mine_receives_care = (
        friend_profile.affection_style in CARE_DELIVERY_MATCH[mine_profile.support_preference]
    )
    friend_receives_care = (
        mine_profile.affection_style in CARE_DELIVERY_MATCH[friend_profile.support_preference]
    )
    if mine_receives_care and friend_receives_care:
        label = "서로의 챙김이 잘 닿아요"
        delivery_copy = "서로 건네는 애정이 각자가 원하는 위로로 자연스럽게 닿아요."
    elif mine_receives_care or friend_receives_care:
        matched_name, unmatched_name = (
            (mine_name, friend_name) if mine_receives_care else (friend_name, mine_name)
        )
        label = "한쪽에는 바로 닿아요"
        delivery_copy = (
            f"{matched_name}님에게는 상대의 챙김이 잘 닿지만, {unmatched_name}님에게는 원하는 "
            "위로가 바로 전달되지 않을 수 있어요."
        )
    else:
        label = "챙김에 번역이 필요해요"
        delivery_copy = "서로 챙기고도 원하는 위로가 바로 전달되지 않을 수 있어요."

    description = f"{need_copy} {affection_copy} {delivery_copy}"
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
    mine_name = mine.participant.nickname
    friend_name = friend.participant.nickname
    mine_routine = mine.unboxing_kit.axis_scores.routine
    friend_routine = friend.unboxing_kit.axis_scores.routine
    routine_gap = abs(mine_routine - friend_routine)
    mine_style = _play_style(mine)
    friend_style = _play_style(friend)

    if mine_style[1] != friend_style[1] and routine_gap <= 15:
        description = (
            f"{mine_name}님과 {friend_name}님은 새로움에 대한 취향 차이가 크지 않아요. "
            "함께할 장소보다 편한 분위기만 맞추면 자연스럽게 잘 놀 수 있어요."
        )
    elif mine_style == friend_style:
        same_style_copy = {
            ("E", "explore"): (
                "새로운 곳과 활동을 사람들과 함께 즐길 때 신나요. 처음 해보는 약속도 쉽게 "
                "맞는 사이예요."
            ),
            ("E", "routine"): (
                "익숙한 장소에서 좋아하는 사람들과 어울릴 때 편해요. 단골 코스가 생길수록 더 "
                "잘 놀아요."
            ),
            ("I", "explore"): "낯선 경험을 좋아하지만, 북적이기보다 둘만의 속도로 즐길 때 편해요.",
            ("I", "routine"): (
                "익숙한 장소에서 조용히 보내는 시간을 좋아해요. 자주 가던 곳에서도 충분히 "
                "즐거운 사이예요."
            ),
        }
        description = f"{mine_name}님과 {friend_name}님은 둘 다 {same_style_copy[mine_style]}"
    else:
        style_names = {mine_style: mine_name, friend_style: friend_name}
        style_pair = frozenset((mine_style, friend_style))
        if style_pair == frozenset((("E", "explore"), ("E", "routine"))):
            description = (
                "둘 다 사람들과 어울리는 걸 좋아하지만, "
                f"{style_names[('E', 'explore')]}님은 새로운 곳에 끌리고 "
                f"{style_names[('E', 'routine')]}님은 익숙한 곳이 편해요. 장소만 번갈아 "
                "고르면 잘 맞아요."
            )
        elif style_pair == frozenset((("I", "explore"), ("I", "routine"))):
            description = (
                "둘 다 차분하게 노는 걸 좋아하지만, "
                f"{style_names[('I', 'explore')]}님은 낯선 경험을 원하고 "
                f"{style_names[('I', 'routine')]}님은 익숙한 선택이 편해요."
            )
        elif style_pair == frozenset((("E", "explore"), ("I", "explore"))):
            description = (
                "둘 다 새로운 경험을 좋아해요. "
                f"{style_names[('E', 'explore')]}님은 여럿이 신나게, "
                f"{style_names[('I', 'explore')]}님은 소수로 여유롭게 즐길 때 편해요."
            )
        elif style_pair == frozenset((("E", "routine"), ("I", "routine"))):
            description = (
                "둘 다 익숙한 장소를 좋아해요. "
                f"{style_names[('E', 'routine')]}님은 사람들과 어울릴 때, "
                f"{style_names[('I', 'routine')]}님은 조용히 머물 때 더 충전돼요."
            )
        elif style_pair == frozenset((("E", "explore"), ("I", "routine"))):
            description = (
                f"{style_names[('E', 'explore')]}님은 새로운 곳에서 사람들과 어울릴 때 신나고, "
                f"{style_names[('I', 'routine')]}님은 익숙한 곳에서 조용히 보내야 편해요. "
                "장소와 분위기를 하나씩 번갈아 맞춰주세요."
            )
        else:
            description = (
                f"{style_names[('E', 'routine')]}님은 익숙한 장소에서 사람들과 어울리는 걸 "
                f"좋아하고, {style_names[('I', 'explore')]}님은 낯선 곳을 조용히 탐색하는 걸 "
                "좋아해요. 새로운 곳을 한적한 시간에 가면 둘 다 편해요."
            )
    return CompatibilityDetailData(
        key="pace",
        score=score,
        title="함께 노는 방식",
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
