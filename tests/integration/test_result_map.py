from fastapi.testclient import TestClient

from pakit.main import app
from pakit.web.result_map import render_result_map

client = TestClient(app)


def test_result_map_page_renders_html() -> None:
    response = client.get("/result-map")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    body = response.text
    assert body.startswith("<!doctype html>")
    assert "Pakit 결과 조합 지도" in body


def test_result_map_hidden_from_openapi() -> None:
    document = client.get("/openapi.json").json()

    assert "/result-map" not in document["paths"]


def test_question_chips_show_question_and_choices_on_hover_or_focus() -> None:
    body = render_result_map()

    assert 'class="chip chip-q question-chip"' in body
    assert 'tabindex="0"' in body
    assert "친구들이 나를 찾는 순간은 언제인가요?" in body
    assert "결정이 필요할 때" in body
    assert "고민 있을 때" in body
    assert "놀 사람 필요할 때" in body
    assert "정보 필요할 때" in body
    assert "집에만 있으려던 주말, 나를 밖으로 나오게 한 건?" in body
    assert "curiosity" in body
    assert "궁금한 새 장소" in body
    assert "나를 꼭 찾는 친구" in body
    assert "딱 하나 남은 목표" in body
    assert "지켜야 할 약속" in body
    assert "오늘뿐인 기회" in body
    assert "재밌어 보이는 모임" in body
    assert "기분이 안 좋을 때, 가장 반가운 친구의 연락은?" in body
    assert "무슨 일인지 천천히 들어줄게" in body
    assert "일단 나와. 맛있는 거 먹자" in body
    assert "혼자 정리되면 연락해. 기다릴게" in body
    assert "내가 같이 해결해볼까?" in body
    assert "이거 보고 일단 웃어ㅋㅋ" in body
    assert ".question-chip:hover .question-tooltip" in body
    assert ".question-chip:focus .question-tooltip" in body


def test_result_map_includes_copy_from_every_section() -> None:
    body = render_result_map()

    # 각 결과 영역에서 실제 소스 문구가 페이지에 포함되는지 확인한다.
    expected = [
        "취급주의 상자",  # 포장(A1)
        "전기톱",  # 개봉(B4)
        "브레이크가 고장 난",  # 언박싱 조합(A1 x B4)
        "궁금한 건 못 참아요",  # 핵심 특징 · 동원력
        "큰그림을 봐요",  # 핵심 특징 · 타고난 무기(INTJ)
        "정해진 순서를 건너뛰지 않고 현장을 책임지는 헬리콥터",  # 캐릭터 스토리(ESTJ)
        "원리를 알아야 비로소 초점이 잡히는 망원경",  # 캐릭터 스토리(INTP)
        "왜 그러냐고 묻는 대신, 늘 가던 곳에 같이 가서 시간 보내주세요",  # 사용 방법
        "속마음을 꺼냈는데 유난이라는 말이 돌아오면 오래 마음에 남아요",  # 주의사항
        "상위 3.2%",  # MBTI 희귀도(ENTP)
        "수면 우선",  # 충전 방법 · Q07 메커니즘
        "잠이 충분히 채워져야 나머지가 돌아가는 사람이에요",  # 충전 방법 · Q07 첫 문장
        "방해 없는 늦잠",  # 충전 방법 · Q07 키워드
        "침대와 한몸",  # 충전 방법 · Q07 키워드
        "혼자만의 시간",  # 충전 방법 · Q08 키워드
        "관심 분야 탐구",  # 충전 방법 · MBTI 키워드(INTJ)
        "수다 떨기",  # 충전 방법 · MBTI 공통 키워드
        "끝까지 뒤집어 보여주고 싶어져요",  # 주의사항 · MBTI 발작 버튼(ENTP)
        "찰떡궁합 환상의 장난감",  # 궁합 헤드라인
    ]
    for phrase in expected:
        assert phrase in body, f"누락된 문구: {phrase}"

    assert "충전 점수는 API에서 반환하지 않아요" in body
    assert '충전 점수는 <span class="val">90</span> 고정' not in body
