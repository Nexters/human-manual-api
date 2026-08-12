from dataclasses import asdict
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field

from pakit.domain.assessment_contract import AnswerKind
from pakit.domain.assessment_submission import (
    AssessmentSubmission,
    MbtiScores,
    SubmissionResultData,
    SubmittedAnswer,
)

AllowedMbtiScore = Literal[0, 20, 40, 60, 80, 100]

ASSESSMENT_SUBMISSION_EXAMPLE: dict[str, object] = {
    "assessment_version": "2026-08-12.1",
    "participant": {"nickname": "송송"},
    "answers": [
        {"question_id": "step1.q01", "kind": "choice", "option_id": "restaurant"},
        {"question_id": "step1.q02", "kind": "choice", "option_id": "navigation"},
        {"question_id": "step1.q03", "kind": "choice", "option_id": "save_favorites"},
        {"question_id": "step1.q04", "kind": "choice", "option_id": "phone_overuse"},
        {"question_id": "step1.q05", "kind": "choice", "option_id": "after_waking"},
        {"question_id": "step1.q06", "kind": "choice", "option_id": "rush"},
        {"question_id": "step1.q07", "kind": "choice", "option_id": "sleep_until_noon"},
        {"question_id": "step1.q08", "kind": "choice", "option_id": "go_to_bed"},
        {"question_id": "step1.q09", "kind": "choice", "option_id": "tsundere"},
        {"question_id": "step1.q10", "kind": "choice", "option_id": "morning_person"},
        {"question_id": "step2.q01", "kind": "choice", "option_id": "inspect_profile"},
        {"question_id": "step2.q02", "kind": "choice", "option_id": "hint_and_wait"},
        {"question_id": "step2.q03", "kind": "choice", "option_id": "rehearse_with_ai"},
        {"question_id": "step2.q04", "kind": "scale", "value": 50},
        {"question_id": "step2.q05", "kind": "choice", "option_id": "share_everything"},
        {"question_id": "step2.q06", "kind": "integer", "value": 247},
        {"question_id": "step2.q07", "kind": "choice", "option_id": "decorate_for_mood"},
        {"question_id": "step2.q08", "kind": "choice", "option_id": "express_with_words"},
        {"question_id": "step2.q09", "kind": "choice", "option_id": "ruminate"},
        {"question_id": "step2.q10", "kind": "choice", "option_id": "order_familiar_menu"},
        {
            "question_id": "step2.q11",
            "kind": "choice",
            "option_id": "order_familiar_stores",
        },
        {"question_id": "step2.q12", "kind": "action", "action_id": "press"},
    ],
    "mbti_scores": {
        "introversion": 80,
        "intuition": 60,
        "feeling": 40,
        "perceiving": 80,
    },
}


class ParticipantInput(BaseModel):
    """테스트 참여자 정보입니다."""

    model_config = ConfigDict(str_strip_whitespace=True)

    nickname: str = Field(min_length=1, description="결과 화면에 표시할 이름 또는 닉네임")


class ChoiceAnswerInput(BaseModel):
    """하나의 선택지를 고르는 문항의 답변입니다."""

    question_id: str = Field(description="문항 고정 ID")
    kind: Literal["choice"] = Field(description="객관식 답변 타입")
    option_id: str = Field(description="선택한 보기의 고정 ID")


class ScaleAnswerInput(BaseModel):
    """슬라이더로 입력하는 문항의 답변입니다."""

    question_id: str = Field(description="문항 고정 ID")
    kind: Literal["scale"] = Field(description="슬라이더 답변 타입")
    value: int = Field(strict=True, description="슬라이더에서 선택한 정수 값")


class IntegerAnswerInput(BaseModel):
    """숫자를 직접 입력하는 문항의 답변입니다."""

    question_id: str = Field(description="문항 고정 ID")
    kind: Literal["integer"] = Field(description="정수 입력 답변 타입")
    value: int = Field(strict=True, description="사용자가 직접 입력한 정수 값")


class ActionAnswerInput(BaseModel):
    """버튼 누르기 또는 건너뛰기처럼 행동을 선택하는 문항의 답변입니다."""

    question_id: str = Field(description="문항 고정 ID")
    kind: Literal["action"] = Field(description="행동 선택 답변 타입")
    action_id: str = Field(description="선택한 행동의 고정 ID")


AnswerInput = Annotated[
    ChoiceAnswerInput | ScaleAnswerInput | IntegerAnswerInput | ActionAnswerInput,
    Field(discriminator="kind"),
]


class MbtiScoresInput(BaseModel):
    """MBTI 네 지표의 오른쪽 극점 기준 퍼센트입니다."""

    introversion: AllowedMbtiScore = Field(description="외향형 E 0 ↔ 내향형 I 100")
    intuition: AllowedMbtiScore = Field(description="감각형 S 0 ↔ 직관형 N 100")
    feeling: AllowedMbtiScore = Field(description="사고형 T 0 ↔ 감정형 F 100")
    perceiving: AllowedMbtiScore = Field(description="판단형 J 0 ↔ 인식형 P 100")


class AssessmentSubmissionInput(BaseModel):
    """프론트엔드에서 완료한 테스트 전체 제출 데이터입니다."""

    assessment_version: str = Field(description="문항 및 채점 계약 버전")
    participant: ParticipantInput = Field(description="테스트 참여자 정보")
    answers: list[AnswerInput] = Field(
        min_length=1,
        max_length=22,
        description="22개 고정 문항의 답변 목록",
    )
    mbti_scores: MbtiScoresInput = Field(
        description="0·20·40·60·80·100 중 하나로 입력한 MBTI 축별 퍼센트"
    )

    def to_domain(self) -> AssessmentSubmission:
        answers: list[SubmittedAnswer] = []
        for answer in self.answers:
            if isinstance(answer, ChoiceAnswerInput):
                answers.append(
                    SubmittedAnswer(answer.question_id, AnswerKind.CHOICE, answer.option_id)
                )
            elif isinstance(answer, ActionAnswerInput):
                answers.append(
                    SubmittedAnswer(answer.question_id, AnswerKind.ACTION, answer.action_id)
                )
            elif isinstance(answer, ScaleAnswerInput):
                answers.append(
                    SubmittedAnswer(answer.question_id, AnswerKind.SCALE, value=answer.value)
                )
            else:
                answers.append(
                    SubmittedAnswer(answer.question_id, AnswerKind.INTEGER, value=answer.value)
                )

        return AssessmentSubmission(
            assessment_version=self.assessment_version,
            nickname=self.participant.nickname,
            answers=tuple(answers),
            mbti_scores=MbtiScores(**self.mbti_scores.model_dump()),
        )


class ProductOutput(BaseModel):
    """결과 화면에 표시할 제품과 캐릭터 정보입니다."""

    name: str = Field(description="형용사와 캐릭터 명사를 조합한 제품명")
    noun: str = Field(description="MBTI에 연결된 캐릭터 명사")
    character_code: str = Field(description="캐릭터 고정 코드")
    character_asset_key: str = Field(description="프론트엔드 캐릭터 이미지 에셋 키")


class UnboxingOutput(BaseModel):
    """언박싱 연출에 사용할 분류 코드입니다."""

    packaging_code: str = Field(description="포장 유형 코드")
    opening_tool_code: str = Field(description="개봉 도구 유형 코드")


class IntroductionOutput(BaseModel):
    """사용 설명서의 제품 소개 영역입니다."""

    model_name: str = Field(description="참여자가 입력한 이름 또는 닉네임")
    summary: str = Field(description="제품 소개 요약 문구")
    version: str = Field(description="화면에 표시할 제품 버전")


class CompatibilityOutput(BaseModel):
    """잘 맞는 유형과 맞지 않는 유형입니다."""

    compatible: list[str] = Field(description="잘 맞는 유형 목록")
    incompatible: list[str] = Field(description="맞지 않는 유형 목록")


class RarityOutput(BaseModel):
    """결과의 희귀도 정보입니다."""

    grade: str | None = Field(description="희귀도 등급. 미확정이면 null")
    percentage: float | None = Field(description="희귀도 백분율. 미확정이면 null")


class ManualOutput(BaseModel):
    """결과 페이지의 사용 설명서 항목입니다."""

    introduction: IntroductionOutput = Field(description="제품 소개")
    core_features: list[str] = Field(description="핵심 기능 문구 목록")
    precautions: list[str] = Field(description="사용 시 주의사항 목록")
    bugs: list[str] = Field(description="알려진 버그 문구 목록")
    compatibility: CompatibilityOutput = Field(description="호환 유형 정보")
    rarity: RarityOutput = Field(description="한정판 및 희귀도 정보")
    charging: list[str] = Field(description="에너지를 충전하는 방법 목록")


class AssessmentSubmissionOutput(BaseModel):
    """테스트 제출을 검증한 후 반환하는 결과입니다."""

    result_id: str | None = Field(description="저장된 결과 ID. 저장하지 않으면 null")
    persisted: bool = Field(description="결과가 서버에 저장되었는지 여부")
    mode: Literal["mock", "live"] = Field(description="목업 또는 실제 결과 모드")
    assessment_version: str = Field(description="요청에 사용된 테스트 계약 버전")
    content_version: str = Field(description="결과 문구 콘텐츠 버전")
    product: ProductOutput = Field(description="제품명과 캐릭터 정보")
    unboxing: UnboxingOutput = Field(description="언박싱 연출 정보")
    manual: ManualOutput = Field(description="사용 설명서 결과")
    provisional_fields: list[str] = Field(description="아직 목업인 응답 필드 경로 목록")

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
