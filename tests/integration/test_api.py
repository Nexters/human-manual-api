import pytest
from fastapi.testclient import TestClient

from pakit.api.schemas.assessment_submissions import (
    ASSESSMENT_SUBMISSION_EXAMPLE,
    ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE,
)
from pakit.api.schemas.compatibility import COMPATIBILITY_RESPONSE_EXAMPLE
from pakit.domain.assessment_contract import ASSESSMENT_VERSION, QUESTION_CONTRACTS, AnswerKind
from pakit.main import app

client = TestClient(app)


def _valid_submission() -> dict[str, object]:
    answers: list[dict[str, object]] = []
    for question_id, contract in QUESTION_CONTRACTS.items():
        if contract.answer_kind in {AnswerKind.CHOICE, AnswerKind.ACTION}:
            answers.append(
                {"question_id": question_id, "value": sorted(contract.allowed_values)[0]}
            )
        elif contract.answer_kind is AnswerKind.SCALE:
            answers.append({"question_id": question_id, "value": 35})
        else:
            answers.append({"question_id": question_id, "value": 247})

    return {
        "assessment_version": ASSESSMENT_VERSION,
        "participant": {"nickname": "송송"},
        "answers": answers,
        "mbti": "INTP",
    }


def test_health() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_serves_manual_assessment_test_page() -> None:
    response = client.get("/test/")

    assert response.status_code == 200
    assert "나 사용 설명서 테스트" in response.text
    assert "/api/tests/submissions" in response.text


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
    response_example = operation["responses"]["200"]["content"]["application/json"]["example"]
    assert response_example == ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE
    get_operation = document["paths"]["/api/results/{result_code}"]["get"]
    assert get_operation["summary"] == "테스트 결과 조회"
    assert "demo-result-code" in get_operation["description"]
    compatibility_operation = document["paths"]["/api/compatibility"]["get"]
    assert compatibility_operation["tags"] == ["Compatibility"]
    assert compatibility_operation["summary"] == "친구 궁합 조회"
    compatibility_example = compatibility_operation["responses"]["200"]["content"][
        "application/json"
    ]["example"]
    assert compatibility_example == COMPATIBILITY_RESPONSE_EXAMPLE

    test_tag = next(tag for tag in document["tags"] if tag["name"] == "Test")
    assert "답변 제출" in test_tag["description"]
    assert "/api/v1/tests/submissions" not in document["paths"]
    assert "/api/v1/tests/evaluate" not in document["paths"]
    assert "/api/assessments/submissions" not in document["paths"]
    assert "/api/assessments/evaluate" not in document["paths"]
    assert "/api/tests/evaluate" not in document["paths"]

    submission_schema = document["components"]["schemas"]["AssessmentSubmissionInput"]
    assert submission_schema["properties"]["mbti"]["description"] == (
        "화면에서 선택한 네 글자 MBTI 유형"
    )
    answer_schema = document["components"]["schemas"]["AnswerInput"]
    assert set(answer_schema["properties"]) == {"question_id", "value"}
    result_schema = document["components"]["schemas"]["AssessmentSubmissionOutput"]
    assert set(result_schema["properties"]) == {
        "result_code",
        "overview",
        "unboxing_kit",
        "features",
        "can_do",
        "warnings",
        "charging",
    }
    compatibility_schema = document["components"]["schemas"]["CompatibilityOutput"]
    assert set(compatibility_schema["properties"]) == {
        "mine",
        "friend",
        "headline",
        "description",
        "synergy",
        "tips",
        "relationship_tip",
    }


def test_swagger_submission_example_is_accepted() -> None:
    response = client.post(
        "/api/tests/submissions",
        json=ASSESSMENT_SUBMISSION_EXAMPLE,
    )

    assert response.status_code == 200
    body = response.json()
    expected = ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE | {"result_code": body["result_code"]}
    assert body == expected


def test_gets_submitted_result_by_result_code() -> None:
    submitted = client.post(
        "/api/tests/submissions",
        json=ASSESSMENT_SUBMISSION_EXAMPLE,
    )
    assert submitted.status_code == 200
    submitted_body = submitted.json()

    response = client.get(f"/api/results/{submitted_body['result_code']}")

    assert response.status_code == 200
    assert response.json() == submitted_body == ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE


def test_returns_404_for_unknown_result_code() -> None:
    response = client.get("/api/results/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "TEST_RESULT_NOT_FOUND",
            "message": "테스트 결과를 찾을 수 없습니다.",
        }
    }


def test_gets_mock_friend_compatibility() -> None:
    response = client.get(
        "/api/compatibility",
        params={"mine": "demo-result-code", "friend": "demo-friend-code"},
    )

    assert response.status_code == 200
    assert response.json() == COMPATIBILITY_RESPONSE_EXAMPLE


def test_returns_404_for_unknown_compatibility_codes() -> None:
    response = client.get(
        "/api/compatibility",
        params={"mine": "unknown", "friend": "demo-friend-code"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "COMPATIBILITY_NOT_FOUND",
            "message": "친구 궁합 결과를 찾을 수 없습니다.",
        }
    }


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


def test_submits_complete_assessment_and_returns_mixed_result() -> None:
    response = client.post("/api/tests/submissions", json=_valid_submission())

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "result_code",
        "overview",
        "unboxing_kit",
        "features",
        "can_do",
        "warnings",
        "charging",
    }
    assert body["overview"]["noun"] == "망원경"
    assert body["overview"]["character_id"] == "telescope"
    assert body["overview"]["image_url"] == "/assets/characters/telescope.png"
    assert body["overview"]["result_name"].endswith("망원경")
    assert len(body["overview"]["tags"]) == 3
    assert all(0 <= score <= 100 for score in body["unboxing_kit"]["axis_scores"].values())
    assert len(body["features"]) == 4
    assert len(body["can_do"]) == 4
    assert len(body["warnings"]) == 4
    assert len(body["charging"]["activities"]) == 3


def test_submission_uses_answers_and_mbti_for_deterministic_result_fields() -> None:
    payload = ASSESSMENT_SUBMISSION_EXAMPLE | {"mbti": "INTP"}
    example_answers = ASSESSMENT_SUBMISSION_EXAMPLE["answers"]
    assert isinstance(example_answers, list)
    payload["answers"] = [
        answer
        | {
            "value": {
                "step2.q01": "approach_directly",
                "step2.q02": "resolve_immediately",
                "step2.q03": "send_immediately",
                "step2.q04": 100,
                "step2.q05": "share_selectively",
                "step2.q06": 999,
                "step2.q07": "decorate_for_mood",
                "step2.q08": "express_with_actions",
                "step2.q09": "forget_quickly",
                "step2.q10": "try_new_menu",
                "step2.q11": "try_new_store",
                "step2.q12": "press",
            }.get(answer["question_id"], answer["value"])
        }
        for answer in example_answers
    ]

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 200
    body = response.json()
    assert body["overview"] | {"tags": []} == {
        "rarity": "상위 4%",
        "adjective": '"어디야" 물을 때마다 다른 나라 가 있는',
        "noun": "망원경",
        "result_name": '"어디야" 물을 때마다 다른 나라 가 있는 망원경',
        "character_id": "telescope",
        "image_url": "/assets/characters/telescope.png",
        "tags": [],
    }
    assert body["unboxing_kit"]["axis_scores"] == {
        "attachment": 0,
        "expression": 100,
        "routine": 0,
        "egen": 33,
    }
    assert body["unboxing_kit"]["title"] == "고백도 통보로 하는 사람"
    assert body["unboxing_kit"]["packaging"]["type"] == "minimal_box"
    assert body["unboxing_kit"]["opening_tool"]["type"] == "chainsaw"


def test_serves_character_image_from_result_url() -> None:
    submitted = client.post("/api/tests/submissions", json=_valid_submission())
    image_url = submitted.json()["overview"]["image_url"]

    response = client.get(image_url)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"


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


def test_rejects_unknown_answer_value() -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    first = answers[0]
    assert isinstance(first, dict)
    first["value"] = "not-registered"

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "ASSESSMENT_ANSWERS_INVALID"


def test_rejects_legacy_answer_fields() -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    first = answers[0]
    assert isinstance(first, dict)
    first.pop("value")
    first["kind"] = "choice"
    first["option_id"] = "restaurant"

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422


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


def test_rejects_string_answer_with_integer_value() -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    first = answers[0]
    assert isinstance(first, dict)
    first["value"] = 123

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert "문자열" in response.json()["error"]["message"]


def test_rejects_integer_answer_with_string_value() -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    integer_answer = next(answer for answer in answers if answer["question_id"] == "step2.q06")
    assert isinstance(integer_answer, dict)
    integer_answer["value"] = "247"

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert "정수" in response.json()["error"]["message"]


@pytest.mark.parametrize(
    ("question_id", "value", "expected_limit"),
    [
        ("step2.q04", -1, "0 이상"),
        ("step2.q04", 101, "100 이하"),
        ("step2.q06", -1, "0 이상"),
        ("step2.q06", 1000, "999 이하"),
    ],
)
def test_rejects_out_of_range_numeric_answer(
    question_id: str, value: int, expected_limit: str
) -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    answer = next(answer for answer in answers if answer["question_id"] == question_id)
    assert isinstance(answer, dict)
    answer["value"] = value

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert expected_limit in response.json()["error"]["message"]


@pytest.mark.parametrize(
    ("question_id", "value"),
    [("step2.q04", 0), ("step2.q04", 100), ("step2.q06", 0), ("step2.q06", 999)],
)
def test_accepts_numeric_answer_boundaries(question_id: str, value: int) -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    answer = next(answer for answer in answers if answer["question_id"] == question_id)
    assert isinstance(answer, dict)
    answer["value"] = value

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 200


def test_rejects_unknown_mbti() -> None:
    payload = _valid_submission()
    payload["mbti"] = "ABCD"

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
