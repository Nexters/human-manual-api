from hmac import compare_digest
from typing import Annotated

from fastapi import APIRouter, Depends, Header
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
from pakit.core.config import Settings, get_settings
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
        "반환합니다. 현재 베타 기간에는 X-Pakit-Beta-Code 헤더가 필요합니다."
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
        403: {"model": ErrorResponse, "description": "베타 접근 코드가 유효하지 않음"},
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
    settings: Annotated[Settings, Depends(get_settings)],
    beta_access_code: Annotated[str | None, Header(alias="X-Pakit-Beta-Code")] = None,
) -> RomanticReportOutput | JSONResponse:
    configured_beta_code = settings.romantic_report_beta_access_code
    if configured_beta_code is None:
        return _error(
            503,
            "RELATIONSHIP_REPORT_BETA_NOT_CONFIGURED",
            "관계 설명서 베타 접근 설정이 필요합니다.",
        )
    if beta_access_code is None or not compare_digest(
        beta_access_code,
        configured_beta_code.get_secret_value(),
    ):
        return _error(
            403,
            "RELATIONSHIP_REPORT_BETA_ACCESS_DENIED",
            "유효한 베타 접근 코드가 필요합니다.",
        )
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
