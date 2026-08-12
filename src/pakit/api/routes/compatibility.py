from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Query
from fastapi.responses import JSONResponse

from pakit.api.schemas.assessment_submissions import ErrorResponse
from pakit.api.schemas.compatibility import (
    COMPATIBILITY_RESPONSE_EXAMPLE,
    CompatibilityOutput,
)
from pakit.services.compatibility_service import (
    CompatibilityNotFoundError,
    get_mock_compatibility,
)

router = APIRouter(prefix="/compatibility", tags=["Compatibility"])


@router.get(
    "",
    response_model=CompatibilityOutput,
    summary="친구 궁합 조회",
    description=(
        "내 결과 코드와 친구 결과 코드로 친구 궁합을 조회합니다. "
        "현재 목업에서는 `mine=demo-result-code`, `friend=demo-friend-code`만 사용할 수 있으며 "
        "궁합 점수와 문구는 고정 데모 값입니다."
    ),
    response_description="친구와의 궁합 화면에 필요한 목업 결과",
    responses={
        200: {
            "description": "친구와의 궁합 화면에 필요한 목업 결과",
            "content": {
                "application/json": {
                    "example": COMPATIBILITY_RESPONSE_EXAMPLE,
                }
            },
        },
        404: {"model": ErrorResponse, "description": "궁합 결과를 찾을 수 없음"},
    },
)
async def get_compatibility(
    mine: Annotated[str, Query(description="내 테스트 결과 코드")],
    friend: Annotated[str, Query(description="친구 테스트 결과 코드")],
) -> CompatibilityOutput | JSONResponse:
    """고정 목업 코드 두 개로 친구 궁합을 조회합니다."""
    try:
        result = get_mock_compatibility(mine, friend)
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
    return CompatibilityOutput.model_validate(asdict(result))
