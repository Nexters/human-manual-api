from dataclasses import asdict
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, StrictInt, StrictStr

from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_submission import (
    AssessmentSubmission,
    SubmissionResultData,
    SubmittedAnswer,
)

ASSESSMENT_SUBMISSION_EXAMPLE: dict[str, object] = {
    "assessment_version": "2026-08-14.3",
    "participant": {"nickname": "송송"},
    "answers": [
        {"question_id": "step1.q01", "value": "decision"},
        {"question_id": "step1.q02", "value": "set_direction"},
        {"question_id": "step1.q03", "value": "save_favorites"},
        {"question_id": "step1.q04", "value": "phone_overuse"},
        {"question_id": "step1.q05", "value": "after_waking"},
        {"question_id": "step1.q06", "value": "rush"},
        {"question_id": "step1.q07", "value": "sleep_until_noon"},
        {"question_id": "step1.q08", "value": "go_to_bed"},
        {"question_id": "step1.q09", "value": "tsundere"},
        {"question_id": "step1.q10", "value": "morning_person"},
        {"question_id": "step1.q11", "value": "curiosity"},
        {"question_id": "step1.q12", "value": "listen_to_me"},
        {"question_id": "step2.q01", "value": "inspect_profile"},
        {"question_id": "step2.q02", "value": "hint_and_wait"},
        {"question_id": "step2.q03", "value": "rehearse_with_ai"},
        {"question_id": "step2.q04", "value": 50},
        {"question_id": "step2.q05", "value": "share_everything"},
        {"question_id": "step2.q06", "value": 247},
        {"question_id": "step2.q07", "value": "decorate_for_mood"},
        {"question_id": "step2.q08", "value": "express_with_words"},
        {"question_id": "step2.q09", "value": "ruminate"},
        {"question_id": "step2.q10", "value": "order_familiar_menu"},
        {"question_id": "step2.q11", "value": "order_familiar_stores"},
        {"question_id": "step2.q12", "value": "press"},
    ],
    "mbti": "ENTP",
}

ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE: dict[str, Any] = {
    "result_code": "aB3dE7_x",
    "participant": {"nickname": "송송"},
    "overview": {
        "rarity": "상위 4%",
        "adjective": "옷 예쁘게 입고 플러팅 했다고 하는",
        "noun": "팽이",
        "result_name": "옷 예쁘게 입고 플러팅 했다고 하는 팽이",
        "character_id": "spinning_top",
        "image_url": "https://api.pakit.kr/assets/characters/spinning_top.png",
        "tags": ["도파민 MAX", "장난꾸러기", "혼자서도 잘 놀아요"],
    },
    "unboxing_kit": {
        "axis_scores": {
            "attachment": 83,
            "expression": 0,
            "routine": 67,
            "egen": 100,
        },
        "title": "안 친한 척하면서 안부는 꼬박꼬박 챙기는 사람",
        "description": (
            "좋아하는 티는 죽어도 안 내는데, 행동이 이미 다 말하고 있어요. 지나가듯 한 말을 "
            "기억했다가 슬쩍 내밀고, 익숙해진 옆자리는 조용히 지키죠. 가까워지는 덴 느려도 "
            "한번 데워지면 안 식는 은은한 온돌 타입이에요."
        ),
        "packaging": {
            "type": "matryoshka_box",
            "name": "마트료시카 상자",
            "image_url": "https://api.pakit.kr/assets/packaging_boxes/matryoshka_box.png",
            "tags": ["탐색형", "밀착형"],
            "reason": (
                "좋아하는 마음을 바로 보여주는 법이 없어요. 티 안 나게 챙기고, 안부는 돌려서 묻고, "
                "속마음은 몇 번을 접어 안쪽에 넣어두거든요. 근데 마음의 크기는 정반대예요 한번 "
                "곁을 준 사람 옆엔 조용히, 아주 오래 붙어 있어요. 무심해 보였다면 숨긴 거지, 없는 "
                "게 아니에요. 포장 담당자가 검수하려고 뚜껑을 열자, 안에서 상자가 또 나왔어요. "
                "열면 또 상자, 또 상자 첫 겹엔 눈치가, 다음 겹엔 조심스러운 호감이, 안쪽으로 "
                "갈수록 벽에 메모랑 하트가 빼곡해지더니, 마지막 상자는 마음이 꽉 차서 뚜껑이 잘 "
                "안 닫힐 지경이었어요. 담당자는 열어본 순서 그대로 한 겹씩 정성껏 다시 덮고 출고 "
                "도장을 찍었습니다. 서두르지 않고 한 겹씩 열어주는 사람만 알맹이까지 만날 수 있는, "
                "마트료시카 상자입니다."
            ),
        },
        "opening_tool": {
            "type": "glove",
            "name": "장갑",
            "image_url": "https://api.pakit.kr/assets/opening_tools/glove.png",
            "tags": ["루틴형", "에겐형"],
            "reason": (
                "새로운 방법이 넘쳐나도, 좋은 건 늘 하던 방식으로 하는 사람이에요. 인사는 "
                "다정하게, 챙길 건 꼬박꼬박, 어제처럼 오늘도. 심심하다는 오해를 받지만 한결같은 "
                "건 재미없는 게 아니라 안심되는 거예요. 테이프 끝을 무작정 잡아당겼다간 상자까지 "
                "아플까 봐, 장갑부터 얌전히 끼고 시작해요. 테이프가 어디서 시작되는지, 어느 "
                "모서리부터 열어야 안 찢어지는지 익숙한 순서로 하나하나 살피면서, 모서리마다 "
                "조심조심. 서두르지 않고 내용물까지 다정하게 지켜내며 여는 당신에게 주어진 도구는 "
                "포근한 장갑입니다."
            ),
        },
    },
    "features": [
        {
            "title": "궁금하면 직진",
            "description": (
                "궁금한 건 검색만으로 넘기지 않고, 원리와 다른 가능성까지 직접 확인해요."
            ),
        },
        {
            "title": "결정 대장",
            "description": (
                "친구들이 아무거나만 반복하면 조건을 딱 정리해 선택지를 좁혀주는 사람이에요."
            ),
        },
        {
            "title": "혼자 곱씹어요",
            "description": (
                "마음이 복잡하면 바로 꺼내기보다 충분히 들여다보고, 준비가 되면 차근차근 말해요."
            ),
        },
        {
            "title": "다르게 봐요",
            "description": "모두가 당연하다고 넘긴 곳에서 다른 가능성을 발견해요.",
        },
    ],
    "character_story": {
        "title": "한번 돌기 시작하면 새로운 판을 만드는 팽이",
        "description": (
            "팽이는 얌전히 세워두는 순간보다 힘껏 돌기 시작할 때 진짜 재미가 보여요. 정해진 "
            "자리만 맴돌지 않고 이쪽저쪽 부딪치며, 예상하지 못한 방향에서도 자기 균형을 찾아내죠. "
            "당연한 답에 멈추지 않고 새로운 가능성을 시험하는 모습이 닮아 팽이가 도착했습니다."
        ),
    },
    "can_do": [
        "결론을 재촉하지 말고 생각의 흐름을 들어주세요",
        "별일 없어도 자주 안부를 묻고 곁에 있어주세요",
        "표정이 달라지면 지나치지 말고 먼저 물어봐주세요",
        "말과 리액션에 담긴 애정을 알아봐주세요",
    ],
    "warnings": [
        "해결하려고 꺼낸 말에 차갑다는 반응이 돌아오면 억울해져요",
        "내 얘기에 반응이 없으면 신나서 하던 이야기도 금세 재미없어져요",
        "재촉받으면 하려던 마음도 사라져요",
        "잠이 덜 깨면 첫 반응이 무뚝뚝해요",
    ],
    "charging": {
        "description": (
            "일정이 비면 아쉬워하기보다 잠부터 보충해요. 누구의 속도에도 맞추지 않고 "
            "충분히 자야 배터리가 제대로 차는 타입이에요."
        ),
        "activities": [
            {"type": "sleep_until_noon", "label": "늦잠으로 밀린 잠 갚기"},
            {"type": "go_to_bed", "label": "비어버린 약속만큼 푹 쉬기"},
            {
                "type": "sleep_until_noon_go_to_bed",
                "label": "휴대폰을 멀리 두고 알람 없이 푹 자기",
            },
        ],
    },
    "compatible_friends": [
        {
            "badge": "환상의 장난감",
            "noun": "비밀상자",
            "character_id": "secret_box",
            "image_url": "https://api.pakit.kr/assets/characters/secret_box.png",
            "description": (
                "당신이 꺼낸 아이디어를 깊이 이해하고, 생각의 다음 방향을 함께 찾아줘요."
            ),
        },
        {
            "badge": "환상의 장난감",
            "noun": "테디베어",
            "character_id": "teddy_bear",
            "image_url": "https://api.pakit.kr/assets/characters/teddy_bear.png",
            "description": ("꾸준히 관계를 챙기는 당신에게, 다른 리듬과 새로운 재미를 더해줘요."),
        },
    ],
}


class ParticipantInput(BaseModel):
    """테스트 참여자 정보입니다."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nickname: str = Field(min_length=1, description="결과 화면에 표시할 이름 또는 닉네임")


class AnswerInput(BaseModel):
    """한 문항의 답변입니다."""

    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(description="문항 고정 ID")
    value: StrictStr | StrictInt = Field(description="선택한 영문 ID 또는 입력한 정수")


class AssessmentSubmissionInput(BaseModel):
    """프론트엔드에서 완료한 테스트 전체 제출 데이터입니다."""

    assessment_version: str = Field(description="문항 및 채점 계약 버전")
    participant: ParticipantInput = Field(description="테스트 참여자 정보")
    answers: list[AnswerInput] = Field(
        min_length=1,
        max_length=24,
        description="24개 고정 문항의 답변 목록",
    )
    mbti: MbtiType = Field(description="화면에서 선택한 네 글자 MBTI 유형")

    def to_domain(self) -> AssessmentSubmission:
        answers = [SubmittedAnswer(answer.question_id, answer.value) for answer in self.answers]

        return AssessmentSubmission(
            assessment_version=self.assessment_version,
            nickname=self.participant.nickname,
            answers=tuple(answers),
            mbti=self.mbti,
        )


class OverviewOutput(BaseModel):
    """결과 페이지 상단의 장난감 소개입니다."""

    rarity: str = Field(description="희귀도 문구")
    adjective: str = Field(description="성향 축으로 결정된 형용사")
    noun: str = Field(description="MBTI에 따라 결정된 장난감 명사")
    result_name: str = Field(description="형용사와 명사를 합친 최종 결과명")
    character_id: str = Field(description="캐릭터 이미지 매핑용 고정 ID")
    image_url: str = Field(description="서버가 제공하는 캐릭터 이미지 절대 URL")
    tags: list[str] = Field(min_length=3, max_length=3, description="말풍선 태그 3개")


class AxisScoresOutput(BaseModel):
    """언박싱 키트를 결정하는 네 가지 성향 점수입니다."""

    attachment: int = Field(ge=0, le=100, description="거리조절 0 ↔ 밀착 100")
    expression: int = Field(ge=0, le=100, description="탐색 0 ↔ 직진 100")
    routine: int = Field(ge=0, le=100, description="탐험 0 ↔ 루틴 100")
    egen: int = Field(ge=0, le=100, description="테토 0 ↔ 에겐 100")


class PackagingOutput(BaseModel):
    """성향 점수로 선택된 포장 상자입니다."""

    type: Literal["fragile_box", "minimal_box", "matryoshka_box", "locked_box"] = Field(
        description="포장 상자 고정 ID"
    )
    name: str = Field(description="결과 페이지에 표시할 한글 이름")
    image_url: str = Field(description="서버가 제공하는 포장 상자 이미지 절대 URL")
    tags: list[str] = Field(min_length=2, max_length=2, description="관련 성향 태그 2개")
    reason: str = Field(description="이 상자가 선택된 이유")


class OpeningToolOutput(BaseModel):
    """성향 점수로 선택된 개봉 도구입니다."""

    type: Literal["glove", "utility_knife", "magic_wand", "chainsaw"] = Field(
        description="개봉 도구 고정 ID"
    )
    name: str = Field(description="결과 페이지에 표시할 한글 이름")
    image_url: str = Field(description="서버가 제공하는 개봉 도구 이미지 절대 URL")
    tags: list[str] = Field(min_length=2, max_length=2, description="관련 성향 태그 2개")
    reason: str = Field(description="이 도구가 선택된 이유")


class UnboxingKitOutput(BaseModel):
    """성향 점수와 그 점수로 결정된 언박싱 키트입니다."""

    axis_scores: AxisScoresOutput = Field(description="성향 축 4개 점수")
    title: str = Field(description="성향 요약 제목")
    description: str = Field(description="성향 요약 설명")
    packaging: PackagingOutput = Field(description="포장 상자")
    opening_tool: OpeningToolOutput = Field(description="개봉 도구")


class FeatureOutput(BaseModel):
    """장난감의 핵심 특징 한 개입니다."""

    title: str = Field(max_length=7, description="공백 포함 7자 이하의 특징 제목")
    description: str = Field(description="특징 보조 설명")


class CharacterStoryOutput(BaseModel):
    """핵심 특징과 메인 장난감을 연결하는 이야기입니다."""

    title: str = Field(description="장난감의 특징을 담은 이야기 제목")
    description: str = Field(description="장난감과 사용자의 대표 성향을 연결한 설명")


class ChargingActivityOutput(BaseModel):
    """에너지를 충전하는 활동 한 개입니다."""

    type: str = Field(description="충전 활동 고정 ID")
    label: str = Field(description="화면 표시 문구")


class ChargingOutput(BaseModel):
    """충전 방법 설명과 활동입니다."""

    description: str = Field(description="충전 방법 설명")
    activities: list[ChargingActivityOutput] = Field(
        min_length=3,
        max_length=3,
        description="충전 활동 3개",
    )


class CompatibleFriendOutput(BaseModel):
    """개인 결과 화면에 미리 보여주는 잘 맞는 친구 장난감입니다."""

    badge: str = Field(description="카드 상단 궁합 배지")
    noun: str = Field(description="추천 친구의 장난감 명사")
    character_id: str = Field(description="추천 친구 캐릭터의 고정 ID")
    image_url: str = Field(description="추천 친구 캐릭터 이미지 절대 URL")
    description: str = Field(description="사용자와 이 장난감이 잘 맞는 이유")


class AssessmentSubmissionOutput(BaseModel):
    """테스트 제출을 검증한 후 반환하는 결과입니다."""

    model_config = ConfigDict(json_schema_extra={"example": ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE})

    result_code: str = Field(
        min_length=8,
        max_length=8,
        pattern=r"^[A-Za-z0-9_-]{8}$",
        description="결과를 다시 조회할 때 사용하는 URL-safe 8자리 고유 코드",
    )
    participant: ParticipantInput | None = Field(
        description="결과 화면에 표시할 이름 또는 닉네임. 이전 결과에는 없을 수 있음"
    )
    overview: OverviewOutput = Field(description="장난감 소개")
    unboxing_kit: UnboxingKitOutput = Field(description="언박싱 키트")
    features: list[FeatureOutput] = Field(
        min_length=4,
        max_length=4,
        description="핵심 특징 4개",
    )
    character_story: CharacterStoryOutput = Field(
        description="핵심 특징과 메인 장난감을 연결한 이야기"
    )
    can_do: list[str] = Field(min_length=4, max_length=4, description="사용 방법 4개")
    warnings: list[str] = Field(min_length=4, max_length=4, description="주의사항 4개")
    charging: ChargingOutput = Field(description="충전 방법")
    compatible_friends: list[CompatibleFriendOutput] = Field(
        max_length=2,
        description="개인 결과 화면의 친구 궁합 미리보기. 새 결과는 2개, 기존 결과는 비어 있음",
    )

    @classmethod
    def from_domain(
        cls,
        result: SubmissionResultData,
        *,
        public_base_url: str,
    ) -> "AssessmentSubmissionOutput":
        payload = asdict(result)

        def absolute_url(path: str) -> str:
            if path.startswith(("http://", "https://")):
                return path
            return f"{public_base_url.rstrip('/')}/{path.lstrip('/')}"

        payload["overview"]["image_url"] = absolute_url(payload["overview"]["image_url"])
        payload["unboxing_kit"]["packaging"]["image_url"] = absolute_url(
            payload["unboxing_kit"]["packaging"]["image_url"]
        )
        payload["unboxing_kit"]["opening_tool"]["image_url"] = absolute_url(
            payload["unboxing_kit"]["opening_tool"]["image_url"]
        )
        for friend in payload["compatible_friends"]:
            friend["image_url"] = absolute_url(friend["image_url"])
        return cls.model_validate(payload)


class ErrorDetail(BaseModel):
    """클라이언트가 분기 처리할 수 있는 오류 정보입니다."""

    code: str = Field(description="기계 판독용 오류 코드")
    message: str = Field(description="개발자가 확인할 수 있는 한국어 오류 설명")


class ErrorResponse(BaseModel):
    """API 오류 응답입니다."""

    error: ErrorDetail = Field(description="오류 상세 정보")
