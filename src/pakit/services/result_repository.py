from typing import Protocol

from pakit.domain.assessment_submission import AssessmentSubmission, SubmissionResultData


class ResultCodeConflictError(RuntimeError):
    """이미 저장된 결과 코드와 충돌했습니다."""


class ResultRepository(Protocol):
    async def save(
        self,
        result: SubmissionResultData,
        *,
        submission: AssessmentSubmission,
        content_version: str,
        user_id: int | None = None,
    ) -> None: ...

    async def get(self, result_code: str) -> SubmissionResultData | None: ...

    async def count(self) -> int: ...
