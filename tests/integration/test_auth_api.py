from collections.abc import Iterator
from datetime import UTC, datetime
from urllib.parse import parse_qs, urlparse

import pytest
from fastapi.testclient import TestClient
from pydantic import SecretStr

from pakit.api.auth_dependencies import get_kakao_client
from pakit.api.dependencies import get_result_repository, get_user_repository
from pakit.api.schemas.assessment_submissions import ASSESSMENT_SUBMISSION_EXAMPLE
from pakit.core.config import Settings, get_settings
from pakit.core.kakao import KakaoOAuthError
from pakit.domain.assessment_submission import AssessmentSubmission, SubmissionResultData
from pakit.main import app
from pakit.services.user_repository import (
    ResultSyncSummary,
    StoredUser,
    UserCompatibilitySummary,
    UserResultSummary,
)

NOW = datetime(2026, 9, 1, tzinfo=UTC)


class FakeKakaoClient:
    def authorization_url(self, state: str) -> str:
        return f"https://kauth.kakao.com/oauth/authorize?state={state}"

    async def get_user_id(self, code: str) -> str:
        assert code == "authorization-code"
        return "kakao-123"


class FailingKakaoClient(FakeKakaoClient):
    async def get_user_id(self, code: str) -> str:
        raise KakaoOAuthError


class FakeUserRepository:
    def __init__(self) -> None:
        self.user: StoredUser | None = None
        self.synced_codes: tuple[str, ...] = ()
        self.result = UserResultSummary(
            result_code="MINE0001",
            nickname="해서니",
            result_name="테스트용 팽이",
            noun="팽이",
            character_id="spinning_top",
            image_url="/assets/characters/spinning_top.png",
            created_at=NOW,
        )
        self.friend = UserResultSummary(
            result_code="FRIEND01",
            nickname="선우",
            result_name="테스트용 망원경",
            noun="망원경",
            character_id="telescope",
            image_url="/assets/characters/telescope.png",
            created_at=NOW,
        )

    async def upsert_kakao_user(self, kakao_user_id: str) -> StoredUser:
        assert kakao_user_id == "kakao-123"
        self.user = StoredUser(id=42, created_at=NOW, last_logged_in_at=NOW)
        return self.user

    async def get_user(self, user_id: int) -> StoredUser | None:
        return self.user if self.user is not None and user_id == self.user.id else None

    async def sync_results(
        self,
        user_id: int,
        result_codes: tuple[str, ...],
    ) -> ResultSyncSummary:
        assert user_id == 42
        self.synced_codes = result_codes
        return ResultSyncSummary(
            synced=("MINE0001",),
            already_synced=("FRIEND01",),
            rejected=("UNKNOWN1",),
        )

    async def list_results(self, user_id: int) -> list[UserResultSummary]:
        assert user_id == 42
        return [self.result]

    async def list_compatibilities(self, user_id: int) -> list[UserCompatibilitySummary]:
        assert user_id == 42
        return [
            UserCompatibilitySummary(
                mine=self.result,
                friend=self.friend,
                score=91,
                tested_at=NOW,
            )
        ]


class FakeResultRepository:
    def __init__(self) -> None:
        self.results: dict[str, SubmissionResultData] = {}
        self.saved_user_ids: list[int | None] = []

    async def save(
        self,
        result: SubmissionResultData,
        *,
        submission: AssessmentSubmission,
        content_version: str,
        user_id: int | None = None,
    ) -> None:
        self.results[result.result_code] = result
        self.saved_user_ids.append(user_id)

    async def get(self, result_code: str) -> SubmissionResultData | None:
        return self.results.get(result_code)

    async def count(self) -> int:
        return len(self.results)


@pytest.fixture
def auth_client() -> Iterator[tuple[TestClient, FakeUserRepository, FakeResultRepository]]:
    repository = FakeUserRepository()
    result_repository = FakeResultRepository()
    settings = Settings(
        _env_file=None,
        environment="test",
        kakao_rest_api_key="rest-key",
        kakao_client_secret=SecretStr("client-secret"),
        kakao_redirect_uri="https://api.pakit.kr/api/auth/kakao/callback",
        frontend_auth_redirect_url="https://pakit.kr/auth/complete",
        session_secret=SecretStr("test-session-secret"),
        session_max_age_seconds=3600,
    )
    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_kakao_client] = lambda: FakeKakaoClient()
    app.dependency_overrides[get_user_repository] = lambda: repository
    app.dependency_overrides[get_result_repository] = lambda: result_repository
    with TestClient(app) as client:
        yield client, repository, result_repository
    app.dependency_overrides.pop(get_settings, None)
    app.dependency_overrides.pop(get_kakao_client, None)
    app.dependency_overrides.pop(get_user_repository, None)
    app.dependency_overrides.pop(get_result_repository, None)


def _log_in(client: TestClient) -> None:
    started = client.get("/api/auth/kakao/login", follow_redirects=False)
    state = parse_qs(urlparse(started.headers["location"]).query)["state"][0]
    completed = client.get(
        "/api/auth/kakao/callback",
        params={"code": "authorization-code", "state": state},
        follow_redirects=False,
    )
    assert completed.status_code == 307
    assert completed.headers["location"] == "https://pakit.kr/auth/complete"


def test_logs_in_syncs_local_results_and_lists_account_history(
    auth_client: tuple[TestClient, FakeUserRepository, FakeResultRepository],
) -> None:
    client, repository, result_repository = auth_client
    assert client.get("/api/auth/me").status_code == 401
    guest_submission = client.post(
        "/api/tests/submissions",
        json=ASSESSMENT_SUBMISSION_EXAMPLE,
    )
    assert guest_submission.status_code == 200
    assert result_repository.saved_user_ids == [None]

    _log_in(client)
    user_submission = client.post(
        "/api/tests/submissions",
        json=ASSESSMENT_SUBMISSION_EXAMPLE,
    )
    assert user_submission.status_code == 200
    assert result_repository.saved_user_ids == [None, 42]

    me = client.get("/api/auth/me")
    synced = client.post(
        "/api/auth/me/results/sync",
        json={"result_codes": ["MINE0001", "FRIEND01", "UNKNOWN1"]},
    )
    results = client.get("/api/auth/me/results")
    compatibilities = client.get("/api/auth/me/compatibilities")

    assert me.json()["user_id"] == 42
    assert synced.json() == {
        "synced": ["MINE0001"],
        "already_synced": ["FRIEND01"],
        "rejected": ["UNKNOWN1"],
    }
    assert repository.synced_codes == ("MINE0001", "FRIEND01", "UNKNOWN1")
    assert results.json()["items"][0]["image_url"] == (
        "https://testserver/assets/characters/spinning_top.png"
    )
    assert compatibilities.json()["items"][0]["score"] == 91

    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_rejects_invalid_oauth_state_and_invalid_result_codes(
    auth_client: tuple[TestClient, FakeUserRepository, FakeResultRepository],
) -> None:
    client, _, _ = auth_client
    client.get("/api/auth/kakao/login", follow_redirects=False)

    invalid_callback = client.get(
        "/api/auth/kakao/callback",
        params={"code": "authorization-code", "state": "wrong"},
    )
    cancelled = client.get(
        "/api/auth/kakao/callback",
        params={"error": "access_denied"},
    )

    assert invalid_callback.status_code == 400
    assert cancelled.status_code == 400

    _log_in(client)
    invalid_sync = client.post(
        "/api/auth/me/results/sync",
        json={"result_codes": ["too-short"]},
    )
    assert invalid_sync.status_code == 422


def test_returns_bad_gateway_when_kakao_exchange_fails(
    auth_client: tuple[TestClient, FakeUserRepository, FakeResultRepository],
) -> None:
    client, _, _ = auth_client
    app.dependency_overrides[get_kakao_client] = lambda: FailingKakaoClient()
    started = client.get("/api/auth/kakao/login", follow_redirects=False)
    state = parse_qs(urlparse(started.headers["location"]).query)["state"][0]

    response = client.get(
        "/api/auth/kakao/callback",
        params={"code": "authorization-code", "state": state},
    )

    assert response.status_code == 502


def test_returns_to_safe_frontend_path_after_login(
    auth_client: tuple[TestClient, FakeUserRepository, FakeResultRepository],
) -> None:
    client, _, _ = auth_client
    started = client.get(
        "/api/auth/kakao/login",
        params={"return_to": "/compatibility/checkout?mine=MINE0001&friend=FRIEND01"},
        follow_redirects=False,
    )
    state = parse_qs(urlparse(started.headers["location"]).query)["state"][0]

    completed = client.get(
        "/api/auth/kakao/callback",
        params={"code": "authorization-code", "state": state},
        follow_redirects=False,
    )

    assert completed.status_code == 307
    assert completed.headers["location"] == (
        "https://pakit.kr/compatibility/checkout?mine=MINE0001&friend=FRIEND01"
    )


def test_ignores_external_login_return_url(
    auth_client: tuple[TestClient, FakeUserRepository, FakeResultRepository],
) -> None:
    client, _, _ = auth_client
    started = client.get(
        "/api/auth/kakao/login",
        params={"return_to": "https://evil.example/steal"},
        follow_redirects=False,
    )
    state = parse_qs(urlparse(started.headers["location"]).query)["state"][0]

    completed = client.get(
        "/api/auth/kakao/callback",
        params={"code": "authorization-code", "state": state},
        follow_redirects=False,
    )

    assert completed.headers["location"] == "https://pakit.kr/auth/complete"
