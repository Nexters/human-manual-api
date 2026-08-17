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


def test_result_map_includes_copy_from_every_section() -> None:
    body = render_result_map()

    # 각 결과 영역에서 실제 소스 문구가 페이지에 포함되는지 확인한다.
    expected = [
        "취급주의 상자",  # 포장(A1)
        "전기톱",  # 개봉(B4)
        "브레이크가 고장 난",  # 언박싱 조합(A1 x B4)
        "궁금하면 직진",  # 핵심 특징 · 동원력
        "큰그림을 봐요",  # 핵심 특징 · 타고난 무기(INTJ)
        "정해진 순서를 건너뛰지 않고 현장을 책임지는 헬리콥터",  # 캐릭터 스토리(ESTJ)
        "원리를 알아야 비로소 초점이 잡히는 망원경",  # 캐릭터 스토리(INTP)
        "왜 그러냐고 묻는 대신, 늘 가던 곳에 같이 가서 시간 보내주세요",  # 사용 방법
        "속마음을 꺼냈는데 유난이라는 말이 돌아오면 오래 마음에 남아요",  # 주의사항
        "상위 3.2%",  # MBTI 희귀도(ENTP)
        "잠이 덜 깨면 첫 반응",  # 주의사항 · 보호 시간(after_waking)
        "찰떡궁합 환상의 장난감",  # 궁합 헤드라인
    ]
    for phrase in expected:
        assert phrase in body, f"누락된 문구: {phrase}"

    assert "충전 점수는 API에서 반환하지 않고" in body
    assert '충전 점수는 <span class="val">90</span> 고정' not in body
