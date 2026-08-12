from fastapi.testclient import TestClient

from pakit.api.schemas.assessment_submissions import ASSESSMENT_SUBMISSION_EXAMPLE
from pakit.domain.assessment_contract import ASSESSMENT_VERSION, QUESTION_CONTRACTS, AnswerKind
from pakit.main import app

client = TestClient(app)


def _valid_submission() -> dict[str, object]:
    answers: list[dict[str, object]] = []
    for question_id, contract in QUESTION_CONTRACTS.items():
        if contract.answer_kind is AnswerKind.CHOICE:
            answers.append(
                {
                    "question_id": question_id,
                    "kind": "choice",
                    "option_id": sorted(contract.allowed_ids)[0],
                }
            )
        elif contract.answer_kind is AnswerKind.ACTION:
            answers.append(
                {
                    "question_id": question_id,
                    "kind": "action",
                    "action_id": sorted(contract.allowed_ids)[0],
                }
            )
        elif contract.answer_kind is AnswerKind.SCALE:
            answers.append({"question_id": question_id, "kind": "scale", "value": 35})
        else:
            answers.append({"question_id": question_id, "kind": "integer", "value": 247})

    return {
        "assessment_version": ASSESSMENT_VERSION,
        "participant": {"nickname": "송송"},
        "answers": answers,
        "mbti_scores": {
            "introversion": 80,
            "intuition": 60,
            "feeling": 40,
            "perceiving": 80,
        },
    }


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_assessment_openapi_uses_korean_developer_descriptions() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    document = response.json()
    operation = document["paths"]["/api/tests/submissions"]["post"]
    assert operation["tags"] == ["Test"]
    assert operation["summary"] == "테스트 결과 제출"
    assert "요청 데이터" in operation["description"]
    assert "22개 문항" in operation["description"]
    assert "서버에서 확인하는 항목" in operation["description"]
    assert "현재 응답 범위" in operation["description"]
    swagger_example = operation["requestBody"]["content"]["application/json"]["examples"][
        "complete"
    ]
    assert swagger_example["value"] == ASSESSMENT_SUBMISSION_EXAMPLE
    assert "실제 문항·선택지 ID" in swagger_example["description"]

    test_tag = next(tag for tag in document["tags"] if tag["name"] == "Test")
    assert "답변 제출" in test_tag["description"]
    assert "/api/v1/tests/submissions" not in document["paths"]
    assert "/api/v1/tests/evaluate" not in document["paths"]
    assert "/api/assessments/submissions" not in document["paths"]
    assert "/api/assessments/evaluate" not in document["paths"]

    mbti_schema = document["components"]["schemas"]["MbtiScoresInput"]
    assert mbti_schema["properties"]["introversion"]["description"] == ("외향형 E 0 ↔ 내향형 I 100")


def test_swagger_submission_example_is_accepted() -> None:
    response = client.post(
        "/api/tests/submissions",
        json=ASSESSMENT_SUBMISSION_EXAMPLE,
    )

    assert response.status_code == 200


def test_old_versioned_test_path_is_not_available() -> None:
    response = client.post(
        "/api/v1/tests/submissions",
        json=ASSESSMENT_SUBMISSION_EXAMPLE,
    )

    assert response.status_code == 404


def test_evaluate_assessment() -> None:
    response = client.post(
        "/api/tests/evaluate",
        json={
            "mbti": "ENTP",
            "axes": {
                "expression": 90,
                "attachment": 20,
                "manner": 80,
                "novelty": 90,
            },
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["classification"]["packaging_code"] == "A1"
    assert body["classification"]["opening_tool_code"] == "B4"
    assert body["product_name"].endswith("팽이")


def test_rejects_out_of_range_score() -> None:
    response = client.post(
        "/api/tests/evaluate",
        json={
            "mbti": "ENTP",
            "axes": {"expression": 101, "attachment": 0, "manner": 0, "novelty": 0},
        },
    )

    assert response.status_code == 422


def test_submits_complete_assessment_and_returns_mock_result() -> None:
    response = client.post("/api/tests/submissions", json=_valid_submission())

    assert response.status_code == 200
    body = response.json()
    assert body["mode"] == "mock"
    assert body["persisted"] is False
    assert body["result_id"] is None
    assert body["product"]["noun"] == "망원경"
    assert body["product"]["character_asset_key"] == "image_telescope_340"
    assert body["manual"]["introduction"]["model_name"] == "송송"
    assert body["provisional_fields"] == ["product.name", "unboxing", "manual"]


def test_rejects_unsupported_assessment_version() -> None:
    payload = _valid_submission()
    payload["assessment_version"] = "old-version"

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 409
    assert response.json()["error"]["code"] == "ASSESSMENT_VERSION_UNSUPPORTED"


def test_rejects_missing_answer() -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    answers.pop()

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ASSESSMENT_ANSWERS_INVALID"


def test_rejects_duplicate_question_answer() -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    first = answers[0]
    assert isinstance(first, dict)
    last = answers[-1]
    assert isinstance(last, dict)
    last["question_id"] = first["question_id"]

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert "중복" in response.json()["error"]["message"]


def test_rejects_unknown_option_id() -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    first = answers[0]
    assert isinstance(first, dict)
    first["option_id"] = "not-registered"

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ASSESSMENT_ANSWERS_INVALID"


def test_rejects_unknown_question_id() -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    first = answers[0]
    assert isinstance(first, dict)
    first["question_id"] = "unknown.question"

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert "알 수 없는 문항 ID" in response.json()["error"]["message"]


def test_rejects_answer_kind_mismatch() -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    first = answers[0]
    assert isinstance(first, dict)
    first.pop("option_id")
    first["kind"] = "action"
    first["action_id"] = "press"

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert "답변 타입" in response.json()["error"]["message"]


def test_rejects_mbti_midpoint() -> None:
    payload = _valid_submission()
    mbti_scores = payload["mbti_scores"]
    assert isinstance(mbti_scores, dict)
    mbti_scores["intuition"] = 50

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
