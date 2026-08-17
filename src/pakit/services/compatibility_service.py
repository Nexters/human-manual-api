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

COMPATIBILITY_PROFILE_VERSION = "2026-08-17.1"

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
class CompatibilityData:
    mine: CompatibilityPersonData
    friend: CompatibilityPersonData
    headline: str
    description: str
    synergy: SynergyData
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
    ("decision", "set_direction"): "guide",
    ("decision", "lift_mood"): "connector",
    ("decision", "make_it_happen"): "organizer",
    ("decision", "draw_people_out"): "connector",
    ("decision", "coordinate_opinions"): "supporter",
    ("decision", "remember_and_care"): "supporter",
    ("worries", "set_direction"): "guide",
    ("worries", "lift_mood"): "energizer",
    ("worries", "make_it_happen"): "guide",
    ("worries", "draw_people_out"): "supporter",
    ("worries", "coordinate_opinions"): "supporter",
    ("worries", "remember_and_care"): "supporter",
    ("hangout", "set_direction"): "organizer",
    ("hangout", "lift_mood"): "energizer",
    ("hangout", "make_it_happen"): "organizer",
    ("hangout", "draw_people_out"): "connector",
    ("hangout", "coordinate_opinions"): "organizer",
    ("hangout", "remember_and_care"): "supporter",
    ("information", "set_direction"): "guide",
    ("information", "lift_mood"): "connector",
    ("information", "make_it_happen"): "guide",
    ("information", "draw_people_out"): "connector",
    ("information", "coordinate_opinions"): "supporter",
    ("information", "remember_and_care"): "supporter",
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

WEAKNESS_LABEL = {
    "distance": "서로 필요한 거리",
    "conflict": "대화를 푸는 속도",
    "care": "서로 원하는 챙김",
    "pace": "함께 움직이는 속도",
}

SUPPORT_TIPS = {
    "listen_to_me": "해결책부터 꺼내기보다 이야기를 끝까지 들어주면 마음이 먼저 풀려요.",
    "take_me_out": "기분이 가라앉을 때는 밖으로 불러내 함께 움직여주면 금방 살아나요.",
    "give_me_space": "바로 답을 재촉하지 않고 혼자 정리할 시간을 주면 다시 편하게 돌아와요.",
    "solve_together": "공감만 하고 끝내기보다 지금 할 수 있는 일을 함께 찾으면 든든해해요.",
    "make_me_laugh": "분위기가 무거워질 때 취향 맞는 웃음을 건네면 마음의 문이 빨리 열려요.",
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
        "잘못된 조합이 아니라 서로의 신호를 번역하는 시간이 필요한 사이예요.",
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


def _person(result: SubmissionResultData) -> CompatibilityPersonData:
    if result.participant is None:
        raise CompatibilityUnavailableError
    return CompatibilityPersonData(
        nickname=result.participant.nickname,
        noun=result.overview.noun,
        character_id=result.overview.character_id,
        image_url=result.overview.image_url,
    )


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
            description=(
                f"{mine_person.nickname}님과 {friend_person.nickname}님은 "
                f"{WEAKNESS_LABEL[weakest]}만 서로 확인해도 "
                "훨씬 편하고 오래 가는 사이가 될 수 있어요."
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
