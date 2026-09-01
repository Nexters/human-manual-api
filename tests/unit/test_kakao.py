from urllib.parse import parse_qs, urlparse

import pytest
from pytest import MonkeyPatch

from pakit.core.kakao import KakaoOAuthClient, KakaoOAuthError


def _client() -> KakaoOAuthClient:
    return KakaoOAuthClient("rest-key", "client-secret", "https://api.pakit.kr/callback")


def test_builds_kakao_authorization_url_with_state() -> None:
    url = urlparse(_client().authorization_url("csrf-state"))

    assert f"{url.scheme}://{url.netloc}{url.path}" == "https://kauth.kakao.com/oauth/authorize"
    assert parse_qs(url.query) == {
        "client_id": ["rest-key"],
        "redirect_uri": ["https://api.pakit.kr/callback"],
        "response_type": ["code"],
        "state": ["csrf-state"],
    }


def test_exchanges_code_and_returns_kakao_user_id(monkeypatch: MonkeyPatch) -> None:
    payloads = iter(({"access_token": "access-token"}, {"id": 123456789}))
    monkeypatch.setattr(
        KakaoOAuthClient,
        "_request_json",
        staticmethod(lambda request: next(payloads)),
    )

    assert _client()._get_user_id("authorize-code") == "123456789"


def test_rejects_missing_kakao_access_token(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        KakaoOAuthClient,
        "_request_json",
        staticmethod(lambda request: {}),
    )

    with pytest.raises(KakaoOAuthError, match="액세스 토큰"):
        _client()._get_user_id("authorize-code")


def test_rejects_missing_kakao_user_id(monkeypatch: MonkeyPatch) -> None:
    payloads = iter(({"access_token": "access-token"}, {}))
    monkeypatch.setattr(
        KakaoOAuthClient,
        "_request_json",
        staticmethod(lambda request: next(payloads)),
    )

    with pytest.raises(KakaoOAuthError, match="회원번호"):
        _client()._get_user_id("authorize-code")
