from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol


@dataclass(frozen=True)
class RelationshipProfileSource:
    result_code: str
    nickname: str
    mbti: str
    assessment_version: str
    axis_scores: dict[str, int]
    answers: dict[str, str | int]


@dataclass(frozen=True)
class StoredRomanticReport:
    report_code: str
    content: str
    created_at: datetime


@dataclass(frozen=True)
class RomanticReportToSave:
    report_code: str
    mine_result_code: str
    partner_result_code: str
    mine_gender: str
    partner_gender: str
    prompt_version: str
    profile_version: str
    model: str
    input_snapshot: dict[str, Any]
    content: str
    provider_response_id: str | None
    input_tokens: int | None
    output_tokens: int | None


class RomanticReportRepository(Protocol):
    async def get_profile_source(self, result_code: str) -> RelationshipProfileSource | None: ...

    async def find_existing(
        self,
        *,
        mine_result_code: str,
        partner_result_code: str,
        mine_gender: str,
        partner_gender: str,
        prompt_version: str,
        profile_version: str,
        model: str,
    ) -> StoredRomanticReport | None: ...

    async def save(self, report: RomanticReportToSave) -> StoredRomanticReport: ...


class RelationshipProfileSourceUnavailableError(RuntimeError):
    """결과는 있으나 원본 응답 스냅샷이 없습니다."""
