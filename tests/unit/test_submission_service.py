import asyncio
from collections.abc import Iterator

from pytest import MonkeyPatch

from pakit.api.schemas.assessment_submissions import (
    ASSESSMENT_SUBMISSION_EXAMPLE,
    AssessmentSubmissionInput,
)
from pakit.domain.assessment_submission import SubmissionResultData
from pakit.services.result_repository import ResultCodeConflictError
from pakit.services.submission_service import submit_assessment


class ConflictOnceRepository:
    def __init__(self) -> None:
        self.saved_codes: list[str] = []

    async def save(
        self,
        result: SubmissionResultData,
        *,
        assessment_version: str,
        content_version: str,
    ) -> None:
        self.saved_codes.append(result.result_code)
        if len(self.saved_codes) == 1:
            raise ResultCodeConflictError

    async def get(self, result_code: str) -> SubmissionResultData | None:
        return None


def test_reissues_the_result_code_when_it_conflicts(monkeypatch: MonkeyPatch) -> None:
    generated_codes: Iterator[str] = iter(("AAAAAAAA", "BBBBBBBB"))
    monkeypatch.setattr(
        "pakit.services.submission_service.token_urlsafe",
        lambda _: next(generated_codes),
    )
    submission = AssessmentSubmissionInput.model_validate(ASSESSMENT_SUBMISSION_EXAMPLE).to_domain()
    repository = ConflictOnceRepository()

    result = asyncio.run(submit_assessment(submission, repository))

    assert result.result_code == "BBBBBBBB"
    assert repository.saved_codes == ["AAAAAAAA", "BBBBBBBB"]
