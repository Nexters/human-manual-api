from typing import Annotated

from fastapi import Depends, HTTPException, Request, status

from pakit.api.dependencies import get_user_repository
from pakit.core.config import Settings, get_settings
from pakit.core.kakao import KakaoOAuthClient
from pakit.core.session import InvalidSessionError, SessionSigner
from pakit.services.auth_service import KakaoClient
from pakit.services.user_repository import StoredUser, UserRepository

SESSION_COOKIE_NAME = "pakit_session"


def get_kakao_client(settings: Annotated[Settings, Depends(get_settings)]) -> KakaoClient:
    if (
        settings.kakao_rest_api_key is None
        or settings.kakao_client_secret is None
        or settings.kakao_redirect_uri is None
    ):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="카카오 로그인이 설정되지 않았습니다.",
        )
    return KakaoOAuthClient(
        rest_api_key=settings.kakao_rest_api_key,
        client_secret=settings.kakao_client_secret.get_secret_value(),
        redirect_uri=settings.kakao_redirect_uri,
    )


def get_session_signer(settings: Annotated[Settings, Depends(get_settings)]) -> SessionSigner:
    if settings.session_secret is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="로그인 세션이 설정되지 않았습니다.",
        )
    return SessionSigner(
        settings.session_secret.get_secret_value(),
        max_age_seconds=settings.session_max_age_seconds,
    )


async def get_optional_current_user(
    request: Request,
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> StoredUser | None:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token is None or settings.session_secret is None:
        return None
    signer = SessionSigner(
        settings.session_secret.get_secret_value(),
        max_age_seconds=settings.session_max_age_seconds,
    )
    try:
        user_id = signer.verify(token)
    except InvalidSessionError:
        return None
    return await repository.get_user(user_id)


async def require_current_user(
    user: Annotated[StoredUser | None, Depends(get_optional_current_user)],
) -> StoredUser:
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="로그인이 필요합니다.",
        )
    return user
