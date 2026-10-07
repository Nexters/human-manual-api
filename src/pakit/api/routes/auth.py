from secrets import token_urlsafe
from typing import Annotated
from urllib.parse import urlsplit, urlunsplit

from fastapi import APIRouter, Cookie, Depends, Query, Request, Response, status
from fastapi.responses import JSONResponse, RedirectResponse

from pakit.api.auth_dependencies import (
    SESSION_COOKIE_NAME,
    get_kakao_client,
    get_session_signer,
    require_current_user,
)
from pakit.api.dependencies import get_user_repository
from pakit.api.schemas.auth import (
    CurrentUserOutput,
    MyCompatibilitiesOutput,
    MyCompatibilityItemOutput,
    MyResultItemOutput,
    MyResultsOutput,
    ResultSyncInput,
    ResultSyncOutput,
)
from pakit.core.config import Settings, get_settings
from pakit.core.kakao import KakaoOAuthError
from pakit.core.session import SessionSigner
from pakit.services.auth_service import KakaoClient, log_in_with_kakao
from pakit.services.user_repository import StoredUser, UserRepository

router = APIRouter(prefix="/auth", tags=["Auth"])
OAUTH_STATE_COOKIE_NAME = "pakit_oauth_state"
OAUTH_RETURN_TO_COOKIE_NAME = "pakit_oauth_return_to"
OAUTH_STATE_MAX_AGE_SECONDS = 600


def _secure_cookie(settings: Settings) -> bool:
    return settings.environment in {"staging", "production"}


@router.get("/kakao/login", summary="카카오 로그인 시작")
async def start_kakao_login(
    client: Annotated[KakaoClient, Depends(get_kakao_client)],
    settings: Annotated[Settings, Depends(get_settings)],
    return_to: Annotated[str | None, Query(max_length=500)] = None,
) -> RedirectResponse:
    state = token_urlsafe(32)
    response = RedirectResponse(client.authorization_url(state))
    response.set_cookie(
        OAUTH_STATE_COOKIE_NAME,
        state,
        max_age=OAUTH_STATE_MAX_AGE_SECONDS,
        httponly=True,
        secure=_secure_cookie(settings),
        samesite="lax",
    )
    safe_return_to = _safe_return_to(return_to)
    if safe_return_to is not None:
        response.set_cookie(
            OAUTH_RETURN_TO_COOKIE_NAME,
            safe_return_to,
            max_age=OAUTH_STATE_MAX_AGE_SECONDS,
            httponly=True,
            secure=_secure_cookie(settings),
            samesite="lax",
        )
    else:
        response.delete_cookie(OAUTH_RETURN_TO_COOKIE_NAME)
    return response


@router.get(
    "/kakao/callback",
    summary="카카오 로그인 콜백",
    include_in_schema=False,
    response_model=None,
)
async def complete_kakao_login(
    client: Annotated[KakaoClient, Depends(get_kakao_client)],
    signer: Annotated[SessionSigner, Depends(get_session_signer)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
    code: Annotated[str | None, Query()] = None,
    state: Annotated[str | None, Query()] = None,
    error: Annotated[str | None, Query()] = None,
    oauth_state: Annotated[str | None, Cookie(alias=OAUTH_STATE_COOKIE_NAME)] = None,
    return_to: Annotated[str | None, Cookie(alias=OAUTH_RETURN_TO_COOKIE_NAME)] = None,
) -> RedirectResponse | JSONResponse:
    if error is not None:
        return JSONResponse(status_code=400, content={"detail": "카카오 로그인이 취소됐습니다."})
    if code is None or state is None or oauth_state is None or state != oauth_state:
        return JSONResponse(status_code=400, content={"detail": "로그인 요청이 유효하지 않습니다."})
    try:
        user = await log_in_with_kakao(code, client, repository)
    except KakaoOAuthError:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={"detail": "카카오 로그인 처리에 실패했습니다."},
        )
    response = RedirectResponse(_frontend_redirect(settings.frontend_auth_redirect_url, return_to))
    response.delete_cookie(OAUTH_STATE_COOKIE_NAME)
    response.delete_cookie(OAUTH_RETURN_TO_COOKIE_NAME)
    response.set_cookie(
        SESSION_COOKIE_NAME,
        signer.create(user.id),
        max_age=settings.session_max_age_seconds,
        httponly=True,
        secure=_secure_cookie(settings),
        samesite="lax",
    )
    return response


def _safe_return_to(value: str | None) -> str | None:
    if value is None or not value.startswith("/") or value.startswith("//"):
        return None
    parsed = urlsplit(value)
    if parsed.scheme or parsed.netloc:
        return None
    return value


def _frontend_redirect(base_url: str, return_to: str | None) -> str:
    safe_path = _safe_return_to(return_to)
    if safe_path is None:
        return base_url
    base = urlsplit(base_url)
    target = urlsplit(safe_path)
    return urlunsplit((base.scheme, base.netloc, target.path, target.query, ""))


@router.get("/me", response_model=CurrentUserOutput, summary="현재 로그인 사용자 조회")
async def get_me(
    user: Annotated[StoredUser, Depends(require_current_user)],
) -> CurrentUserOutput:
    return CurrentUserOutput(user_id=user.id, created_at=user.created_at)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT, summary="로그아웃")
async def logout(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE_NAME)


@router.post(
    "/me/results/sync",
    response_model=ResultSyncOutput,
    summary="비회원 결과를 내 계정에 연결",
)
async def sync_my_results(
    data: ResultSyncInput,
    user: Annotated[StoredUser, Depends(require_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> ResultSyncOutput:
    result = await repository.sync_results(user.id, tuple(data.result_codes))
    return ResultSyncOutput(
        synced=list(result.synced),
        already_synced=list(result.already_synced),
        rejected=list(result.rejected),
    )


@router.get("/me/results", response_model=MyResultsOutput, summary="내 테스트 결과 목록")
async def list_my_results(
    request: Request,
    user: Annotated[StoredUser, Depends(require_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> MyResultsOutput:
    summaries = await repository.list_results(user.id)
    items = [
        MyResultItemOutput.from_summary(summary, public_base_url=str(request.base_url))
        for summary in summaries
    ]
    return MyResultsOutput(total=len(items), items=items)


@router.get(
    "/me/compatibilities",
    response_model=MyCompatibilitiesOutput,
    summary="내 친구 궁합 이력",
)
async def list_my_compatibilities(
    request: Request,
    user: Annotated[StoredUser, Depends(require_current_user)],
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> MyCompatibilitiesOutput:
    summaries = await repository.list_compatibilities(user.id)
    items = [
        MyCompatibilityItemOutput.from_summary(
            summary,
            public_base_url=str(request.base_url),
        )
        for summary in summaries
    ]
    return MyCompatibilitiesOutput(total=len(items), items=items)
