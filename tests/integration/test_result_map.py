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
        "내가 기분이 가라앉아 있으면, 왜 그러냐고 묻지 말고 늘 가던 데로 불러내주세요",  # 사용 방법
        "혼자 있는 시간이 길어지면 기운이 빠져서, 연락이 없으면 먼저 찾게 돼요",  # 주의사항 E·밀착
        "사람은 좋은데 하루 종일 붙어 있으면, 어느 순간 혼자 있고 싶어져요",  # 주의사항 E·거리조절
        # 주의사항 I·밀착
        "가까운 사람은 계속 보고 싶은데, 혼자 정리할 틈이 없으면 대답이 짧아져요",
        "혼자 정리할 틈이 없으면 대답이 점점 짧아져요",  # 주의사항 I·거리조절
        # 주의사항 T·직진
        "내 일처럼 해결책을 생각해줬는데 “너 T야?” 소리를 들으면, 그대로 멈춰요",
        # 주의사항 T·탐색
        "생각을 정리해서 조심스럽게 말했는데 “너무 복잡하게 생각해”라고 하면, 대화를 강제 종료해요",
        # 주의사항 F·직진
        "큰맘 먹고 서운하다고 바로 말했는데 “그걸로 왜 그래?”라고 하면, "
        "솔직 버튼을 다시 잠가버려요",
        # 주의사항 F·탐색
        "알아봐 달라고 신호를 보냈는데 “말 안 했잖아”라고 하면, 서운함에 눈물 버튼이 눌려요",
        "상위 3.2%",  # MBTI 희귀도(ENTP)
        "장난꾸러기",  # 상단 키워드 · MBTI(ENTP)
        "도파민 MAX",  # 상단 키워드 · 탐험 극점
        "거리조절 쪽",  # 상단 키워드 · 축 방향 라벨
        "키워드 3",  # 상단 키워드 · 최종 세 번째 슬롯
        "수면 우선",  # 충전 방법 · Q07 메커니즘
        "잠이 충분히 채워져야 나머지가 돌아가는 사람이에요",  # 충전 방법 · Q07 첫 문장
        "충분한 휴식",  # 충전 방법 · Q07 키워드
        "침대와 한몸",  # 충전 방법 · Q07 키워드
        "혼자만의 시간",  # 충전 방법 · Q08 키워드
        "맛있는 음식",  # 충전 방법 · Q08 키워드
        "새로운 환경",  # 충전 방법 · Q08 키워드
        "새로운 생각을 끝없이 펼치는 당신 곁에서",  # 환상의 장난감 설명
        "익숙한 기준과 안전한 순서를 먼저 지키는 모습",  # 환장의 장난감 설명
        "관심 분야 탐구",  # 충전 방법 · MBTI 키워드(INTJ)
        "수다 떨기",  # 충전 방법 · MBTI 공통 키워드
        "끝까지 뒤집어 보여주고 싶어져요",  # 주의사항 · MBTI 발작 버튼(ENTP)
        "환장의 장난감",  # 개인 결과 · 환장 카드
        "찰떡궁합 환상의 장난감",  # 궁합 헤드라인
        "총점 = 거리 .25 + 갈등 .25 + 챙김 .20 + 함께 놀기 .20 + MBTI .10",
        "케미 게이지 · 전체 점수 4구간",
        "케미 게이지",
        "88~100",
        "76~87",
        "64~75",
        "0~63",
        "설명하지 않아도 서로 편한 방식을 자연스럽게 알아봐요.",
        "찰떡 케미",
        "닮은 부분은 편안하고, 다른 부분은 서로의 빈틈을 채워줘요.",
        "달라도 잘 맞아요",
        "서로의 사용법을 알아갈수록 점점 편해지는 사이예요.",
        "맞춰갈수록 좋아요",
        "서로 편한 방식이 달라, 각자의 사용법을 알아갈 시간이 필요해요.",
        "설명서가 필요해요",
        "더 오래 잘 지내려면 · 최고 항목 4개 \N{MULTIPLICATION SIGN} 항목 점수 3개",
        "74~100",
        "60~73",
        "0~59",
        "서운함을 푸는 타이밍을 서로 알아가는 중이에요",
        "둘 다 거리조절 (0~49)",  # 궁합 상세 · 거리감 같은 구간
        "박종하님은 이해선님보다 조금 더 자주 안부를 나눌 때 관계가 편해져요",
        "원하는 간격의 차이가 크지 않아 자연스럽게 맞는 사이예요",
        "서로 원하는 관계의 간격이 달라 조금씩 맞춰갈 필요가 있는 사이예요",
        "둘 다 바로 풀기",  # 궁합 상세 · 갈등 같은 구간
        "박종하님은 생각난 말을 먼저 꺼내고, 이해선님은 표현을 한 번 정리한 뒤",
        "03 챙김 · step1.q12 \N{MULTIPLICATION SIGN} step2.q08",  # 챙김 입력 재료
        "받는 사람이 원하는 위로를 행에서",
        "두 사람의 방향을 각각 계산한 뒤 평균을 챙김 점수로 사용해요",
        "주는 사람이 말로 표현",
        "한 방향 판정표",
        "95 · 잘 닿음",  # 궁합 상세 · 챙김 한 방향 판정
        "68 · 번역 필요",
        "박종하님에게는 상대의 챙김이 잘 닿지만",  # 궁합 상세 · 챙김 한쪽 전달
        "서로 챙기고도 원하는 위로가 바로 전달되지 않을 수 있어요",
        "E탐험 \N{MULTIPLICATION SIGN} E탐험",  # 궁합 상세 · 함께 노는 방식
        "처음 해보는 약속도 쉽게 맞는 사이예요",
        "E탐험 \N{MULTIPLICATION SIGN} I루틴",
        "장소와 분위기를 하나씩 번갈아 맞춰주세요",
        "04 함께 노는 방식 · routine \N{MULTIPLICATION SIGN} E/I",
        "routine 유사도 \N{MULTIPLICATION SIGN} .80 + E/I 적합도 \N{MULTIPLICATION SIGN} .20",
        "새로움에 대한 취향 차이가 크지 않아요",
        "함께 있을 때 맞춤 팁 · 상대의 극단 축 4개 \N{MULTIPLICATION SIGN} 방향 4개",
        "|점수 \N{MINUS SIGN} 50|",
        "애착 → 표현 → 루틴 → 에겐테토",
        "거리조절 → 밀착",
        "혼자 있고 싶은 날에도 짧게 안부를 남겨 상대가 안심할 틈을 주세요!",
        "탐험 → 루틴",
        "가끔은 상대가 좋아하는 단골 코스를 함께 따라가보세요!",
        "에겐 → 테토",
        "상대의 무뚝뚝한 표현보다 직접 챙겨주는 행동을 먼저 봐주세요!",
        "15점 이하와 초과로 나누어 설명",  # 궁합 상세 · 거리감 경계
    ]
    for phrase in expected:
        assert phrase in body, f"누락된 문구: {phrase}"

    for tag in ("동력", "관계", "마음", "강점"):
        assert f'<span class="val">{tag}</span>' in body

    assert "충전 점수는 API에서 반환하지 않아요" in body
    assert '충전 점수는 <span class="val">90</span> 고정' not in body
