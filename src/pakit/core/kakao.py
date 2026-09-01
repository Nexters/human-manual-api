import asyncio
import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class KakaoOAuthError(RuntimeError):
    pass


@dataclass(frozen=True)
class KakaoOAuthClient:
    rest_api_key: str
    client_secret: str
    redirect_uri: str

    def authorization_url(self, state: str) -> str:
        query = urlencode(
            {
                "client_id": self.rest_api_key,
                "redirect_uri": self.redirect_uri,
                "response_type": "code",
                "state": state,
            }
        )
        return f"https://kauth.kakao.com/oauth/authorize?{query}"

    async def get_user_id(self, code: str) -> str:
        return await asyncio.to_thread(self._get_user_id, code)

    def _get_user_id(self, code: str) -> str:
        token_payload = self._request_json(
            Request(
                "https://kauth.kakao.com/oauth/token",
                data=urlencode(
                    {
                        "grant_type": "authorization_code",
                        "client_id": self.rest_api_key,
                        "redirect_uri": self.redirect_uri,
                        "code": code,
                        "client_secret": self.client_secret,
                    }
                ).encode(),
                headers={"Content-Type": "application/x-www-form-urlencoded;charset=utf-8"},
                method="POST",
            )
        )
        access_token = token_payload.get("access_token")
        if not isinstance(access_token, str) or not access_token:
            raise KakaoOAuthError("카카오 토큰 응답에 액세스 토큰이 없습니다.")
        user_payload = self._request_json(
            Request(
                "https://kapi.kakao.com/v2/user/me",
                headers={"Authorization": f"Bearer {access_token}"},
            )
        )
        kakao_user_id = user_payload.get("id")
        if not isinstance(kakao_user_id, int | str):
            raise KakaoOAuthError("카카오 사용자 응답에 회원번호가 없습니다.")
        return str(kakao_user_id)

    @staticmethod
    def _request_json(request: Request) -> dict[str, Any]:
        try:
            with urlopen(request, timeout=10) as response:
                payload = json.load(response)
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as error:
            raise KakaoOAuthError("카카오 인증 서버 요청에 실패했습니다.") from error
        if not isinstance(payload, dict):
            raise KakaoOAuthError("카카오 인증 서버 응답 형식이 올바르지 않습니다.")
        return payload
