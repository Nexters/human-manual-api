from fastapi import APIRouter

from pakit.domain.assessment import AssessmentInput, AssessmentResult
from pakit.services.result_builder import build_assessment_result

router = APIRouter(prefix="/assessments", tags=["assessments"])


@router.post("/evaluate", response_model=AssessmentResult)
async def evaluate_assessment(data: AssessmentInput) -> AssessmentResult:
    """Classify one completed assessment using the current PRD rules."""
    return build_assessment_result(data)
