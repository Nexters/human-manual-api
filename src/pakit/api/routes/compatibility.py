from dataclasses import asdict
from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request
from fastapi.responses import JSONResponse

from pakit.api.dependencies import (
    get_compatibility_event_reader,
    get_result_repository,
    get_usage_event_repository,
)
from pakit.api.schemas.assessment_submissions import ErrorResponse
from pakit.api.schemas.compatibility import (
    COMPATIBILITY_RANKING_RESPONSE_EXAMPLE,
    COMPATIBILITY_RESPONSE_EXAMPLE,
    CompatibilityOutput,
    CompatibilityRankingOutput,
)
from pakit.api.schemas.image_urls import absolute_image_url
from pakit.services.compatibility_ranking_service import (
    CompatibilityRankingNotFoundError,
    get_compatibility_ranking,
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
from pakit.services.usage_event_repository import CompatibilityEventReader, UsageEventRepository
from pakit.services.usage_tracking_service import record_compatibility_completed

router = APIRouter(prefix="/compatibility", tags=["Compatibility"])
ranking_router = APIRouter(prefix="/results", tags=["Compatibility"])


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


@ranking_router.get(
    "/{result_code}/compatibility-ranking",
    response_model=CompatibilityRankingOutput,
    summary="내 케미 랭킹 조회",
    description=(
        "결과 코드와 케미 테스트를 완료한 고유 상대를 최신 궁합 점수의 내림차순으로 "
        "반환합니다. 같은 상대와 여러 번 테스트한 경우 가장 최근 성공 기록만 사용하며, "
        "같은 점수는 같은 순위로 표시합니다."
    ),
    response_description="내 결과 코드와 케미 테스트를 완료한 상대의 점수 랭킹",
    responses={
        200: {
            "description": "내 결과 코드와 케미 테스트를 완료한 상대의 점수 랭킹",
            "content": {
                "application/json": {
                    "example": COMPATIBILITY_RANKING_RESPONSE_EXAMPLE,
                }
            },
        },
        404: {"model": ErrorResponse, "description": "기준 결과를 찾을 수 없음"},
    },
)
async def get_my_compatibility_ranking(
    request: Request,
    result_code: Annotated[
        str,
        Path(
            min_length=8,
            max_length=8,
            pattern=r"^[A-Za-z0-9_-]{8}$",
            description="랭킹 기준이 되는 내 결과 코드",
        ),
    ],
    result_repository: Annotated[ResultRepository, Depends(get_result_repository)],
    event_reader: Annotated[
        CompatibilityEventReader,
        Depends(get_compatibility_event_reader),
    ],
) -> CompatibilityRankingOutput | JSONResponse:
    try:
        ranking = await get_compatibility_ranking(
            result_code,
            result_repository,
            event_reader,
        )
    except CompatibilityRankingNotFoundError:
        return JSONResponse(
            status_code=404,
            content={
                "error": {
                    "code": "COMPATIBILITY_RANKING_NOT_FOUND",
                    "message": "케미 랭킹의 기준 결과를 찾을 수 없습니다.",
                }
            },
        )

    payload = asdict(ranking)
    for item in payload["rankings"]:
        item["image_url"] = absolute_image_url(
            item["image_url"],
            public_base_url=str(request.base_url),
        )
    return CompatibilityRankingOutput.model_validate(payload)
