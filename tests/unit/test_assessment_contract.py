import json
from pathlib import Path

from pakit.api.schemas.assessment_submissions import ASSESSMENT_SUBMISSION_EXAMPLE
from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_contract import ASSESSMENT_VERSION, QUESTION_CONTRACTS, AnswerKind


def test_runtime_contract_matches_published_identifier_document() -> None:
    document_path = Path(__file__).parents[2] / "docs" / "assessment-identifiers.v1.json"
    document = json.loads(document_path.read_text(encoding="utf-8"))

    assert document["assessment_version"] == ASSESSMENT_VERSION
    assert document["identifier_status"] == "published"
    assert len(document["questions"]) == 22
    assert {question["question_id"] for question in document["questions"]} == set(
        QUESTION_CONTRACTS
    )
    for question in document["questions"]:
        contract = QUESTION_CONTRACTS[question["question_id"]]
        assert contract.answer_kind is AnswerKind(question["answer_kind"])
        assert contract.allowed_values == frozenset(question.get("values", []))

    example_answers = ASSESSMENT_SUBMISSION_EXAMPLE["answers"]
    assert isinstance(example_answers, list)
    examples_by_question = {answer["question_id"]: answer for answer in example_answers}
    assert set(examples_by_question) == set(QUESTION_CONTRACTS)
    for question in document["questions"]:
        example = examples_by_question[question["question_id"]]
        if question["answer_kind"] in {"choice", "action"}:
            assert example["value"] in question["values"]

    mbti_input = document["mbti_input"]
    assert mbti_input["field"] == "mbti"
    assert set(mbti_input["allowed_values"]) == {mbti.value for mbti in MbtiType}
