from secrets import token_urlsafe

from pakit.domain.assessment_contract import (
    ASSESSMENT_VERSION,
    QUESTION_CONTRACTS,
    AnswerKind,
)
from pakit.domain.assessment_submission import (
    AssessmentSubmission,
    CharacterStoryData,
    FeatureData,
    OverviewData,
    ResultParticipantData,
    SubmissionResultData,
    UnboxingItemData,
    UnboxingKitData,
)
from pakit.domain.characters import CHARACTERS
from pakit.services.assessment_classifier import (
    AssessmentClassification,
    classify_submission,
)
from pakit.services.charging_service import build_charging
from pakit.services.compatibility_service import (
    build_compatibility_profile,
    build_compatible_friends,
)
from pakit.services.emotional_processing_service import build_emotional_processing_feature
from pakit.services.handling_guide_service import build_handling_guide
from pakit.services.motivation_service import build_motivation_feature
from pakit.services.result_content import (
    CHARACTER_STORY_COPY,
    COMBINATION_COPY,
    MBTI_STRENGTH_COPY,
    OPENING_TOOL_COPY,
    PACKAGING_COPY,
    RELATIONSHIP_ROLE_COPY,
    RESULT_CONTENT_VERSION,
    FeatureCopy,
    UnboxingItemCopy,
)
from pakit.services.result_repository import ResultCodeConflictError, ResultRepository
from pakit.services.warning_service import build_warnings


class UnsupportedAssessmentVersionError(ValueError):
    pass


class InvalidSubmissionError(ValueError):
    pass


class ResultNotFoundError(LookupError):
    pass


class ResultCodeGenerationError(RuntimeError):
    pass


RESULT_CODE_GENERATION_ATTEMPTS = 5


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


def _unboxing_item(item: UnboxingItemCopy, asset_directory: str) -> UnboxingItemData:
    return UnboxingItemData(
        type=item.type,
        name=item.name,
        image_url=f"/assets/{asset_directory}/{item.type}.png",
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
    mbti_strength = MBTI_STRENGTH_COPY[submission.mbti]
    motivation_feature = build_motivation_feature(answers["step1.q11"], submission.mbti)
    emotional_processing_feature = build_emotional_processing_feature(
        classification.axis_scores.expression,
        classification.axis_scores.egen,
    )
    character_story = CHARACTER_STORY_COPY[submission.mbti]
    handling_guide = build_handling_guide(
        support_preference=answers["step1.q12"],
        mbti=submission.mbti,
        attachment_score=classification.axis_scores.attachment,
        conflict_style=answers["step2.q02"],
        affection_style=answers["step2.q08"],
    )
    warnings = build_warnings(
        protected_time=answers["step1.q05"],
        anger_trigger=answers["step1.q06"],
        mbti=submission.mbti,
    )
    charging = build_charging(
        holiday_choice=answers["step1.q07"],
        cancellation_choice=answers["step1.q08"],
    )

    return SubmissionResultData(
        result_code=result_code,
        participant=ResultParticipantData(nickname=submission.nickname),
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
            packaging=_unboxing_item(
                PACKAGING_COPY[classification.packaging_code],
                "packaging_boxes",
            ),
            opening_tool=_unboxing_item(
                OPENING_TOOL_COPY[classification.opening_tool_code],
                "opening_tools",
            ),
        ),
        features=tuple(
            _feature(item)
            for item in (
                motivation_feature,
                relationship_role,
                emotional_processing_feature,
                mbti_strength,
            )
        ),
        character_story=CharacterStoryData(
            title=character_story.title,
            description=character_story.description,
        ),
        can_do=handling_guide,
        warnings=warnings,
        charging=charging,
        compatible_friends=build_compatible_friends(
            submission.mbti,
            classification.axis_scores,
        ),
        compatibility_profile=build_compatibility_profile(
            mbti=submission.mbti,
            relationship_moment=answers["step1.q01"],
            relationship_strength=answers["step1.q02"],
            motivation=answers["step1.q11"],
            support_preference=answers["step1.q12"],
            conflict_style=answers["step2.q02"],
            affection_style=answers["step2.q08"],
        ),
    )


async def submit_assessment(
    submission: AssessmentSubmission,
    repository: ResultRepository,
) -> SubmissionResultData:
    if submission.assessment_version != ASSESSMENT_VERSION:
        raise UnsupportedAssessmentVersionError

    _validate_answers(submission)
    classification = classify_submission(submission)
    for _ in range(RESULT_CODE_GENERATION_ATTEMPTS):
        result = _build_result(submission, token_urlsafe(6), classification)
        try:
            await repository.save(
                result,
                assessment_version=submission.assessment_version,
                content_version=RESULT_CONTENT_VERSION,
            )
        except ResultCodeConflictError:
            continue
        return result
    raise ResultCodeGenerationError


async def get_result(result_code: str, repository: ResultRepository) -> SubmissionResultData:
    result = await repository.get(result_code)
    if result is None:
        raise ResultNotFoundError
    return result
