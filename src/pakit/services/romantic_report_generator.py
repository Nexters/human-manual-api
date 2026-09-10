from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class GeneratedRelationshipReport:
    content: str
    provider_response_id: str | None = None
    input_tokens: int | None = None
    output_tokens: int | None = None


class RomanticReportGenerator(Protocol):
    @property
    def model(self) -> str: ...

    async def generate(
        self, *, instructions: str, user_prompt: str
    ) -> GeneratedRelationshipReport: ...


class RomanticReportGenerationError(RuntimeError):
    """AI 공급자가 관계 설명서를 정상적으로 생성하지 못했습니다."""


class RomanticReportGeneratorNotConfiguredError(RuntimeError):
    """AI 생성 설정이 구성되지 않았습니다."""
