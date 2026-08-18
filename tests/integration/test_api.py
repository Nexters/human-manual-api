import re
from copy import deepcopy
from dataclasses import replace
from typing import Any

import pytest
from fastapi.testclient import TestClient

from pakit.api.dependencies import get_result_repository
from pakit.api.schemas.assessment_submissions import (
    ASSESSMENT_SUBMISSION_EXAMPLE,
    ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE,
)
from pakit.api.schemas.compatibility import COMPATIBILITY_RESPONSE_EXAMPLE
from pakit.domain.assessment_contract import ASSESSMENT_VERSION, QUESTION_CONTRACTS, AnswerKind
from pakit.domain.assessment_submission import SubmissionResultData
from pakit.main import app


class InMemoryResultRepository:
    def __init__(self) -> None:
        self.results: dict[str, SubmissionResultData] = {}

    async def save(
        self,
        result: SubmissionResultData,
        *,
        assessment_version: str,
        content_version: str,
    ) -> None:
        self.results[result.result_code] = result

    async def get(self, result_code: str) -> SubmissionResultData | None:
        return self.results.get(result_code)


result_repository = InMemoryResultRepository()
app.dependency_overrides[get_result_repository] = lambda: result_repository
client = TestClient(app)


def _testserver_response_example() -> dict[str, Any]:
    expected = deepcopy(ASSESSMENT_SUBMISSION_RESPONSE_EXAMPLE)
    expected["overview"]["image_url"] = "http://testserver/assets/characters/spinning_top.png"
    expected["unboxing_kit"]["packaging"]["image_url"] = (
        "http://testserver/assets/packaging_boxes/matryoshka_box.png"
    )
    expected["unboxing_kit"]["opening_tool"]["image_url"] = (
        "http://testserver/assets/opening_tools/glove.png"
    )
    expected["compatible_friends"][0]["image_url"] = (
        "http://testserver/assets/characters/secret_box.png"
    )
    expected["compatible_friends"][1]["image_url"] = (
        "http://testserver/assets/characters/teddy_bear.png"
    )
    return expected


def _valid_submission() -> dict[str, object]:
    answers: list[dict[str, object]] = []
    for question_id, contract in QUESTION_CONTRACTS.items():
        if contract.answer_kind in {AnswerKind.CHOICE, AnswerKind.ACTION}:
            answers.append(
                {"question_id": question_id, "value": sorted(contract.allowed_values)[0]}
            )
        elif contract.answer_kind is AnswerKind.SCALE:
            answers.append({"question_id": question_id, "value": 50})
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


@pytest.mark.parametrize(
    "origin",
    ["http://localhost:3000", "http://localhost:5173", "https://pakit.kr"],
)
def test_allows_cors_from_frontend(origin: str) -> None:
    response = client.options(
        "/api/tests/submissions",
        headers={
            "Origin": origin,
            "Access-Control-Request-Method": "POST",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == origin
    assert response.headers["access-control-allow-credentials"] == "true"


def test_serves_manual_assessment_test_page() -> None:
    response = client.get("/test/")

    assert response.status_code == 200
    assert "나 사용 설명서 테스트" in response.text
    assert "/api/tests/submissions" in response.text
    assert 'id="features"' in response.text
    assert "data.features.map" in response.text
    assert 'id="character-story-title"' in response.text
    assert "data.character_story.title" in response.text
    assert 'id="can-do"' in response.text
    assert "data.can_do.map" in response.text
    assert 'id="warnings"' in response.text
    assert "data.warnings.map" in response.text
    assert 'id="charging-description"' in response.text
    assert 'id="charging-activities"' in response.text
    assert "data.charging.activities.map" in response.text
    assert 'id="packaging-image"' in response.text
    assert "data.unboxing_kit.packaging.image_url" in response.text
    assert 'id="tool-image"' in response.text
    assert "data.unboxing_kit.opening_tool.image_url" in response.text
    assert 'id="summary-title"' not in response.text
    assert "data.unboxing_kit.title" not in response.text
    assert 'id="compatible-friends"' in response.text
    assert "data.compatible_friends.map" in response.text
    assert 'id="compatibility-link"' in response.text
    assert "/compatibility-test/?mine=" in response.text
    assert 'id="fill-defaults"' in response.text
    assert 'id="nickname" type="text" required' in response.text
    assert 'id="nickname" type="text" value=' not in response.text
    assert 'input.setCustomValidity("값을 선택해주세요.")' in response.text
    assert 'mbti.add(new Option("MBTI 선택", "", true, true))' in response.text
    assert 'document.querySelector("#nickname").value = "해서니"' in response.text
    assert 'choices("step1.q11"' in response.text
    assert 'choices("step1.q12"' in response.text


def test_serves_manual_compatibility_test_page() -> None:
    response = client.get("/compatibility-test/")

    assert response.status_code == 200
    assert "친구 궁합 테스트" in response.text
    assert "/api/compatibility?" in response.text
    assert "data.details.map" in response.text
    assert 'id="mine-image"' in response.text
    assert 'id="friend-image"' in response.text
    assert "data.synergy.score" in response.text
    assert "data.tips.map" in response.text
    assert "data.relationship_tip.description" in response.text


def test_assessment_openapi_uses_korean_developer_descriptions() -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    document = response.json()
    operation = document["paths"]["/api/tests/submissions"]["post"]
    assert operation["tags"] == ["Test"]
    assert operation["summary"] == "테스트 결과 제출"
    assert "요청 데이터" in operation["description"]
    assert "20개 문항" in operation["description"]
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
    assert "데이터베이스" in get_operation["description"]
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
    assert "/api/assessments/submissions" not in document["paths"]

    submission_schema = document["components"]["schemas"]["AssessmentSubmissionInput"]
    assert submission_schema["properties"]["mbti"]["description"] == (
        "화면에서 선택한 네 글자 MBTI 유형"
    )
    answer_schema = document["components"]["schemas"]["AnswerInput"]
    assert set(answer_schema["properties"]) == {"question_id", "value"}
    result_schema = document["components"]["schemas"]["AssessmentSubmissionOutput"]
    assert set(result_schema["properties"]) == {
        "result_code",
        "participant",
        "overview",
        "unboxing_kit",
        "features",
        "character_story",
        "can_do",
        "warnings",
        "charging",
        "compatible_friends",
    }
    result_code_schema = result_schema["properties"]["result_code"]
    assert result_code_schema["minLength"] == 8
    assert result_code_schema["maxLength"] == 8
    assert result_code_schema["pattern"] == "^[A-Za-z0-9_-]{8}$"
    charging_schema = document["components"]["schemas"]["ChargingOutput"]
    assert set(charging_schema["properties"]) == {"description", "activities"}
    assert charging_schema["properties"]["description"]["maxLength"] == 61
    charging_activity_schema = document["components"]["schemas"]["ChargingActivityOutput"]
    assert charging_activity_schema["properties"]["label"]["maxLength"] == 10
    feature_schema = document["components"]["schemas"]["FeatureOutput"]
    assert feature_schema["properties"]["title"]["maxLength"] == 11
    unboxing_schema = document["components"]["schemas"]["UnboxingKitOutput"]
    assert set(unboxing_schema["properties"]) == {
        "axis_scores",
        "packaging",
        "opening_tool",
    }
    compatibility_schema = document["components"]["schemas"]["CompatibilityOutput"]
    assert set(compatibility_schema["properties"]) == {
        "mine",
        "friend",
        "headline",
        "description",
        "synergy",
        "details",
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
    expected = _testserver_response_example() | {"result_code": body["result_code"]}
    assert body == expected
    assert len(body["result_code"]) == 8
    assert re.fullmatch(r"[A-Za-z0-9_-]{8}", body["result_code"])


def test_gets_submitted_result_by_result_code() -> None:
    submitted = client.post(
        "/api/tests/submissions",
        json=ASSESSMENT_SUBMISSION_EXAMPLE,
    )
    assert submitted.status_code == 200
    submitted_body = submitted.json()

    response = client.get(f"/api/results/{submitted_body['result_code']}")

    assert response.status_code == 200
    assert response.json() == submitted_body


def test_creates_a_distinct_result_code_for_each_submission() -> None:
    first = client.post("/api/tests/submissions", json=ASSESSMENT_SUBMISSION_EXAMPLE)
    second = client.post("/api/tests/submissions", json=ASSESSMENT_SUBMISSION_EXAMPLE)

    assert first.status_code == second.status_code == 200
    assert first.json()["result_code"] != second.json()["result_code"]


def test_returns_404_for_unknown_result_code() -> None:
    response = client.get("/api/results/not-found")

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "TEST_RESULT_NOT_FOUND",
            "message": "테스트 결과를 찾을 수 없습니다.",
        }
    }


def test_calculates_friend_compatibility_from_two_saved_results() -> None:
    mine = client.post("/api/tests/submissions", json=ASSESSMENT_SUBMISSION_EXAMPLE)
    friend_payload = _valid_submission()
    friend_payload["participant"] = {"nickname": "선우"}
    friend_payload["mbti"] = "ISFJ"
    friend = client.post("/api/tests/submissions", json=friend_payload)
    assert mine.status_code == friend.status_code == 200

    response = client.get(
        "/api/compatibility",
        params={
            "mine": mine.json()["result_code"],
            "friend": friend.json()["result_code"],
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["mine"] == {
        "nickname": mine.json()["participant"]["nickname"],
        "noun": mine.json()["overview"]["noun"],
        "character_id": mine.json()["overview"]["character_id"],
        "image_url": mine.json()["overview"]["image_url"],
    }
    assert body["friend"] == {
        "nickname": "선우",
        "noun": friend.json()["overview"]["noun"],
        "character_id": friend.json()["overview"]["character_id"],
        "image_url": friend.json()["overview"]["image_url"],
    }
    assert 0 <= body["synergy"]["score"] <= 100
    assert len(body["synergy"]["tags"]) == 2
    assert [detail["key"] for detail in body["details"]] == [
        "distance",
        "conflict",
        "care",
        "pace",
    ]
    assert all(body["mine"]["nickname"] in detail["description"] for detail in body["details"])
    assert all(body["friend"]["nickname"] in detail["description"] for detail in body["details"])
    assert [tip["target"] for tip in body["tips"]] == ["mine", "friend"]
    assert body["tips"][0]["image_url"] == body["mine"]["image_url"]
    assert body["tips"][1]["image_url"] == body["friend"]["image_url"]
    for image_url in (
        body["mine"]["image_url"],
        body["friend"]["image_url"],
        *(tip["image_url"] for tip in body["tips"]),
    ):
        assert image_url.startswith("http://testserver/assets/characters/")
        assert client.get(image_url).status_code == 200


def test_returns_404_for_unknown_compatibility_codes() -> None:
    response = client.get(
        "/api/compatibility",
        params={"mine": "unknown1", "friend": "unknown2"},
    )

    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "COMPATIBILITY_NOT_FOUND",
            "message": "친구 궁합 결과를 찾을 수 없습니다.",
        }
    }


def test_returns_409_for_a_result_created_before_compatibility_profiles() -> None:
    current = client.post("/api/tests/submissions", json=ASSESSMENT_SUBMISSION_EXAMPLE)
    legacy = client.post("/api/tests/submissions", json=_valid_submission())
    assert current.status_code == legacy.status_code == 200
    legacy_code = legacy.json()["result_code"]
    result_repository.results[legacy_code] = replace(
        result_repository.results[legacy_code],
        compatibility_profile=None,
    )

    response = client.get(
        "/api/compatibility",
        params={"mine": current.json()["result_code"], "friend": legacy_code},
    )

    assert response.status_code == 409
    assert response.json() == {
        "error": {
            "code": "COMPATIBILITY_PROFILE_UNAVAILABLE",
            "message": "이 결과는 궁합 기능 추가 전에 생성되어 궁합을 계산할 수 없습니다.",
        }
    }


def test_old_versioned_test_path_is_not_available() -> None:
    response = client.post(
        "/api/v1/tests/submissions",
        json=ASSESSMENT_SUBMISSION_EXAMPLE,
    )

    assert response.status_code == 404


def test_submits_complete_assessment_and_returns_mixed_result() -> None:
    response = client.post("/api/tests/submissions", json=_valid_submission())

    assert response.status_code == 200
    body = response.json()
    assert set(body) == {
        "result_code",
        "participant",
        "overview",
        "unboxing_kit",
        "features",
        "character_story",
        "can_do",
        "warnings",
        "charging",
        "compatible_friends",
    }
    assert body["participant"] == {"nickname": "송송"}
    assert body["overview"]["noun"] == "망원경"
    assert body["overview"]["character_id"] == "telescope"
    assert body["overview"]["image_url"] == "http://testserver/assets/characters/telescope.png"
    assert body["overview"]["result_name"].endswith("망원경")
    assert len(body["overview"]["tags"]) == 3
    assert all(0 <= score <= 100 for score in body["unboxing_kit"]["axis_scores"].values())
    assert len(body["features"]) == 4
    assert body["character_story"]["title"]
    assert body["overview"]["noun"] in body["character_story"]["description"]
    assert len(body["can_do"]) == 4
    assert len(body["warnings"]) == 4
    assert set(body["charging"]) == {"description", "activities"}
    assert len(body["charging"]["activities"]) == 3
    assert body["charging"]["activities"][2] == {
        "type": "INTP",
        "label": "외부와 단절",
    }
    assert len(body["compatible_friends"]) == 2
    assert all(friend["badge"] == "환상의 장난감" for friend in body["compatible_friends"])


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
        "rarity": "상위 3.3%",
        "adjective": '"어디야" 물을 때마다 다른 나라 가 있는',
        "noun": "망원경",
        "result_name": '"어디야" 물을 때마다 다른 나라 가 있는 망원경',
        "character_id": "telescope",
        "image_url": "http://testserver/assets/characters/telescope.png",
        "tags": [],
    }
    assert body["unboxing_kit"]["axis_scores"] == {
        "attachment": 0,
        "expression": 100,
        "routine": 0,
        "egen": 33,
    }
    assert set(body["unboxing_kit"]) == {"axis_scores", "packaging", "opening_tool"}
    assert body["unboxing_kit"]["packaging"]["type"] == "minimal_box"
    assert body["unboxing_kit"]["opening_tool"]["type"] == "chainsaw"
    assert body["features"] == [
        {
            "title": "궁금한 건 못 참아요",
            "description": (
                "궁금한 건 검색만으로 넘기지 않고, 원리와 다른 가능성까지 직접 확인해요."
            ),
        },
        {
            "title": "결정 조율자",
            "description": (
                "친구들 의견이 갈리면 기준과 공통점을 정리해 "
                "모두가 납득할 방향을 만드는 사람이에요."
            ),
        },
        {
            "title": "바로 해결해요",
            "description": "걸리는 건 바로 확인하고, 해결할 일을 끝낸 뒤 다음 행동으로 넘어가요.",
        },
        {
            "title": "원리를 따져요",
            "description": "당연해 보이는 것도 작동 원리를 알 때까지 파고들어요.",
        },
    ]
    assert body["character_story"] == {
        "title": "원리를 알아야 비로소 초점이 잡히는 망원경",
        "description": (
            "망원경은 눈에 대기만 한다고 바로 보이지 않아요. 렌즈가 어떤 원리로 상을 잡는지 "
            "이해하고 몇 번이고 직접 조절해야 흐릿하던 것이 선명해지죠. 남들이 당연하게 넘긴 것도 "
            "직접 뜯어보고 원리를 이해해야 넘어가는 모습이 닮아 망원경이 도착했습니다."
        ),
    }
    assert body["can_do"] == [
        "내 말의 표면만 보지 말고, 왜 이런 말을 하는지까지 이해해주세요",
        "혼자 있는 시간을 넉넉히 주세요. 답장이 하루 늦어도 삐진 게 아니라 그저 충전 중입니다.",
        "서운한 일은 돌려 넘기지 말고, 그 자리에서 바로 확인하고 풀어주세요.",
        "말없이 챙기는 행동을 애정으로 알아봐주세요",
    ]
    assert body["warnings"] == [
        "해결하려고 꺼낸 말에 차갑다는 말이 돌아오면 억울해져요",
        "혼자 정리할 틈이 없으면 대답이 점점 짧아져요",
        "재촉받으면 하려던 마음도 사라져요",
        "잠이 덜 깨면 첫 반응이 무뚝뚝해요",
    ]


def test_submission_uses_q11_for_the_motivation_feature_only() -> None:
    curiosity_payload = _valid_submission()
    fun_payload = _valid_submission()
    curiosity_answers = curiosity_payload["answers"]
    fun_answers = fun_payload["answers"]
    assert isinstance(curiosity_answers, list)
    assert isinstance(fun_answers, list)
    for answer in curiosity_answers:
        if answer["question_id"] == "step1.q11":
            answer["value"] = "curiosity"
    for answer in fun_answers:
        if answer["question_id"] == "step1.q11":
            answer["value"] = "fun"

    curiosity_response = client.post("/api/tests/submissions", json=curiosity_payload)
    fun_response = client.post("/api/tests/submissions", json=fun_payload)

    assert curiosity_response.status_code == 200
    assert fun_response.status_code == 200
    curiosity_features = curiosity_response.json()["features"]
    fun_features = fun_response.json()["features"]
    assert curiosity_features[0]["title"] == "궁금한 건 못 참아요"
    assert fun_features[0]["title"] == "재밌는 건 해야 해요"
    assert curiosity_features[1:] == fun_features[1:]


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("listen_to_me", "내 말의 표면만 보지 말고, 왜 이런 말을 하는지까지 이해해주세요"),
        ("take_me_out", "생각이 막히면 새로운 장소로 데려가주세요"),
        ("give_me_space", "생각이 정리될 때까지 혼자 생각할 시간을 주세요"),
        ("solve_together", "막힌 이유부터 함께 정리해주세요"),
        ("make_me_laugh", "복잡한 생각에서 잠깐 빠져나오게 엉뚱한 이야기를 던져주세요"),
    ],
)
def test_uses_every_q12_support_preference(value: str, expected: str) -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    for answer in answers:
        if answer["question_id"] == "step1.q12":
            answer["value"] = value

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 200
    assert response.json()["can_do"][0] == expected


@pytest.mark.parametrize(
    ("question_id", "value", "slot", "expected"),
    [
        (
            "step1.q05",
            "during_meal",
            3,
            "밥 먹는 흐름이 끊기면 바로 예민해져요",
        ),
        (
            "step1.q05",
            "after_work",
            3,
            "퇴근 직후 할 일이 쏟아지면 바로 방전돼요",
        ),
        (
            "step1.q05",
            "late_night",
            3,
            "새벽 감성을 끊으면 괜히 더 예민해져요",
        ),
        (
            "step1.q06",
            "interrupt",
            2,
            "말을 끊으면 남은 이야기도 삼켜버려요",
        ),
        (
            "step1.q06",
            "take_food",
            2,
            "음식을 허락 없이 가져가면 한입보다 큰 서운함이 남아요",
        ),
        ("step1.q06", "nag", 2, "잔소리가 반복되면 귀부터 닫아요"),
        (
            "step1.q06",
            "change_plan",
            2,
            "계획이 갑자기 바뀌면 기분부터 틀어져요",
        ),
    ],
)
def test_uses_warning_answers(
    question_id: str,
    value: str,
    slot: int,
    expected: str,
) -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    for answer in answers:
        if answer["question_id"] == question_id:
            answer["value"] = value

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 200
    assert response.json()["warnings"][slot] == expected


def test_submission_uses_q01_and_q02_for_the_relationship_role_only() -> None:
    decision_payload = _valid_submission()
    worries_payload = _valid_submission()
    decision_answers = decision_payload["answers"]
    worries_answers = worries_payload["answers"]
    assert isinstance(decision_answers, list)
    assert isinstance(worries_answers, list)

    for answer in decision_answers:
        if answer["question_id"] == "step1.q01":
            answer["value"] = "decision"
        elif answer["question_id"] == "step1.q02":
            answer["value"] = "organize_and_coordinate"
    for answer in worries_answers:
        if answer["question_id"] == "step1.q01":
            answer["value"] = "worries"
        elif answer["question_id"] == "step1.q02":
            answer["value"] = "make_it_happen"

    decision_response = client.post("/api/tests/submissions", json=decision_payload)
    worries_response = client.post("/api/tests/submissions", json=worries_payload)

    assert decision_response.status_code == 200
    assert worries_response.status_code == 200
    decision_features = decision_response.json()["features"]
    worries_features = worries_response.json()["features"]
    assert decision_features[1]["title"] == "결정 조율자"
    assert worries_features[1]["title"] == "현실 해결사"
    assert decision_features[0] == worries_features[0]
    assert decision_features[2:] == worries_features[2:]


def test_serves_all_images_from_absolute_result_urls() -> None:
    submitted = client.post("/api/tests/submissions", json=_valid_submission())
    body = submitted.json()
    image_urls = [
        body["overview"]["image_url"],
        body["unboxing_kit"]["packaging"]["image_url"],
        body["unboxing_kit"]["opening_tool"]["image_url"],
        *(friend["image_url"] for friend in body["compatible_friends"]),
    ]

    assert all(image_url.startswith("http://testserver/assets/") for image_url in image_urls)
    for image_url in image_urls:
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
    first["option_id"] = "decision"

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


@pytest.mark.parametrize("removed_question_id", ["step1.q03", "step1.q04"])
def test_rejects_removed_question_id(removed_question_id: str) -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    first = answers[0]
    assert isinstance(first, dict)
    first["question_id"] = removed_question_id

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


@pytest.mark.parametrize("value", [1, 24, 26, 99])
def test_rejects_q04_value_outside_25_point_steps(value: int) -> None:
    payload = _valid_submission()
    answers = payload["answers"]
    assert isinstance(answers, list)
    answer = next(answer for answer in answers if answer["question_id"] == "step2.q04")
    assert isinstance(answer, dict)
    answer["value"] = value

    response = client.post("/api/tests/submissions", json=payload)

    assert response.status_code == 422
    assert "25 단위" in response.json()["error"]["message"]


@pytest.mark.parametrize(
    ("question_id", "value"),
    [
        ("step2.q04", 0),
        ("step2.q04", 25),
        ("step2.q04", 50),
        ("step2.q04", 75),
        ("step2.q04", 100),
        ("step2.q06", 0),
        ("step2.q06", 999),
    ],
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
