import asyncio
from collections.abc import Iterator

from pytest import MonkeyPatch

from pakit.api.schemas.assessment_submissions import (
    ASSESSMENT_SUBMISSION_EXAMPLE,
    AssessmentSubmissionInput,
)
from pakit.domain.assessment_submission import AssessmentSubmission, SubmissionResultData
from pakit.services.result_repository import ResultCodeConflictError
from pakit.services.submission_service import submit_assessment


class ConflictOnceRepository:
    def __init__(self) -> None:
        self.saved_codes: list[str] = []
        self.saved_submissions: list[AssessmentSubmission] = []
        self.saved_user_ids: list[int | None] = []

    async def save(
        self,
        result: SubmissionResultData,
        *,
        submission: AssessmentSubmission,
        content_version: str,
        user_id: int | None = None,
    ) -> None:
        self.saved_codes.append(result.result_code)
        self.saved_submissions.append(submission)
        self.saved_user_ids.append(user_id)
        if len(self.saved_codes) == 1:
            raise ResultCodeConflictError

    async def get(self, result_code: str) -> SubmissionResultData | None:
        return None

    async def count(self) -> int:
        return len(self.saved_codes)


def test_reissues_the_result_code_when_it_conflicts(monkeypatch: MonkeyPatch) -> None:
    generated_codes: Iterator[str] = iter(("AAAAAAAA", "BBBBBBBB"))
    monkeypatch.setattr(
        "pakit.services.submission_service.token_urlsafe",
        lambda _: next(generated_codes),
    )
    submission = AssessmentSubmissionInput.model_validate(ASSESSMENT_SUBMISSION_EXAMPLE).to_domain()
    repository = ConflictOnceRepository()

    result = asyncio.run(submit_assessment(submission, repository, user_id=42))

    assert result.result_code == "BBBBBBBB"
    assert repository.saved_codes == ["AAAAAAAA", "BBBBBBBB"]
    assert repository.saved_user_ids == [42, 42]
    assert repository.saved_submissions == [submission, submission]
