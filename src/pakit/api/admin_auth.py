import secrets
from typing import Annotated

from fastapi import Depends, HTTPException, Response, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from pakit.core.config import get_settings

basic = HTTPBasic(auto_error=False)


def require_admin(
    response: Response,
    credentials: Annotated[HTTPBasicCredentials | None, Depends(basic)],
) -> None:
    response.headers["Cache-Control"] = "no-store"
    settings = get_settings()
    if settings.admin_username is None or settings.admin_password is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="관리자 자격 증명이 설정되지 않았습니다.",
            headers={"Cache-Control": "no-store"},
        )
    supplied_username = credentials.username if credentials else ""
    supplied_password = credentials.password if credentials else ""
    expected_password = settings.admin_password.get_secret_value()
    username_matches = secrets.compare_digest(supplied_username, settings.admin_username)
    password_matches = secrets.compare_digest(supplied_password, expected_password)
    if not (username_matches and password_matches):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="관리자 인증이 필요합니다.",
            headers={"WWW-Authenticate": "Basic", "Cache-Control": "no-store"},
        )


AdminAccess = Annotated[None, Depends(require_admin)]
