from typing import Protocol

from pakit.domain.assessment_submission import SubmissionResultData


class ResultCodeConflictError(RuntimeError):
    """이미 저장된 결과 코드와 충돌했습니다."""


class ResultRepository(Protocol):
    async def save(
        self,
        result: SubmissionResultData,
        *,
        assessment_version: str,
        content_version: str,
    ) -> None: ...

    async def get(self, result_code: str) -> SubmissionResultData | None: ...
