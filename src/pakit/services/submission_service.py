from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_contract import (
    ASSESSMENT_VERSION,
    QUESTION_CONTRACTS,
    AnswerKind,
)
from pakit.domain.assessment_submission import (
    AssessmentSubmission,
    ChargingActivityData,
    ChargingData,
    FeatureData,
    OverviewData,
    SubmissionResultData,
    SubmittedAnswer,
    UnboxingItemData,
    UnboxingKitData,
)
from pakit.domain.characters import CHARACTERS
from pakit.services.assessment_classifier import (
    AssessmentClassification,
    classify_submission,
)
from pakit.services.motivation_service import build_motivation_feature
from pakit.services.result_content import (
    COMBINATION_COPY,
    MBTI_FEATURE_COPY,
    OPENING_TOOL_COPY,
    PACKAGING_COPY,
    RELATIONSHIP_ROLE_COPY,
    FeatureCopy,
    UnboxingItemCopy,
)


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
        elif contract.minimum is not None and answer.value < contract.minimum:
            raise InvalidSubmissionError(
                f"{answer.question_id}의 value는 {contract.minimum} 이상이어야 합니다."
            )
        elif contract.maximum is not None and answer.value > contract.maximum:
            raise InvalidSubmissionError(
                f"{answer.question_id}의 value는 {contract.maximum} 이하여야 합니다."
            )


def _unboxing_item(item: UnboxingItemCopy) -> UnboxingItemData:
    return UnboxingItemData(
        type=item.type,
        name=item.name,
        tags=item.tags,
        reason=item.reason,
    )


def _feature(item: FeatureCopy) -> FeatureData:
    return FeatureData(title=item.title, description=item.description)


def _build_result(
    submission: AssessmentSubmission,
    result_code: str,
    classification: AssessmentClassification,
) -> SubmissionResultData:
    character = CHARACTERS[submission.mbti]
    adjective = classification.adjective
    combination_copy = COMBINATION_COPY[
        (classification.packaging_code, classification.opening_tool_code)
    ]
    answers = {answer.question_id: str(answer.value) for answer in submission.answers}
    relationship_role = RELATIONSHIP_ROLE_COPY[(answers["step1.q01"], answers["step1.q02"])]
    mbti_features = MBTI_FEATURE_COPY[submission.mbti]
    motivation_feature = build_motivation_feature(answers["step1.q11"], submission.mbti)

    return SubmissionResultData(
        result_code=result_code,
        overview=OverviewData(
            rarity="상위 4%",
            adjective=adjective,
            noun=character.noun,
            result_name=f"{adjective} {character.noun}",
            character_id=character.code,
            image_url=f"/assets/{character.asset_key}",
            tags=("도파민 MAX", "장난꾸러기", "혼자서도 잘 놀아요"),
        ),
        unboxing_kit=UnboxingKitData(
            axis_scores=classification.axis_scores,
            title=combination_copy.title,
            description=combination_copy.description,
            packaging=_unboxing_item(PACKAGING_COPY[classification.packaging_code]),
            opening_tool=_unboxing_item(OPENING_TOOL_COPY[classification.opening_tool_code]),
        ),
        features=tuple(
            _feature(item) for item in (motivation_feature, relationship_role, *mbti_features)
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
    result = _build_result(
        submission,
        DEMO_RESULT_CODE,
        classify_submission(submission),
    )
    _DEMO_RESULTS[DEMO_RESULT_CODE] = result
    return result


def get_result(result_code: str) -> SubmissionResultData:
    try:
        return _DEMO_RESULTS[result_code]
    except KeyError:
        raise ResultNotFoundError from None


_DEFAULT_DEMO_SUBMISSION = AssessmentSubmission(
    assessment_version=ASSESSMENT_VERSION,
    nickname="송송",
    answers=(
        SubmittedAnswer("step1.q01", "decision"),
        SubmittedAnswer("step1.q02", "set_direction"),
        SubmittedAnswer("step1.q11", "curiosity"),
        SubmittedAnswer("step2.q01", "inspect_profile"),
        SubmittedAnswer("step2.q02", "hint_and_wait"),
        SubmittedAnswer("step2.q03", "rehearse_with_ai"),
        SubmittedAnswer("step2.q04", 50),
        SubmittedAnswer("step2.q05", "share_everything"),
        SubmittedAnswer("step2.q06", 247),
        SubmittedAnswer("step2.q07", "decorate_for_mood"),
        SubmittedAnswer("step2.q08", "express_with_words"),
        SubmittedAnswer("step2.q09", "ruminate"),
        SubmittedAnswer("step2.q10", "order_familiar_menu"),
        SubmittedAnswer("step2.q11", "order_familiar_stores"),
        SubmittedAnswer("step2.q12", "press"),
    ),
    mbti=MbtiType.ENTP,
)
_DEMO_RESULTS: dict[str, SubmissionResultData] = {
    DEMO_RESULT_CODE: _build_result(
        _DEFAULT_DEMO_SUBMISSION,
        DEMO_RESULT_CODE,
        classify_submission(_DEFAULT_DEMO_SUBMISSION),
    )
}
