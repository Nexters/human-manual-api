import asyncio
from dataclasses import replace
from io import StringIO
from pathlib import Path

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.util import load_python_file
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from pakit.api.schemas.assessment_submissions import (
    ASSESSMENT_SUBMISSION_EXAMPLE,
    AssessmentSubmissionInput,
    AssessmentSubmissionOutput,
)
from pakit.core.models import AssessmentResultRecord, Base
from pakit.core.result_repository import SqlAlchemyResultRepository
from pakit.domain.assessment_submission import SubmittedAnswer
from pakit.services.submission_service import InvalidSubmissionError, submit_assessment


def test_keeps_each_submission_separate_and_private() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        first = AssessmentSubmissionInput.model_validate(ASSESSMENT_SUBMISSION_EXAMPLE).to_domain()
        second = replace(
            first,
            answers=tuple(
                SubmittedAnswer(answer.question_id, 0)
                if answer.question_id == "step2.q04"
                else answer
                for answer in first.answers
            ),
        )
        async with sessions() as session:
            repository = SqlAlchemyResultRepository(session)
            first_result = await submit_assessment(first, repository)
            second_result = await submit_assessment(second, repository)
            assert first_result.result_code != second_result.result_code
        async with sessions() as session:
            for submission, result in ((first, first_result), (second, second_result)):
                record = await session.scalar(
                    select(AssessmentResultRecord).where(
                        AssessmentResultRecord.result_code == result.result_code
                    )
                )
                assert record is not None
                assert record.response_snapshot == {
                    "assessment_version": submission.assessment_version,
                    "mbti": submission.mbti.value,
                    "answers": [
                        {"question_id": answer.question_id, "value": answer.value}
                        for answer in submission.answers
                    ],
                }
                restored = await SqlAlchemyResultRepository(session).get(result.result_code)
                assert restored == result
                public_payload = AssessmentSubmissionOutput.from_domain(
                    restored, public_base_url="https://example.test"
                ).model_dump()
                assert "answers" not in public_payload
                assert "response_snapshot" not in public_payload
                response = AssessmentSubmissionInput.model_validate(
                    {
                        **record.response_snapshot,
                        "participant": {"nickname": submission.nickname},
                    }
                )
                assert response.to_domain() == submission
                assert "response_snapshot" not in record.result_snapshot
                assert "answers" not in record.result_snapshot
        await engine.dispose()

    asyncio.run(run())


def test_invalid_submission_does_not_persist_responses() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        submission = AssessmentSubmissionInput.model_validate(
            ASSESSMENT_SUBMISSION_EXAMPLE
        ).to_domain()
        async with sessions() as session:
            repository = SqlAlchemyResultRepository(session)
            with pytest.raises(InvalidSubmissionError):
                await submit_assessment(replace(submission, answers=()), repository)
            assert await repository.count() == 0
        await engine.dispose()

    asyncio.run(run())


def test_response_snapshot_migration_is_nullable_and_reversible(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    migration = load_python_file(
        str(Path(__file__).resolve().parents[2] / "migrations" / "versions"),
        "20260908_04_add_response_snapshot.py",
    )
    output = StringIO()
    context = MigrationContext.configure(
        dialect_name="postgresql", opts={"as_sql": True, "output_buffer": output}
    )
    monkeypatch.setattr(migration, "op", Operations(context))
    migration.upgrade()
    upgrade_sql = output.getvalue()
    assert "ADD COLUMN response_snapshot JSONB" in upgrade_sql
    assert "NOT NULL" not in upgrade_sql
    assert "UPDATE" not in upgrade_sql
    assert "result_snapshot" not in upgrade_sql
    output.seek(0)
    output.truncate()
    migration.downgrade()
    assert "DROP COLUMN response_snapshot" in output.getvalue()
    assert "result_snapshot" not in output.getvalue()
