from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from pakit.api.dependencies import (
    get_romantic_report_generator,
    get_romantic_report_repository,
)
from pakit.api.schemas.assessment_submissions import ErrorResponse
from pakit.api.schemas.romantic_reports import (
    ROMANTIC_REPORT_REQUEST_EXAMPLE,
    RomanticReportCreateInput,
    RomanticReportOutput,
)
from pakit.services.romantic_profile_builder import RomanticProfileUnavailableError
from pakit.services.romantic_report_generator import (
    RomanticReportGenerationError,
    RomanticReportGenerator,
)
from pakit.services.romantic_report_repository import (
    RelationshipProfileSourceUnavailableError,
    RomanticReportRepository,
)
from pakit.services.romantic_report_service import (
    CreateRomanticReportCommand,
    RomanticReportResultNotFoundError,
    create_romantic_report,
)

router = APIRouter(prefix="/relationship-reports", tags=["Relationship Report"])


@router.post(
    "/romantic",
    response_model=RomanticReportOutput,
    summary="연인 관계 설명서 생성",
    description=(
        "저장된 두 테스트 결과와 화면에서 입력받은 성별로 AI 연인 관계 설명서를 생성합니다. "
        "같은 입력과 생성 버전의 결과가 이미 있으면 AI를 다시 호출하지 않고 저장된 설명서를 "
        "반환합니다. 현재 품질 검증 단계라 결제 권한 확인은 아직 적용하지 않았습니다."
    ),
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "examples": {"romantic": {"value": ROMANTIC_REPORT_REQUEST_EXAMPLE}}
                }
            }
        }
    },
    responses={
        404: {"model": ErrorResponse, "description": "결과 코드를 찾을 수 없음"},
        409: {"model": ErrorResponse, "description": "원본 응답을 사용할 수 없음"},
        502: {"model": ErrorResponse, "description": "AI 생성 실패"},
        503: {"model": ErrorResponse, "description": "AI 생성 설정 없음"},
    },
)
async def generate_romantic_report(
    body: RomanticReportCreateInput,
    repository: Annotated[RomanticReportRepository, Depends(get_romantic_report_repository)],
    generator: Annotated[RomanticReportGenerator | None, Depends(get_romantic_report_generator)],
) -> RomanticReportOutput | JSONResponse:
    if generator is None:
        return _error(
            503,
            "RELATIONSHIP_REPORT_AI_NOT_CONFIGURED",
            "관계 설명서 AI 생성 설정이 필요합니다.",
        )
    try:
        report = await create_romantic_report(
            CreateRomanticReportCommand(
                mine_result_code=body.mine_result_code,
                partner_result_code=body.partner_result_code,
                mine_gender=body.mine_gender,
                partner_gender=body.partner_gender,
            ),
            repository,
            generator,
        )
    except RomanticReportResultNotFoundError:
        return _error(
            404, "RELATIONSHIP_REPORT_RESULT_NOT_FOUND", "테스트 결과를 찾을 수 없습니다."
        )
    except (RelationshipProfileSourceUnavailableError, RomanticProfileUnavailableError):
        return _error(
            409,
            "RELATIONSHIP_PROFILE_UNAVAILABLE",
            "이 결과의 원본 응답으로는 아직 관계 설명서를 만들 수 없습니다.",
        )
    except RomanticReportGenerationError:
        return _error(
            502,
            "RELATIONSHIP_REPORT_GENERATION_FAILED",
            "관계 설명서 생성에 실패했습니다. 잠시 후 다시 시도해주세요.",
        )
    return RomanticReportOutput(
        report_code=report.report_code,
        content=report.content,
        created_at=report.created_at,
    )


def _error(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )
