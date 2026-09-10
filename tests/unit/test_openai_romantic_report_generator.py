import asyncio
from typing import Any, ClassVar

from pytest import MonkeyPatch

from pakit.core.openai_romantic_report_generator import OpenAIRomanticReportGenerator


class FakeResponse:
    def raise_for_status(self) -> None:
        return None

    def json(self) -> dict[str, Any]:
        return {
            "id": "resp_123",
            "output": [{"content": [{"type": "output_text", "text": "## 1. 이 관계의 핵심 구조"}]}],
            "usage": {"input_tokens": 120, "output_tokens": 80},
        }


class FakeAsyncClient:
    last_request: ClassVar[dict[str, Any]] = {}

    def __init__(self, *, timeout: float) -> None:
        self.timeout = timeout

    async def __aenter__(self) -> "FakeAsyncClient":
        return self

    async def __aexit__(self, *args: object) -> None:
        return None

    async def post(self, url: str, **kwargs: Any) -> FakeResponse:
        type(self).last_request = {"url": url, **kwargs}
        return FakeResponse()


def test_calls_responses_api_without_provider_storage(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setattr(
        "pakit.core.openai_romantic_report_generator.httpx2.AsyncClient",
        FakeAsyncClient,
    )
    generator = OpenAIRomanticReportGenerator(
        api_key="secret-key",
        model="configured-model",
        max_output_tokens=5000,
        timeout_seconds=60,
    )

    generated = asyncio.run(generator.generate(instructions="system", user_prompt="user profile"))

    assert generated.content == "## 1. 이 관계의 핵심 구조"
    assert generated.provider_response_id == "resp_123"
    assert generated.input_tokens == 120
    assert generated.output_tokens == 80
    assert FakeAsyncClient.last_request["url"] == "https://api.openai.com/v1/responses"
    assert FakeAsyncClient.last_request["json"] == {
        "model": "configured-model",
        "instructions": "system",
        "input": "user profile",
        "max_output_tokens": 5000,
        "store": False,
    }
