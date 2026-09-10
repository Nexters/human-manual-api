from typing import Any

import httpx2

from pakit.services.romantic_report_generator import (
    GeneratedRelationshipReport,
    RomanticReportGenerationError,
    RomanticReportGenerator,
)


class OpenAIRomanticReportGenerator(RomanticReportGenerator):
    def __init__(
        self,
        *,
        api_key: str,
        model: str,
        max_output_tokens: int,
        timeout_seconds: float,
    ) -> None:
        self._api_key = api_key
        self._model = model
        self._max_output_tokens = max_output_tokens
        self._timeout_seconds = timeout_seconds

    @property
    def model(self) -> str:
        return self._model

    async def generate(self, *, instructions: str, user_prompt: str) -> GeneratedRelationshipReport:
        try:
            async with httpx2.AsyncClient(timeout=self._timeout_seconds) as client:
                response = await client.post(
                    "https://api.openai.com/v1/responses",
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self._model,
                        "instructions": instructions,
                        "input": user_prompt,
                        "max_output_tokens": self._max_output_tokens,
                        "store": False,
                    },
                )
                response.raise_for_status()
                payload: dict[str, Any] = response.json()
        except (httpx2.HTTPError, ValueError, TypeError) as error:
            raise RomanticReportGenerationError from error

        content = _output_text(payload).strip()
        if not content:
            raise RomanticReportGenerationError
        usage = payload.get("usage") or {}
        return GeneratedRelationshipReport(
            content=content,
            provider_response_id=payload.get("id"),
            input_tokens=usage.get("input_tokens"),
            output_tokens=usage.get("output_tokens"),
        )


def _output_text(payload: dict[str, Any]) -> str:
    direct = payload.get("output_text")
    if isinstance(direct, str):
        return direct
    texts: list[str] = []
    for item in payload.get("output", []):
        for content in item.get("content", []):
            if content.get("type") == "output_text" and isinstance(content.get("text"), str):
                texts.append(content["text"])
    return "".join(texts)
