from typing import Annotated

from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse

from pakit.api.schemas.assessment_submissions import (
    ASSESSMENT_SUBMISSION_EXAMPLE,
    AssessmentSubmissionInput,
    AssessmentSubmissionOutput,
    ErrorResponse,
)
from pakit.domain.assessment import AssessmentInput, AssessmentResult
from pakit.services.result_builder import build_assessment_result
from pakit.services.submission_service import (
    InvalidSubmissionError,
    UnsupportedAssessmentVersionError,
    submit_assessment,
)

router = APIRouter(prefix="/tests", tags=["Test"])


@router.post(
    "/submissions",
    response_model=AssessmentSubmissionOutput,
    summary="테스트 결과 제출",
    description=(
        "테스트 완료 화면에서 프론트엔드가 **한 번 호출하는 API**입니다.\n\n"
        "### 요청 데이터\n"
        "- `assessment_version`: 프론트에 적용한 문항 계약 버전\n"
        "- `participant.nickname`: 결과에 표시할 이름 또는 닉네임\n"
        "- `answers`: `docs/assessment-identifiers.v1.json`에 정의된 22개 문항의 답변\n"
        "- `mbti_scores`: MBTI 네 지표의 퍼센트. 각 값은 "
        "`0`, `20`, `40`, `60`, `80`, `100` 중 하나\n\n"
        "### 서버에서 확인하는 항목\n"
        "- 테스트 버전이 현재 서버 버전과 일치하는지 확인합니다.\n"
        "- 22개 문항이 빠짐없이 한 번씩 제출됐는지 확인합니다.\n"
        "- 문항별 답변 타입과 선택지 ID가 계약에 맞는지 확인합니다.\n"
        "- MBTI 퍼센트로 16개 유형 중 하나를 판정해 최종 캐릭터를 선택합니다.\n\n"
        "### 현재 응답 범위\n"
        "현재는 프론트엔드 개발을 위한 **목업 결과**를 반환합니다. "
        "`mode`는 `mock`, `persisted`는 `false`, `result_id`는 `null`입니다. "
        "캐릭터는 실제 MBTI 매핑 결과이며, 제품명·언박싱·사용 설명서 문구는 임시 데이터입니다."
    ),
    response_description="검증을 통과한 테스트 목업 결과",
    responses={
        409: {"model": ErrorResponse, "description": "지원하지 않는 테스트 버전"},
        422: {"model": ErrorResponse, "description": "테스트 답변 검증 실패"},
    },
)
async def create_assessment_submission(
    data: Annotated[
        AssessmentSubmissionInput,
        Body(
            openapi_examples={
                "complete": {
                    "summary": "22개 문항과 MBTI 입력을 모두 포함한 예시",
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
) -> AssessmentSubmissionOutput | JSONResponse:
    """완료한 테스트 답변을 검증하고 목업 결과를 반환합니다."""
    try:
        result = submit_assessment(data.to_domain())
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
    return AssessmentSubmissionOutput.from_domain(result)


@router.post(
    "/evaluate",
    response_model=AssessmentResult,
    summary="테스트 분류 규칙 확인",
    description=(
        "백엔드 분류 규칙 확인용 API입니다. MBTI 유형과 네 가지 성향 축 점수를 받아 "
        "포장 유형, 개봉 도구, 캐릭터 명사와 임시 형용사를 계산합니다."
    ),
    response_description="분류 규칙을 적용한 결과",
)
async def evaluate_assessment(data: AssessmentInput) -> AssessmentResult:
    """현재 PRD의 분류 규칙으로 테스트 결과를 계산합니다."""
    return build_assessment_result(data)
