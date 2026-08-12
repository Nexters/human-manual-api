from pakit.domain.assessment_contract import (
    ASSESSMENT_VERSION,
    QUESTION_CONTRACTS,
    AnswerKind,
)
from pakit.domain.assessment_submission import (
    AssessmentSubmission,
    CompatibilityData,
    IntroductionData,
    ManualData,
    ProductData,
    RarityData,
    SubmissionResultData,
    UnboxingData,
)
from pakit.domain.characters import CHARACTERS


class UnsupportedAssessmentVersionError(ValueError):
    pass


class InvalidSubmissionError(ValueError):
    pass


def _validate_answers(submission: AssessmentSubmission) -> None:
    question_ids = [answer.question_id for answer in submission.answers]
    if len(question_ids) != len(set(question_ids)):
        raise InvalidSubmissionError("문항 답변은 중복될 수 없습니다.")

    expected_ids = set(QUESTION_CONTRACTS)
    submitted_ids = set(question_ids)
    missing_ids = sorted(expected_ids - submitted_ids)
    unknown_ids = sorted(submitted_ids - expected_ids)
    if unknown_ids:
        raise InvalidSubmissionError(f"알 수 없는 문항 ID입니다: {', '.join(unknown_ids)}")
    if missing_ids:
        raise InvalidSubmissionError(f"필수 문항 답변이 누락되었습니다: {', '.join(missing_ids)}")

    for answer in submission.answers:
        contract = QUESTION_CONTRACTS[answer.question_id]
        if contract.answer_kind in {AnswerKind.CHOICE, AnswerKind.ACTION}:
            if not isinstance(answer.value, str):
                raise InvalidSubmissionError(f"{answer.question_id}의 value는 문자열이어야 합니다.")
            if answer.value not in contract.allowed_values:
                raise InvalidSubmissionError(f"{answer.question_id}에 허용되지 않은 value입니다.")
        elif not isinstance(answer.value, int):
            raise InvalidSubmissionError(f"{answer.question_id}의 value는 정수여야 합니다.")


def submit_assessment(submission: AssessmentSubmission) -> SubmissionResultData:
    if submission.assessment_version != ASSESSMENT_VERSION:
        raise UnsupportedAssessmentVersionError

    _validate_answers(submission)
    character = CHARACTERS[submission.mbti]
    descriptor = "좋아하면 대놓고 자랑하는"

    return SubmissionResultData(
        result_id=None,
        persisted=False,
        mode="mock",
        assessment_version=ASSESSMENT_VERSION,
        content_version="mock-v1",
        product=ProductData(
            name=f"{descriptor} {character.noun}",
            noun=character.noun,
            character_code=character.code,
            character_asset_key=character.asset_key,
        ),
        unboxing=UnboxingData(packaging_code="A1", opening_tool_code="B1"),
        manual=ManualData(
            introduction=IntroductionData(
                model_name=submission.nickname,
                summary=f"{character.noun} 캐릭터에 연결된 목업 제품 설명입니다.",
                version="v1.0",
            ),
            core_features=("관심 있는 대상을 자기 방식으로 오래 탐색합니다.",),
            precautions=("결과 문구는 현재 프론트엔드 연동용 목업입니다.",),
            bugs=("실제 채점 규칙이 연결되기 전까지 같은 목업 문구가 표시됩니다.",),
            compatibility=CompatibilityData(compatible=(), incompatible=()),
            rarity=RarityData(grade=None, percentage=None),
            charging=("좋아하는 방식으로 충분히 쉬기",),
        ),
        provisional_fields=("product.name", "unboxing", "manual"),
    )
