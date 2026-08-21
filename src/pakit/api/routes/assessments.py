from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, Request
from fastapi.responses import JSONResponse

from pakit.api.dependencies import get_result_repository
from pakit.api.schemas.assessment_submissions import (
    ASSESSMENT_SUBMISSION_EXAMPLE,
    ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE,
    AssessmentSubmissionInput,
    AssessmentSubmissionOutput,
    CompletedTestCountOutput,
    ErrorResponse,
)
from pakit.services.result_repository import ResultRepository
from pakit.services.submission_service import (
    InvalidSubmissionError,
    ResultNotFoundError,
    UnsupportedAssessmentVersionError,
    count_completed_tests,
    get_result,
    submit_assessment,
)

router = APIRouter(prefix="/tests", tags=["Test"])
results_router = APIRouter(prefix="/results", tags=["Test"])


@router.get(
    "/submissions/count",
    response_model=CompletedTestCountOutput,
    summary="누적 테스트 완료 수 조회",
    description="결과 저장까지 성공한 누적 테스트 수를 반환합니다.",
)
async def get_completed_test_count(
    repository: Annotated[ResultRepository, Depends(get_result_repository)],
) -> CompletedTestCountOutput:
    return CompletedTestCountOutput(completed_count=await count_completed_tests(repository))


@router.post(
    "/submissions",
    response_model=AssessmentSubmissionOutput,
    summary="테스트 결과 제출",
    description=(
        "테스트 완료 화면에서 프론트엔드가 **한 번 호출하는 API**입니다.\n\n"
        "### 요청 데이터\n"
        "- `assessment_version`: 프론트에 적용한 문항 계약 버전\n"
        "- `participant.nickname`: 결과에 표시할 이름 또는 닉네임\n"
        "- `answers`: `docs/assessment-identifiers.v1.json`에 정의된 20개 문항의 답변\n"
        "- `mbti`: 화면에서 선택한 네 글자 MBTI 유형. 예: `ENTP`\n\n"
        "### 서버에서 확인하는 항목\n"
        "- 테스트 버전이 현재 서버 버전과 일치하는지 확인합니다.\n"
        "- 20개 문항이 빠짐없이 한 번씩 제출됐는지 확인합니다.\n"
        "- 문항별 `value`가 계약에 맞는 문자열 또는 정수인지 확인합니다.\n"
        "- STEP 2 답변으로 성향 점수, 형용사, 포장 상자와 개봉 도구를 결정합니다.\n"
        "- 선택한 MBTI에 맞는 장난감 명사, 캐릭터와 이미지를 결정합니다.\n\n"
        "### 현재 응답 범위\n"
        "결과 조회용 `result_code`, 표시 이름인 `participant`와 결과 페이지에 필요한 "
        "`overview`, `unboxing_kit`, "
        "`features`, `character_story`, `can_do`, "
        "`warnings`, `charging`을 반환합니다. 형용사·장난감·캐릭터·이미지·성향 점수·"
        "포장 상자·개봉 도구·핵심 특징·장난감 이야기는 제출값으로 결정됩니다. "
        "희귀도·상단 태그·"
        "사용 방법과 주의사항, 충전 설명과 활동도 제출값으로 결정됩니다. 계산 규칙이 "
        "확정되지 않은 충전 점수는 반환하지 않습니다."
    ),
    response_description="규칙 기반 분류와 목업 콘텐츠를 조합한 테스트 결과",
    responses={
        200: {
            "description": "규칙 기반 분류와 목업 콘텐츠를 조합한 테스트 결과",
            "content": {
                "application/json": {
                    "example": ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE,
                }
            },
        },
        409: {"model": ErrorResponse, "description": "지원하지 않는 테스트 버전"},
        422: {"model": ErrorResponse, "description": "테스트 답변 검증 실패"},
    },
)
async def create_assessment_submission(
    request: Request,
    data: Annotated[
        AssessmentSubmissionInput,
        Body(
            openapi_examples={
                "complete": {
                    "summary": "20개 문항과 MBTI 입력을 모두 포함한 예시",
                    "description": (
                        "`docs/assessment-identifiers.v1.json`에 게시된 실제 문항·선택지 "
                        "ID를 사용한 유효한 요청입니다. Swagger의 'Try it out'에서 바로 "
                        "실행할 수 있습니다."
                    ),
                    "value": ASSESSMENT_SUBMISSION_EXAMPLE,
                }
            }
        ),
    ],
    repository: Annotated[ResultRepository, Depends(get_result_repository)],
) -> AssessmentSubmissionOutput | JSONResponse:
    """완료한 테스트 답변을 검증하고 규칙 기반 결과를 반환합니다."""
    try:
        result = await submit_assessment(data.to_domain(), repository)
    except UnsupportedAssessmentVersionError:
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": "ASSESSMENT_VERSION_UNSUPPORTED",
                    "message": "지원하지 않는 테스트 버전입니다.",
                }
            },
        )
    except InvalidSubmissionError as error:
        return JSONResponse(
            status_code=422,
            content={
                "error": {
                    "code": "ASSESSMENT_ANSWERS_INVALID",
                    "message": str(error),
                }
            },
        )
    return AssessmentSubmissionOutput.from_domain(
        result,
        public_base_url=str(request.base_url),
    )


@results_router.get(
    "/{result_code}",
    response_model=AssessmentSubmissionOutput,
    summary="테스트 결과 조회",
    description=(
        "테스트 제출 API에서 받은 `result_code`로 결과를 조회합니다. "
        "결과는 생성 당시의 내용 그대로 데이터베이스에 저장됩니다."
    ),
    response_description="result_code에 해당하는 테스트 결과",
    responses={
        200: {
            "description": "result_code에 해당하는 테스트 결과",
            "content": {
                "application/json": {
                    "example": ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE,
                }
            },
        },
        404: {"model": ErrorResponse, "description": "결과를 찾을 수 없음"},
    },
)
async def get_assessment_result(
    request: Request,
    result_code: Annotated[
        str,
        Path(description="테스트 제출 응답에서 받은 결과 조회 코드"),
    ],
    repository: Annotated[ResultRepository, Depends(get_result_repository)],
) -> AssessmentSubmissionOutput | JSONResponse:
    """고유 결과 코드로 저장된 테스트 결과를 조회합니다."""
    try:
        result = await get_result(result_code, repository)
    except ResultNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "TEST_RESULT_NOT_FOUND",
                    "message": "테스트 결과를 찾을 수 없습니다.",
                }
            },
        )
    return AssessmentSubmissionOutput.from_domain(
        result,
        public_base_url=str(request.base_url),
    )
