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
    "details": [
        {
            "key": "distance",
            "score": 72,
            "title": "우리 사이의 거리감",
            "label": "조금 맞춰가면 돼요",
            "description": (
                "지은님은 각자의 시간을 보장받을수록 편하고, 선우님은 자주 연결될수록 "
                "안심해요. 애정의 크기보다 편한 간격이 다른 사이예요."
            ),
        },
        {
            "key": "conflict",
            "score": 68,
            "title": "서운함을 푸는 속도",
            "label": "조금 맞춰가면 돼요",
            "description": (
                "지은님은 바로 확인해야 마음이 놓이고, 선우님은 생각을 정리할 시간이 "
                "필요해요. 질문은 공격이 아니고 침묵은 회피가 아니에요."
            ),
        },
        {
            "key": "care",
            "score": 84,
            "title": "마음을 주고받는 방식",
            "label": "서로의 위로법을 알아가요",
            "description": (
                "지은님은 같이 웃으며 분위기를 바꿀 때 마음이 풀리고, 선우님은 혼자 정리할 "
                "시간을 받을 때 마음이 풀려요. 서로 원하는 위로를 미리 말해두면 애정이 "
                "엇갈리지 않아요."
            ),
        },
        {
            "key": "pace",
            "score": 91,
            "title": "약속과 행동의 리듬",
            "label": "자연스럽게 맞아요",
            "description": (
                "지은님은 분위기를 끌어올리고 재밌는 일이 생기면 움직여요. 선우님은 "
                "사람을 챙기고 지킬 약속이 있을 때 힘이 나요."
            ),
        },
    ],
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
            "지은님과 선우님은 함께 무언가를 시작하고 이어가는 호흡이 좋아요. 연락이 "
            "뜸해질 때 쓸 짧은 신호 하나를 정해두면 각자의 시간도 더 편하게 믿을 수 있어요."
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


class CompatibilityDetailOutput(BaseModel):
    """두 사람의 관계를 한 가지 관점에서 비교한 상세 분석입니다."""

    key: Literal["distance", "conflict", "care", "pace"] = Field(
        description="상세 분석 영역의 고정 ID"
    )
    score: int = Field(ge=0, le=100, description="해당 영역의 궁합 점수")
    title: str = Field(description="상세 분석 제목")
    label: str = Field(description="점수 구간을 직관적으로 설명하는 라벨")
    description: str = Field(description="두 사람의 실제 차이와 관계 장면을 설명하는 문장")


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
    details: list[CompatibilityDetailOutput] = Field(
        min_length=4,
        max_length=4,
        description="거리감·갈등·위로·행동 리듬 상세 분석 4개",
    )
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
