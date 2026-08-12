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
    "assessment_version": "2026-08-12.3",
    "participant": {"nickname": "송송"},
    "answers": [
        {"question_id": "step1.q01", "value": "restaurant"},
        {"question_id": "step1.q02", "value": "navigation"},
        {"question_id": "step1.q03", "value": "save_favorites"},
        {"question_id": "step1.q04", "value": "phone_overuse"},
        {"question_id": "step1.q05", "value": "after_waking"},
        {"question_id": "step1.q06", "value": "rush"},
        {"question_id": "step1.q07", "value": "sleep_until_noon"},
        {"question_id": "step1.q08", "value": "go_to_bed"},
        {"question_id": "step1.q09", "value": "tsundere"},
        {"question_id": "step1.q10", "value": "morning_person"},
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
    "result_code": "demo-result-code",
    "overview": {
        "rarity": "상위 4%",
        "adjective": "새벽 2시에도 카톡 폭격하는",
        "noun": "팽이",
        "result_name": "새벽 2시에도 카톡 폭격하는 팽이",
        "character_id": "spinning_top",
        "tags": ["도파민 MAX", "장난꾸러기", "혼자서도 잘 놀아요"],
    },
    "unboxing_kit": {
        "axis_scores": {
            "attachment": 20,
            "expression": 65,
            "routine": 20,
            "egen": 75,
        },
        "title": "밤이 깊어질수록 텐션이 올라가는 장난꾸러기",
        "description": "해가 지면 비로소 에너지가 충전되는 타입이에요.",
        "packaging": {
            "type": "fragile_box",
            "name": "취급주의 상자",
            "tags": ["직진형", "거리조절형"],
            "reason": "마음을 크게 담아 쉽게 드러내는 성향을 표현한 상자예요.",
        },
        "opening_tool": {
            "type": "magic_wand",
            "name": "마술봉",
            "tags": ["탐험형", "에겐형"],
            "reason": "새로운 경험을 흥미롭게 바꾸는 모습을 닮았어요.",
        },
    },
    "features": [
        {"title": "분위기를 띄워요", "description": "생각보다 빠른 행동력"},
        {"title": "일단 해봐요", "description": "생각보다 빠른 행동력"},
        {"title": "변화를 즐겨요", "description": "새로운 방식에 열린 태도"},
        {"title": "탐험형", "description": "직접 부딪히며 발견"},
    ],
    "can_do": [
        "같이 놀아주세요",
        "새로운 제안을 던져주세요",
        "리액션을 아끼지 말아주세요",
        "자유롭게 맡겨주세요",
    ],
    "warnings": [
        "똑같은 일만 반복시켜요",
        "선택을 지나치게 제한해요",
        "재미없는 분위기를 오래 끌어요",
        "아이디어를 시작부터 막아버려요",
    ],
    "charging": {
        "score": 90,
        "description": "친구들과 놀 때 가장 빠르게 충전돼요",
        "activities": [
            {"type": "hangout", "label": "친구들과 놀기"},
            {"type": "beer", "label": "맥주 한 잔"},
            {"type": "travel", "label": "여행가기"},
        ],
    },
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
        max_length=22,
        description="22개 고정 문항의 답변 목록",
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
    tags: list[str] = Field(min_length=2, max_length=2, description="관련 성향 태그 2개")
    reason: str = Field(description="이 상자가 선택된 이유")


class OpeningToolOutput(BaseModel):
    """성향 점수로 선택된 개봉 도구입니다."""

    type: Literal["glove", "utility_knife", "magic_wand", "chainsaw"] = Field(
        description="개봉 도구 고정 ID"
    )
    name: str = Field(description="결과 페이지에 표시할 한글 이름")
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

    title: str = Field(description="특징 제목")
    description: str = Field(description="특징 보조 설명")


class ChargingActivityOutput(BaseModel):
    """에너지를 충전하는 활동 한 개입니다."""

    type: str = Field(description="충전 활동 고정 ID")
    label: str = Field(description="화면 표시 문구")


class ChargingOutput(BaseModel):
    """충전 점수와 충전 활동입니다."""

    score: int = Field(ge=0, le=100, description="충전 점수")
    description: str = Field(description="충전 방법 설명")
    activities: list[ChargingActivityOutput] = Field(
        min_length=3,
        max_length=3,
        description="충전 활동 3개",
    )


class AssessmentSubmissionOutput(BaseModel):
    """테스트 제출을 검증한 후 반환하는 결과입니다."""

    model_config = ConfigDict(json_schema_extra={"example": ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE})

    result_code: str = Field(description="결과를 다시 조회할 때 사용하는 고유 코드")
    overview: OverviewOutput = Field(description="장난감 소개")
    unboxing_kit: UnboxingKitOutput = Field(description="언박싱 키트")
    features: list[FeatureOutput] = Field(
        min_length=4,
        max_length=4,
        description="핵심 특징 4개",
    )
    can_do: list[str] = Field(min_length=4, max_length=4, description="사용 방법 4개")
    warnings: list[str] = Field(min_length=4, max_length=4, description="주의사항 4개")
    charging: ChargingOutput = Field(description="충전 방법")

    @classmethod
    def from_domain(cls, result: SubmissionResultData) -> "AssessmentSubmissionOutput":
        return cls.model_validate(asdict(result))


class ErrorDetail(BaseModel):
    """클라이언트가 분기 처리할 수 있는 오류 정보입니다."""

    code: str = Field(description="기계 판독용 오류 코드")
    message: str = Field(description="개발자가 확인할 수 있는 한국어 오류 설명")


class ErrorResponse(BaseModel):
    """API 오류 응답입니다."""

    error: ErrorDetail = Field(description="오류 상세 정보")
