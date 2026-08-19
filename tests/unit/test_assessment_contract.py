import json
from pathlib import Path

from pakit.api.schemas.assessment_submissions import ASSESSMENT_SUBMISSION_EXAMPLE
from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_contract import ASSESSMENT_VERSION, QUESTION_CONTRACTS, AnswerKind

STEP1_DISPLAY_ORDER = [
    "step1.q01",
    "step1.q05",
    "step1.q06",
    "step1.q07",
    "step1.q08",
    "step1.q12",
    "step1.q11",
    "step1.q02",
]


def test_runtime_contract_matches_published_identifier_document() -> None:
    document_path = Path(__file__).parents[2] / "docs" / "assessment-identifiers.v1.json"
    document = json.loads(document_path.read_text(encoding="utf-8"))

    assert document["assessment_version"] == ASSESSMENT_VERSION
    assert document["identifier_status"] == "published"
    assert len(document["questions"]) == 20
    assert {"step1.q03", "step1.q04"}.isdisjoint(QUESTION_CONTRACTS)
    assert sum(question_id.startswith("step1.") for question_id in QUESTION_CONTRACTS) == 8
    assert [
        question_id for question_id in QUESTION_CONTRACTS if question_id.startswith("step1.")
    ] == (STEP1_DISPLAY_ORDER)
    assert {question["question_id"] for question in document["questions"]} == set(
        QUESTION_CONTRACTS
    )
    step1_questions = [question for question in document["questions"] if question["step"] == 1]
    assert [question["order"] for question in step1_questions] == list(range(1, 9))
    assert [question["question_id"] for question in step1_questions] == STEP1_DISPLAY_ORDER
    step2_questions = [question for question in document["questions"] if question["step"] == 2]
    assert [question["order"] for question in step2_questions] == list(range(1, 13))
    for question in document["questions"]:
        contract = QUESTION_CONTRACTS[question["question_id"]]
        assert contract.answer_kind is AnswerKind(question["answer_kind"])
        assert contract.allowed_values == frozenset(question.get("values", []))
        constraints = question.get("constraints", {})
        assert contract.minimum == constraints.get("minimum")
        assert contract.maximum == constraints.get("maximum")
        assert contract.step == constraints.get("step")

    example_answers = ASSESSMENT_SUBMISSION_EXAMPLE["answers"]
    assert isinstance(example_answers, list)
    assert [
        answer["question_id"]
        for answer in example_answers
        if str(answer["question_id"]).startswith("step1.")
    ] == STEP1_DISPLAY_ORDER
    examples_by_question = {answer["question_id"]: answer for answer in example_answers}
    assert set(examples_by_question) == set(QUESTION_CONTRACTS)
    for question in document["questions"]:
        example = examples_by_question[question["question_id"]]
        if question["answer_kind"] in {"choice", "action"}:
            assert example["value"] in question["values"]

    mbti_input = document["mbti_input"]
    assert mbti_input["field"] == "mbti"
    assert set(mbti_input["allowed_values"]) == {mbti.value for mbti in MbtiType}


def test_q02_content_defines_four_role_choices_without_asset_metadata() -> None:
    document_path = Path(__file__).parents[2] / "docs" / "assessment-content.v1.json"
    document = json.loads(document_path.read_text(encoding="utf-8"))
    question = next(item for item in document["questions"] if item["question_id"] == "step1.q02")

    assert question["prompt"] == "친구들과 있을 때, 나와 가장 닮은 토끼는?"
    assert question["options"] == [
        {
            "value": "organize_and_coordinate",
            "label": "잠깐, 의견 정리해서 방향부터 잡자.",
            "role": "정리·조율",
        },
        {
            "value": "lift_mood",
            "label": "분위기 왜 이래ㅋㅋ 일단 웃고 보자.",
            "role": "분위기 전환",
        },
        {
            "value": "make_it_happen",
            "label": "재밌겠다. 일단 해보고 생각하자!",
            "role": "실행·추진",
        },
        {
            "value": "care_for_others",
            "label": "넌 뭐가 좋아? 말해주면 내가 챙길게.",
            "role": "관심·배려",
        },
    ]

    step1_questions = sorted(
        (item for item in document["questions"] if item["step"] == 1),
        key=lambda item: item["order"],
    )
    assert [item["order"] for item in step1_questions] == list(range(1, 9))
    assert [item["question_id"] for item in step1_questions] == STEP1_DISPLAY_ORDER
