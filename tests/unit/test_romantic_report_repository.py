import asyncio

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from pakit.api.schemas.assessment_submissions import (
    ASSESSMENT_SUBMISSION_EXAMPLE,
    AssessmentSubmissionInput,
)
from pakit.core.models import Base
from pakit.core.result_repository import SqlAlchemyResultRepository
from pakit.core.romantic_report_repository import SqlAlchemyRomanticReportRepository
from pakit.services.romantic_report_repository import RomanticReportToSave
from pakit.services.submission_service import submit_assessment


def test_reads_profile_source_and_persists_generated_report() -> None:
    async def run() -> None:
        engine = create_async_engine("sqlite+aiosqlite://")
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        sessions = async_sessionmaker(engine, expire_on_commit=False)
        async with sessions() as session:
            submission = AssessmentSubmissionInput.model_validate(
                ASSESSMENT_SUBMISSION_EXAMPLE
            ).to_domain()
            result = await submit_assessment(
                submission,
                SqlAlchemyResultRepository(session),
            )
        async with sessions() as session:
            repository = SqlAlchemyRomanticReportRepository(session)
            source = await repository.get_profile_source(result.result_code)
            assert source is not None
            assert source.nickname == "송송"
            assert source.mbti == "ENTP"
            stored = await repository.save(
                RomanticReportToSave(
                    report_code="reportCode12",
                    mine_result_code=result.result_code,
                    partner_result_code="BBBBBBBB",
                    mine_gender="여자",
                    partner_gender="남자",
                    prompt_version="prompt-v1",
                    profile_version="profile-v1",
                    model="model-v1",
                    input_snapshot={"mine": {}, "partner": {}},
                    content="관계 설명서",
                    provider_response_id="resp_123",
                    input_tokens=10,
                    output_tokens=20,
                )
            )
            duplicate = await repository.save(
                RomanticReportToSave(
                    report_code="otherCode123",
                    mine_result_code=result.result_code,
                    partner_result_code="BBBBBBBB",
                    mine_gender="여자",
                    partner_gender="남자",
                    prompt_version="prompt-v1",
                    profile_version="profile-v1",
                    model="model-v1",
                    input_snapshot={"mine": {}, "partner": {}},
                    content="동시에 생성된 다른 본문",
                    provider_response_id="resp_456",
                    input_tokens=11,
                    output_tokens=21,
                )
            )
            existing = await repository.find_existing(
                mine_result_code=result.result_code,
                partner_result_code="BBBBBBBB",
                mine_gender="여자",
                partner_gender="남자",
                prompt_version="prompt-v1",
                profile_version="profile-v1",
                model="model-v1",
            )
        await engine.dispose()

        assert stored == existing
        assert duplicate == stored
        assert stored.created_at.year == 2026

    asyncio.run(run())
