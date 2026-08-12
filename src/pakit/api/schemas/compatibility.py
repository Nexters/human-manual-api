from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

COMPATIBILITY_RESPONSE_EXAMPLE: dict[str, Any] = {
    "mine": {
        "nickname": "지은",
        "noun": "팽이",
        "character_id": "spinning_top",
    },
    "friend": {
        "nickname": "선우",
        "noun": "곰인형",
        "character_id": "teddy_bear",
    },
    "headline": "찰떡궁합 환상의 장난감",
    "description": "서로의 아이디어를 키워주는 신나는 조합이에요",
    "synergy": {
        "score": 80,
        "title": "낼 수 있는 시너지때",
        "description": (
            "새로운 일을 시작하면 이 친구는 색다른 시선을 더해줘요. "
            "둘이 대화할수록 아이디어가 선명해져요."
        ),
        "tags": ["즉흥적인 케미", "아이디어 시너지"],
    },
    "tips": [
        {
            "target": "mine",
            "character_id": "spinning_top",
            "title": "지은님에게",
            "description": "갑작스러운 변화는 미리 알려주고 직설적인 말은 부드럽게 다듬어주세요.",
        },
        {
            "target": "friend",
            "character_id": "cube",
            "title": "선우님에게",
            "description": (
                "즉흥적인 행동을 무책임함으로 단정하지 말고, 불편한 점은 솔직하게 알려주세요."
            ),
        },
    ],
    "relationship_tip": {
        "title": "더 오래 잘 지내려면",
        "description": (
            "서로의 속도를 바꾸려 하기보다 차이를 이해해 주세요. "
            "팽이는 갑작스러운 계획을 미리 알려주고, 비밀상자는 "
            "불편한 마음을 참지 않고 표현하면 돼요."
        ),
    },
}


class CompatibilityPersonOutput(BaseModel):
    """궁합 화면 상단에 표시할 한 사람의 결과 요약입니다."""

    nickname: str = Field(description="화면에 표시할 닉네임")
    noun: str = Field(description="테스트 결과 장난감 명사")
    character_id: str = Field(description="캐릭터 이미지 매핑용 고정 ID")


class SynergyOutput(BaseModel):
    """두 사람이 함께 있을 때의 시너지입니다."""

    score: int = Field(ge=0, le=100, description="궁합 점수")
    title: str = Field(description="시너지 제목")
    description: str = Field(description="시너지 설명")
    tags: list[str] = Field(min_length=2, max_length=2, description="시너지 태그 2개")


class CompatibilityTipOutput(BaseModel):
    """두 사람 중 한 명에게 전달할 관계 팁입니다."""

    target: Literal["mine", "friend"] = Field(description="팁을 전달할 대상")
    character_id: str = Field(description="팁 이미지 매핑용 캐릭터 ID")
    title: str = Field(description="팁 제목")
    description: str = Field(description="팁 설명")


class RelationshipTipOutput(BaseModel):
    """관계를 오래 유지하기 위한 공통 팁입니다."""

    title: str = Field(description="공통 팁 제목")
    description: str = Field(description="공통 팁 설명")


class CompatibilityOutput(BaseModel):
    """친구와의 궁합 화면에 필요한 목업 결과입니다."""

    model_config = ConfigDict(json_schema_extra={"example": COMPATIBILITY_RESPONSE_EXAMPLE})

    mine: CompatibilityPersonOutput = Field(description="내 테스트 결과 요약")
    friend: CompatibilityPersonOutput = Field(description="친구 테스트 결과 요약")
    headline: str = Field(description="궁합 결과 제목")
    description: str = Field(description="궁합 결과 한 줄 설명")
    synergy: SynergyOutput = Field(description="두 사람이 만드는 시너지")
    tips: list[CompatibilityTipOutput] = Field(
        min_length=2,
        max_length=2,
        description="각 사람에게 전달할 팁 2개",
    )
    relationship_tip: RelationshipTipOutput = Field(description="오래 지내기 위한 공통 팁")
