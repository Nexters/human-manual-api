from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_contract import (
    ASSESSMENT_VERSION,
    QUESTION_CONTRACTS,
    AnswerKind,
)
from pakit.domain.assessment_submission import (
    AssessmentSubmission,
    AxisScoresData,
    ChargingActivityData,
    ChargingData,
    FeatureData,
    OverviewData,
    SubmissionResultData,
    UnboxingItemData,
    UnboxingKitData,
)
from pakit.domain.characters import CHARACTERS


class UnsupportedAssessmentVersionError(ValueError):
    pass


class InvalidSubmissionError(ValueError):
    pass


class ResultNotFoundError(LookupError):
    pass


DEMO_RESULT_CODE = "demo-result-code"


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


def _build_mock_result(mbti: MbtiType, result_code: str) -> SubmissionResultData:
    character = CHARACTERS[mbti]
    adjective = "새벽 2시에도 카톡 폭격하는"

    return SubmissionResultData(
        result_code=result_code,
        overview=OverviewData(
            rarity="상위 4%",
            adjective=adjective,
            noun=character.noun,
            result_name=f"{adjective} {character.noun}",
            character_id=character.code,
            tags=("도파민 MAX", "장난꾸러기", "혼자서도 잘 놀아요"),
        ),
        unboxing_kit=UnboxingKitData(
            axis_scores=AxisScoresData(
                attachment=20,
                expression=65,
                routine=20,
                egen=75,
            ),
            title="밤이 깊어질수록 텐션이 올라가는 장난꾸러기",
            description="해가 지면 비로소 에너지가 충전되는 타입이에요.",
            packaging=UnboxingItemData(
                type="fragile_box",
                name="취급주의 상자",
                tags=("직진형", "거리조절형"),
                reason="마음을 크게 담아 쉽게 드러내는 성향을 표현한 상자예요.",
            ),
            opening_tool=UnboxingItemData(
                type="magic_wand",
                name="마술봉",
                tags=("탐험형", "에겐형"),
                reason="새로운 경험을 흥미롭게 바꾸는 모습을 닮았어요.",
            ),
        ),
        features=(
            FeatureData("분위기를 띄워요", "생각보다 빠른 행동력"),
            FeatureData("일단 해봐요", "생각보다 빠른 행동력"),
            FeatureData("변화를 즐겨요", "새로운 방식에 열린 태도"),
            FeatureData("탐험형", "직접 부딪히며 발견"),
        ),
        can_do=(
            "같이 놀아주세요",
            "새로운 제안을 던져주세요",
            "리액션을 아끼지 말아주세요",
            "자유롭게 맡겨주세요",
        ),
        warnings=(
            "똑같은 일만 반복시켜요",
            "선택을 지나치게 제한해요",
            "재미없는 분위기를 오래 끌어요",
            "아이디어를 시작부터 막아버려요",
        ),
        charging=ChargingData(
            score=90,
            description="친구들과 놀 때 가장 빠르게 충전돼요",
            activities=(
                ChargingActivityData("hangout", "친구들과 놀기"),
                ChargingActivityData("beer", "맥주 한 잔"),
                ChargingActivityData("travel", "여행가기"),
            ),
        ),
    )


def submit_assessment(submission: AssessmentSubmission) -> SubmissionResultData:
    if submission.assessment_version != ASSESSMENT_VERSION:
        raise UnsupportedAssessmentVersionError

    _validate_answers(submission)
    return _build_mock_result(submission.mbti, DEMO_RESULT_CODE)


def get_result(result_code: str) -> SubmissionResultData:
    if result_code != DEMO_RESULT_CODE:
        raise ResultNotFoundError
    return _build_mock_result(MbtiType.ENTP, DEMO_RESULT_CODE)
