from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import JSONResponse

from pakit.api.dependencies import get_result_repository, get_usage_event_repository
from pakit.api.schemas.assessment_submissions import ErrorResponse
from pakit.api.schemas.compatibility import (
    COMPATIBILITY_RESPONSE_EXAMPLE,
    CompatibilityOutput,
)
from pakit.services.compatibility_service import (
    COMPATIBILITY_RULES_VERSION,
    CompatibilityNotFoundError,
    CompatibilityUnavailableError,
)
from pakit.services.compatibility_service import (
    get_compatibility as build_compatibility_result,
)
from pakit.services.result_repository import ResultRepository
from pakit.services.usage_event_repository import UsageEventRepository
from pakit.services.usage_tracking_service import record_compatibility_completed

router = APIRouter(prefix="/compatibility", tags=["Compatibility"])


@router.get(
    "",
    response_model=CompatibilityOutput,
    summary="친구 궁합 조회",
    description=(
        "내 결과 코드와 친구 결과 코드에 저장된 성향 축, 관계 답변 파생값, MBTI를 결합해 "
        "친구 궁합을 계산합니다. 테스트 답변과 성향 축이 계산의 70%, MBTI가 30%를 차지합니다."
    ),
    response_description="친구와의 궁합 화면에 필요한 계산 결과",
    responses={
        200: {
            "description": "친구와의 궁합 화면에 필요한 계산 결과",
            "content": {
                "application/json": {
                    "example": COMPATIBILITY_RESPONSE_EXAMPLE,
                }
            },
        },
        404: {"model": ErrorResponse, "description": "궁합 결과를 찾을 수 없음"},
        409: {"model": ErrorResponse, "description": "기존 결과에 궁합 계산 정보가 없음"},
    },
)
async def get_compatibility(
    request: Request,
    mine: Annotated[str, Query(description="내 테스트 결과 코드")],
    friend: Annotated[str, Query(description="친구 테스트 결과 코드")],
    repository: Annotated[ResultRepository, Depends(get_result_repository)],
    usage_repository: Annotated[UsageEventRepository, Depends(get_usage_event_repository)],
) -> CompatibilityOutput | JSONResponse:
    """저장된 두 테스트 결과로 친구 궁합을 계산합니다."""
    try:
        result = await build_compatibility_result(mine, friend, repository)
    except CompatibilityNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "COMPATIBILITY_NOT_FOUND",
                    "message": "친구 궁합 결과를 찾을 수 없습니다.",
                }
            },
        )
    except CompatibilityUnavailableError:
        return JSONResponse(
            status_code=409,
            content={
                "error": {
                    "code": "COMPATIBILITY_PROFILE_UNAVAILABLE",
                    "message": "이 결과는 궁합 기능 추가 전에 생성되어 궁합을 계산할 수 없습니다.",
                }
            },
        )
    await record_compatibility_completed(
        usage_repository,
        mine_result_code=mine,
        friend_result_code=friend,
        score=result.synergy.score,
        version=COMPATIBILITY_RULES_VERSION,
    )
    return CompatibilityOutput.from_domain_payload(
        asdict(result),
        public_base_url=str(request.base_url),
    )
