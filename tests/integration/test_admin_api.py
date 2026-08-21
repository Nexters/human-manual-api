from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient
from pydantic import SecretStr
from pytest import MonkeyPatch

import pakit.api.admin_auth as admin_auth
import pakit.api.routes.admin as admin_routes
from pakit.api.dependencies import get_admin_repository
from pakit.core.config import Settings
from pakit.main import create_app
from pakit.services.admin_repository import StoredResult, StoredUsageEvent


def _result(code: str, mbti: str, created_at: datetime, nickname: str) -> StoredResult:
    return StoredResult(
        result_code=code,
        assessment_version="questions-v1",
        content_version="content-v1",
        created_at=created_at,
        snapshot={
            "participant": {"nickname": nickname},
            "overview": {
                "result_name": "팽이 지은",
                "character_id": "spinning_top",
                "tags": ["장난꾸러기", "도파민 MAX", "혼자서도 잘 놀아요"],
            },
            "unboxing_kit": {
                "axis_scores": {
                    "attachment": 25,
                    "expression": 75,
                    "routine": 10,
                    "egen": 50,
                }
            },
            "compatibility_profile": {"mbti": mbti},
        },
    )


class FakeAdminRepository:
    def __init__(self, results: list[StoredResult], events: list[StoredUsageEvent]) -> None:
        self.results = results
        self.events = events

    async def list_results(self) -> list[StoredResult]:
        return self.results

    async def get_result(self, result_code: str) -> StoredResult | None:
        return next((result for result in self.results if result.result_code == result_code), None)

    async def list_usage_events(self) -> list[StoredUsageEvent]:
        return self.events


def _event(
    name: str,
    code: str,
    occurred_at: datetime,
    *,
    friend: str | None = None,
    score: int | None = None,
) -> StoredUsageEvent:
    return StoredUsageEvent(
        event_name=name,  # type: ignore[arg-type]
        result_code=code,
        related_result_code=friend,
        compatibility_score=score,
        compatibility_version="rules-v1" if score else None,
        occurred_at=occurred_at,
    )


def _client(monkeypatch: MonkeyPatch, *, configured: bool = True) -> TestClient:
    started_at = datetime(2026, 8, 20, tzinfo=UTC)
    settings = Settings(
        admin_username="operator" if configured else None,
        admin_password=SecretStr("correct-horse") if configured else None,
        usage_tracking_started_at=started_at,
    )
    monkeypatch.setattr(admin_auth, "get_settings", lambda: settings)
    monkeypatch.setattr(admin_routes, "get_settings", lambda: settings)
    application = create_app()
    results = [
        _result("RESULT01", "ENTP", started_at, "해서니"),
        _result("RESULT02", "INTJ", started_at + timedelta(minutes=1), "선우"),
    ]
    events = [
        _event("result_viewed", "RESULT01", started_at + timedelta(hours=1)),
        _event(
            "compatibility_completed",
            "RESULT01",
            started_at + timedelta(hours=2),
            friend="RESULT02",
            score=84,
        ),
    ]
    repository = FakeAdminRepository(results, events)
    application.dependency_overrides[get_admin_repository] = lambda: repository
    return TestClient(application)


def test_admin_is_closed_when_credentials_are_not_configured(monkeypatch: MonkeyPatch) -> None:
    client = _client(monkeypatch, configured=False)

    response = client.get("/admin")

    assert response.status_code == 503
    assert response.headers["cache-control"] == "no-store"


def test_admin_requires_basic_authentication(monkeypatch: MonkeyPatch) -> None:
    client = _client(monkeypatch)

    response = client.get("/api/admin/dashboard", auth=("operator", "wrong"))

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Basic"
    assert response.headers["cache-control"] == "no-store"


def test_admin_html_and_read_only_apis_show_results_and_conversion(
    monkeypatch: MonkeyPatch,
) -> None:
    client = _client(monkeypatch)
    auth = ("operator", "correct-horse")

    html = client.get("/admin", auth=auth)
    dashboard = client.get("/api/admin/dashboard", auth=auth)
    results = client.get("/api/admin/results", auth=auth)
    detail = client.get("/api/admin/results/RESULT01", auth=auth)
    analytics = client.get("/api/admin/analytics/compatibility", auth=auth)
    missing = client.get("/api/admin/results/UNKNOWN1", auth=auth)

    assert html.status_code == 200
    assert "Pakit Admin" in html.text
    assert html.headers["cache-control"] == "no-store"
    assert dashboard.status_code == 200
    assert dashboard.headers["cache-control"] == "no-store"
    assert dashboard.json()["counts"]["total_results"] == 2
    assert dashboard.json()["experience_ratio"] == 50.0
    assert dashboard.json()["view_to_compatibility_ratio"] == 100.0
    assert results.json()["items"][0]["nickname"] == "선*"
    assert results.json()["items"][1]["nickname"] == "해*니"
    assert detail.json()["nickname"] == "해서니"
    assert detail.json()["usage"] == {
        "view_count": 1,
        "last_viewed_at": "2026-08-20T01:00:00Z",
        "compatibility_count": 1,
    }
    assert analytics.json()["completed_count"] == 1
    assert analytics.json()["view_to_compatibility_ratio"] == 100.0
    assert missing.status_code == 404
    assert missing.headers["cache-control"] == "no-store"
