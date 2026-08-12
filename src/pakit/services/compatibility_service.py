from dataclasses import dataclass
from typing import Literal

MINE_RESULT_CODE = "demo-result-code"
FRIEND_RESULT_CODE = "demo-friend-code"


class CompatibilityNotFoundError(LookupError):
    pass


@dataclass(frozen=True)
class CompatibilityPersonData:
    nickname: str
    noun: str
    character_id: str


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


def get_mock_compatibility(mine: str, friend: str) -> CompatibilityData:
    if mine != MINE_RESULT_CODE or friend != FRIEND_RESULT_CODE:
        raise CompatibilityNotFoundError

    return CompatibilityData(
        mine=CompatibilityPersonData("지은", "팽이", "spinning_top"),
        friend=CompatibilityPersonData("선우", "곰인형", "teddy_bear"),
        headline="찰떡궁합 환상의 장난감",
        description="서로의 아이디어를 키워주는 신나는 조합이에요",
        synergy=SynergyData(
            score=80,
            title="낼 수 있는 시너지때",
            description=(
                "새로운 일을 시작하면 이 친구는 색다른 시선을 더해줘요. "
                "둘이 대화할수록 아이디어가 선명해져요."
            ),
            tags=("즉흥적인 케미", "아이디어 시너지"),
        ),
        tips=(
            CompatibilityTipData(
                target="mine",
                character_id="spinning_top",
                title="지은님에게",
                description=(
                    "갑작스러운 변화는 미리 알려주고 직설적인 말은 부드럽게 다듬어주세요."
                ),
            ),
            CompatibilityTipData(
                target="friend",
                character_id="cube",
                title="선우님에게",
                description=(
                    "즉흥적인 행동을 무책임함으로 단정하지 말고, 불편한 점은 솔직하게 알려주세요."
                ),
            ),
        ),
        relationship_tip=RelationshipTipData(
            title="더 오래 잘 지내려면",
            description=(
                "서로의 속도를 바꾸려 하기보다 차이를 이해해 주세요. "
                "팽이는 갑작스러운 계획을 미리 알려주고, 비밀상자는 "
                "불편한 마음을 참지 않고 표현하면 돼요."
            ),
        ),
    )
