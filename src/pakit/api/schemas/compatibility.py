from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

COMPATIBILITY_RESPONSE_EXAMPLE: dict[str, Any] = {
    "mine": {
        "nickname": "지은",
        "noun": "팽이",
        "character_id": "spinning_top",
        "image_url": "https://api.pakit.kr/assets/characters/spinning_top.png",
    },
    "friend": {
        "nickname": "선우",
        "noun": "곰인형",
        "character_id": "teddy_bear",
        "image_url": "https://api.pakit.kr/assets/characters/teddy_bear.png",
    },
    "headline": "다른 맛이 잘 섞이는 장난감",
    "description": "닮은 부분은 편안하고 다른 부분은 서로의 빈틈을 채워줘요.",
    "synergy": {
        "score": 80,
        "title": "함께 굴러가는 힘",
        "description": ("계획을 세우고 움직이는 속도가 맞아 함께할 때 일이 자연스럽게 이어져요."),
        "tags": ["함께 잘 움직여요", "아이디어가 통해요"],
    },
    "tips": [
        {
            "target": "mine",
            "character_id": "spinning_top",
            "image_url": "https://api.pakit.kr/assets/characters/spinning_top.png",
            "title": "지은님에게",
            "description": (
                "갑작스러운 제안은 짧게라도 미리 알려주면 상대도 마음 편히 함께 움직여요."
            ),
        },
        {
            "target": "friend",
            "character_id": "teddy_bear",
            "image_url": "https://api.pakit.kr/assets/characters/teddy_bear.png",
            "title": "선우님에게",
            "description": (
                "계획 밖의 제안을 무책임함으로 단정하지 않고 작은 여지를 남겨두면 더 즐거워져요."
            ),
        },
    ],
    "relationship_tip": {
        "title": "더 오래 잘 지내려면",
        "description": (
            "지은님과 선우님은 함께 움직이는 속도의 신호만 서로 확인해도 "
            "훨씬 편하고 오래 가는 사이가 될 수 있어요."
        ),
    },
}


class CompatibilityPersonOutput(BaseModel):
    """궁합 화면 상단에 표시할 한 사람의 결과 요약입니다."""

    nickname: str = Field(description="화면에 표시할 닉네임")
    noun: str = Field(description="테스트 결과 장난감 명사")
    character_id: str = Field(description="캐릭터 이미지 매핑용 고정 ID")
    image_url: str = Field(description="서버가 제공하는 캐릭터 이미지 절대 URL")


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
    image_url: str = Field(description="팁에 표시할 캐릭터 이미지 절대 URL")
    title: str = Field(description="팁 제목")
    description: str = Field(description="팁 설명")


class RelationshipTipOutput(BaseModel):
    """관계를 오래 유지하기 위한 공통 팁입니다."""

    title: str = Field(description="공통 팁 제목")
    description: str = Field(description="공통 팁 설명")


class CompatibilityOutput(BaseModel):
    """저장된 두 테스트 결과로 계산한 친구 궁합입니다."""

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

    @classmethod
    def from_domain_payload(
        cls,
        payload: dict[str, Any],
        *,
        public_base_url: str,
    ) -> "CompatibilityOutput":
        def absolute_url(path: str) -> str:
            if path.startswith(("http://", "https://")):
                return path
            return f"{public_base_url.rstrip('/')}/{path.lstrip('/')}"

        payload["mine"]["image_url"] = absolute_url(payload["mine"]["image_url"])
        payload["friend"]["image_url"] = absolute_url(payload["friend"]["image_url"])
        for tip in payload["tips"]:
            tip["image_url"] = absolute_url(tip["image_url"])
        return cls.model_validate(payload)
