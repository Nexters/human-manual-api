import json
from pathlib import Path

import pytest

from pakit.api.schemas.assessment_submissions import ASSESSMENT_SUBMISSION_EXAMPLE
from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_contract import QUESTION_CONTRACTS, AnswerKind
from pakit.domain.assessment_submission import MbtiScores, classify_mbti


@pytest.mark.parametrize("expected", list(MbtiType))
def test_classifies_all_mbti_types(expected: MbtiType) -> None:
    scores = MbtiScores(
        introversion=100 if expected.value[0] == "I" else 0,
        intuition=100 if expected.value[1] == "N" else 0,
        feeling=100 if expected.value[2] == "F" else 0,
        perceiving=100 if expected.value[3] == "P" else 0,
    )

    assert classify_mbti(scores) is expected


def test_runtime_contract_matches_published_identifier_document() -> None:
    document_path = Path(__file__).parents[2] / "docs" / "assessment-identifiers.v1.json"
    document = json.loads(document_path.read_text(encoding="utf-8"))

    assert document["identifier_status"] == "published"
    assert len(document["questions"]) == 22
    assert {question["question_id"] for question in document["questions"]} == set(
        QUESTION_CONTRACTS
    )
    for question in document["questions"]:
        contract = QUESTION_CONTRACTS[question["question_id"]]
        assert contract.answer_kind is AnswerKind(question["answer_kind"])
        documented_ids = question.get("option_ids", question.get("action_ids", []))
        assert contract.allowed_ids == frozenset(documented_ids)

    example_answers = ASSESSMENT_SUBMISSION_EXAMPLE["answers"]
    assert isinstance(example_answers, list)
    examples_by_question = {answer["question_id"]: answer for answer in example_answers}
    assert set(examples_by_question) == set(QUESTION_CONTRACTS)
    for question in document["questions"]:
        example = examples_by_question[question["question_id"]]
        if question["answer_kind"] == "choice":
            assert example["option_id"] in question["option_ids"]
        elif question["answer_kind"] == "action":
            assert example["action_id"] in question["action_ids"]

    mbti_input = document["mbti_input"]
    assert mbti_input["allowed_values"] == [0, 20, 40, 60, 80, 100]
    assert [axis["score_key"] for axis in mbti_input["axes"]] == [
        "introversion",
        "intuition",
        "feeling",
        "perceiving",
    ]
