"""결과 조합 지도 페이지.

각 결과 칸이 어떤 질문·성향 축에서 나오고 어떤 값이 가능한지 한 페이지로 보여주는
내부 검토용 HTML을 소스 문구에서 직접 생성한다. 문구를 수정하면 페이지도 함께 갱신된다.

`GET /result-map` 에서 서빙한다. 실제 사용자 제출 경로(classify_submission) 기준이다.
"""

from collections.abc import Mapping, Sequence
from functools import lru_cache
from html import escape as _escape

from pakit.domain.assessment import MbtiType
from pakit.domain.assessment_submission import AxisScoresData
from pakit.domain.characters import CHARACTERS
from pakit.services import assessment_classifier as ac
from pakit.services import charging_service as ch
from pakit.services import compatibility_service as cs
from pakit.services import overview_tag_service as ot
from pakit.services import result_content as rc
from pakit.services.result_content import UnboxingItemCopy

MBTI = list(CHARACTERS.keys())  # INTJ, ISTJ, ... 유형군 순서

# 각 중간축군(NT/ST/NF/SF)을 대표하는 실제 MBTI (value[1:3] 이 축군과 일치)
_MIDDLE_GROUP_MBTI = {
    "NT": MbtiType.INTJ,
    "NF": MbtiType.INFJ,
    "ST": MbtiType.ISTJ,
    "SF": MbtiType.ISFJ,
}


def esc(value: object) -> str:
    return _escape(str(value))


def noun(mbti: MbtiType) -> str:
    return CHARACTERS[mbti].noun


# ── 질문 화면 문구 (docs/assessment-content.md 기준) ─────────────────────
Q_TITLE = {
    "step1.q01": "친구들이 나를 찾는 순간은 언제인가요?",
    "step1.q02": "친구들과 있을 때, 송송님과 가장 닮은 토키는?",
    "step1.q05": "절대 건드리면 안 되는 시간은?",
    "step1.q06": "나를 화나게 하는 가장 빠른 방법은?",
    "step1.q07": "기다리던 휴일, 첫 스케줄은?",
    "step1.q08": "약속이 갑자기 취소됐을 때는?",
    "step1.q11": "집에만 있으려던 주말, 나를 밖으로 나오게 한 건?",
    "step1.q12": "기분이 안 좋을 때, 가장 반가운 친구의 연락은?",
    "step2.q02": "서운한 말을 들었을 때 대처는?",
    "step2.q03": "친구와 싸운 뒤 메시지를 보내기 직전에는?",
    "step2.q08": "애정을 표현하는 방식은?",
}

CHOICE = {
    "step1.q01": {
        "decision": "결정이 필요할 때",
        "worries": "고민 있을 때",
        "hangout": "놀 사람 필요할 때",
        "information": "정보 필요할 때",
    },
    "step1.q02": {
        "organize_and_coordinate": "잠깐, 의견 정리해서 방향부터 잡자.",
        "lift_mood": "분위기 왜 이래ㅋㅋ 일단 웃고 보자.",
        "make_it_happen": "재밌겠다. 일단 해보고 생각하자!",
        "care_for_others": "넌 뭐가 좋아? 말해주면 내가 챙길게.",
    },
    "step1.q05": {
        "after_waking": "기상 직후",
        "during_meal": "밥 먹을 때",
        "after_work": "퇴근 직후",
        "late_night": "새벽 감성 타임",
    },
    "step1.q06": {
        "rush": "재촉하기",
        "interrupt": "말 끊기",
        "take_food": "음식 뺏어먹기",
        "arrive_late": "약속 늦기",
        "nag": "잔소리",
        "change_plan": "내 계획 바꾸기",
    },
    "step1.q07": {
        "sleep_until_noon": "낮 12시 기상",
        "morning_run": "아침 러닝",
        "brunch_cafe": "브런치 카페",
        "stay_in_bed": "이불 밖은 위험해",
        "watch_streaming": "밀린 OTT 시청",
        "self_development": "자기개발",
    },
    "step1.q08": {
        "go_to_bed": "당장 침대로 간다",
        "contact_others": "다른 친구한테 연락 돌린다",
        "eat_alone": "혼자라도 식당 가서 먹는다",
        "go_for_drive": "안 가 본 곳으로 드라이브",
    },
    "step1.q11": {
        "curiosity": "궁금한 새 장소",
        "needed_by_someone": "나를 꼭 찾는 친구",
        "clear_goal": "딱 하나 남은 목표",
        "responsibility": "지켜야 할 약속",
        "last_chance": "오늘뿐인 기회",
        "fun": "재밌어 보이는 모임",
    },
    "step1.q12": {
        "listen_to_me": "무슨 일인지 천천히 들어줄게",
        "take_me_out": "일단 나와. 맛있는 거 먹자",
        "give_me_space": "혼자 정리되면 연락해. 기다릴게",
        "solve_together": "내가 같이 해결해볼까?",
        "make_me_laugh": "이거 보고 일단 웃어ㅋㅋ",
    },
    "step2.q02": {
        "hint_and_wait": "티 내며 삭히는 고구마형",
        "resolve_immediately": "바로 풀어야 하는 사이다형",
    },
    "step2.q03": {
        "rehearse_with_ai": "AI와 몇 번이고 상담한다",
        "send_immediately": "고민 없이 바로 보낸다",
    },
    "step2.q08": {
        "express_with_words": "말·리액션·표현으로 채운다",
        "express_with_actions": "말없이 행동으로 보여준다",
    },
}

MIDDLE_GROUP_LABEL = {
    "NT": "NT · 논리탐구",
    "ST": "ST · 현실실용",
    "NF": "NF · 의미공감",
    "SF": "SF · 배려조화",
}

AXES = [
    ("expr", "표현방식", "탐색", "직진", "step2.q01 · q02 · q03", "50↑ 직진"),
    (
        "att",
        "애착유형",
        "거리조절",
        "밀착",
        "step2.q04 · q05 · q06",
        "Q04 50% · Q05 30% · Q06 20% / 50↑ 밀착",
    ),
    ("egen", "에겐테토", "테토", "에겐", "step2.q07 · q08 · q09", "50↑ 에겐"),
    ("rout", "자극추구", "탐험", "루틴", "step2.q10 · q11 · q12", "50↑ 루틴"),
]

A_CODES = {
    "A1": ("직진", "밀착", "취급주의 상자"),
    "A2": ("직진", "거리조절", "미니멀 상자"),
    "A3": ("탐색", "밀착", "마트료시카 상자"),
    "A4": ("탐색", "거리조절", "자물쇠 상자"),
}
B_CODES = {
    "B1": ("루틴", "에겐", "장갑"),
    "B2": ("루틴", "테토", "커터칼"),
    "B3": ("탐험", "에겐", "마술봉"),
    "B4": ("탐험", "테토", "전기톱"),
}


# ── HTML 조각 헬퍼 ───────────────────────────────────────────────────────
def code_chip(code: str) -> str:
    return f'<span class="code">{esc(code)}</span>'


def qchip(qid: str) -> str:
    question = Q_TITLE.get(qid, qid)
    choices = CHOICE.get(qid, {})
    choice_rows = "".join(
        f"<li>{val(value)}<span>{esc(label)}</span></li>" for value, label in choices.items()
    )
    choice_summary = ", ".join(f"{value}: {label}" for value, label in choices.items())
    aria_label = f"{qid}. {question}. 선택지: {choice_summary}"
    return (
        f'<span class="chip chip-q question-chip" tabindex="0" aria-label="{esc(aria_label)}">'
        f"{esc(qid)}"
        f'<span class="question-tooltip" role="tooltip">'
        f'<span class="question-tooltip-id">{esc(qid)}</span>'
        f"<strong>{esc(question)}</strong>"
        f"<ul>{choice_rows}</ul>"
        f"</span>"
        f"</span>"
    )


def axchip(short: str) -> str:
    name = next(a[1] for a in AXES if a[0] == short)
    return f'<span class="chip chip-ax ax-{short}">{esc(name)}</span>'


def mbtichip() -> str:
    return '<span class="chip chip-mbti">MBTI</span>'


def val(value: str) -> str:
    return f'<span class="val">{esc(value)}</span>'


def section(sid: str, kicker: str, title: str, inputs: str, count: str, body: str, note: str = "") -> str:
    note_html = f'<p class="note">{note}</p>' if note else ""
    return f"""
<section id="{sid}" class="card">
  <div class="card-head">
    <div class="card-title">
      <span class="kicker">{esc(kicker)}</span>
      <h2>{esc(title)}</h2>
    </div>
    <span class="count">{esc(count)}</span>
  </div>
  <div class="inputs">{inputs}</div>
  {note_html}
  {body}
</section>"""


def table(headers: Sequence[str], rows: Sequence[Sequence[str]], cls: str = "spec") -> str:
    head = "".join(f"<th>{esc(h)}</th>" for h in headers)
    body_rows = []
    for cells in rows:
        tds = "".join(f"<td>{c}</td>" for c in cells)  # cells already html-safe
        body_rows.append(f'<tr class="row">{tds}</tr>')
    return (
        f'<div class="table-wrap"><table class="{cls}">'
        f"<thead><tr>{head}</tr></thead>"
        f'<tbody>{"".join(body_rows)}</tbody></table></div>'
    )


def _build_sections() -> list[tuple[str, str, str, str, str, str]]:
    sections: list[tuple[str, str, str, str, str, str]] = []

    # ── 0. 축 & 코드 범례 ────────────────────────────────────────────────
    axis_rows = []
    for short, _name, neg, pos, qs, rule in AXES:
        axis_rows.append(
            [
                axchip(short),
                f'<span class="pole neg">{esc(neg)}</span> <span class="arrow">0 ↔ 100</span> '
                f'<span class="pole pos">{esc(pos)}</span>',
                f'<span class="q-inline">{esc(qs)}</span>',
                f'<span class="rule">{esc(rule)}</span>',
            ]
        )
    axis_table = table(["축", "양극 (내부점수)", "판정 질문 3개", "분류 규칙"], axis_rows)

    a_rows = [[code_chip(c), esc(n), f"표현 {esc(p1)}", f"애착 {esc(p2)}"]
              for c, (p1, p2, n) in A_CODES.items()]
    a_table = table(["코드", "포장 상자", "표현방식", "애착유형"], a_rows)
    b_rows = [[code_chip(c), esc(n), f"자극 {esc(p1)}", f"에겐테토 {esc(p2)}"]
              for c, (p1, p2, n) in B_CODES.items()]
    b_table = table(["코드", "개봉 도구", "자극추구", "에겐테토"], b_rows)

    legend_body = f"""
<p class="lead">STEP2의 12문항이 <b>4개 성향 축</b>으로 집계되고, 그 축을 둘씩 묶어
<b>포장 코드(A1–A4)</b>와 <b>개봉 코드(B1–B4)</b>가 정해져요. 아래 코드가 여러 결과 칸에서
반복 사용되니 먼저 봐두면 편해요. MBTI는 22문항으로 채점하지 않고 사용자가 직접 제출해요.</p>
{axis_table}
<div class="two-col">
  <div><h4>포장 코드 · A = 표현 × 애착</h4>{a_table}</div>
  <div><h4>개봉 코드 · B = 자극 × 에겐테토</h4>{b_table}</div>
</div>"""
    sections.append(("legend", "기초", "성향 축과 A·B 코드", "", "축 4 · 코드 8", legend_body))

    # ── 1. 제품 이름 ─────────────────────────────────────────────────────
    adj_head = "".join(f"<th>{code_chip(b)}</th>" for b in B_CODES)
    adj_body = []
    for a in A_CODES:
        cells = [f'<th class="rowh">{code_chip(a)}</th>']
        for b in B_CODES:
            cells.append(f'<td class="row">{esc(ac.ADJECTIVES[(a, b)])}</td>')
        adj_body.append(f"<tr>{''.join(cells)}</tr>")
    adj_matrix = (
        '<div class="table-wrap"><table class="spec matrix">'
        f'<thead><tr><th class="corner">형용사 A×B</th>{adj_head}</tr></thead>'
        f'<tbody>{"".join(adj_body)}</tbody></table></div>'
    )
    noun_table = table(["MBTI", "명사(캐릭터)"], [[code_chip(m.value), esc(noun(m))] for m in MBTI])
    rarity_table = table(
        ["MBTI", "희귀도"],
        [[code_chip(m.value), esc(rc.MBTI_RARITY_COPY[m])] for m in MBTI],
    )
    mbti_tag_table = table(
        ["MBTI", "대표 키워드"],
        [[code_chip(m.value), esc(ot.MBTI_OVERVIEW_TAG[m])] for m in MBTI],
    )
    axis_tag_label = {
        ("attachment", "low"): ("애착유형", "거리조절 쪽"),
        ("attachment", "high"): ("애착유형", "밀착 쪽"),
        ("expression", "low"): ("표현방식", "탐색 쪽"),
        ("expression", "high"): ("표현방식", "직진 쪽"),
        ("routine", "low"): ("자극추구", "탐험 쪽"),
        ("routine", "high"): ("자극추구", "루틴 쪽"),
        ("egen", "low"): ("에겐테토", "테토 쪽"),
        ("egen", "high"): ("에겐테토", "에겐 쪽"),
    }
    axis_tag_table = table(
        ["성향 축", "강한 방향", "대표 키워드"],
        [
            [esc(axis_tag_label[key][0]), esc(axis_tag_label[key][1]), esc(tag)]
            for key, tag in ot.AXIS_OVERVIEW_TAG.items()
        ],
    )
    overview_tag_slots = table(
        ["최종 결과", "출처", "선정 규칙", "예시"],
        [
            ["키워드 1", "MBTI", "제출한 MBTI의 대표 키워드", "장난꾸러기"],
            ["키워드 2", "성향 축", "50점에서 가장 멀리 떨어진 축", "도파민 MAX"],
            ["키워드 3", "성향 축", "두 번째로 멀리 떨어진 축", "혼자서도 잘 놀아요"],
        ],
    )
    overview_body = f"""
<p class="lead">결과 이름 = <b>형용사 + 명사</b>. 형용사는 A·B 코드(4축)에서, 명사는 MBTI에서
나와요. 이론상 16 형용사 × 16 명사 = 256가지 이름.</p>
<h4>형용사 16 · A코드(세로) × B코드(가로)</h4>
{adj_matrix}
<div class="two-col">
  <div><h4>명사 16 · MBTI별</h4>{noun_table}</div>
  <div><h4>희귀도 16 · MBTI별</h4>{rarity_table}</div>
</div>
<h4>상단 키워드 · MBTI 1개 + 강한 성향 축 2개</h4>
<p>네 성향 축 중 50점에서 가장 멀리 떨어진 두 축을 사용해요. 동점 우선순위는
애착유형 → 표현방식 → 자극추구 → 에겐테토.</p>
{overview_tag_slots}
<h4>키워드 원본 문구</h4>
<div class="two-col">
  <div>{mbti_tag_table}</div>
  <div>{axis_tag_table}</div>
</div>"""
    sections.append(
        (
            "overview",
            "결과 · overview",
            "제품 이름",
            f"{axchip('expr')}{axchip('att')}{axchip('egen')}{axchip('rout')}{mbtichip()}",
            "최종 키워드 3개 · 원본 문구 24개",
            overview_body,
        )
    )

    # ── 2. 언박싱 키트 ───────────────────────────────────────────────────
    combo_rows = []
    for a in A_CODES:
        for b in B_CODES:
            c = rc.COMBINATION_COPY[(a, b)]
            combo_rows.append([f"{code_chip(a)}{code_chip(b)}", f"<b>{esc(c.title)}</b>", esc(c.description)])
    combo_table = table(["코드", "조합 제목", "설명"], combo_rows)

    def unboxing_cards(copy_map: Mapping[str, UnboxingItemCopy], codes: Sequence[str]) -> str:
        cards = []
        for code in codes:
            item = copy_map[code]
            tags = " · ".join(item.tags)
            cards.append(
                f'<div class="ub-card"><div class="ub-top">{code_chip(code)}<b>{esc(item.name)}</b>'
                f'<span class="ub-tags">{esc(tags)}</span></div>'
                f'<p class="row">{esc(item.reason)}</p></div>'
            )
        return f'<div class="ub-grid">{"".join(cards)}</div>'

    unboxing_body = f"""
<p class="lead">API 응답은 포장·개봉 설명을 각각 A·B 코드별 4종에서 골라 반환해요.
A×B 조합 제목·설명은 기존 결과 스냅샷 복원용 내부 데이터이며 새 API 응답에는 포함되지 않아요.</p>
<h4>조합 제목 + 설명 · 16 (API 미반환)</h4>
{combo_table}
<h4>포장 상자 설명 · 4 (A코드)</h4>
{unboxing_cards(rc.PACKAGING_COPY, list(A_CODES))}
<h4>개봉 도구 설명 · 4 (B코드)</h4>
{unboxing_cards(rc.OPENING_TOOL_COPY, list(B_CODES))}"""
    sections.append(
        (
            "unboxing",
            "결과 · unboxing_kit",
            "언박싱 키트 (포장·개봉)",
            f"{axchip('expr')}{axchip('att')}{axchip('egen')}{axchip('rout')}",
            "조합 16 · 상자 4 · 도구 4",
            unboxing_body,
        )
    )

    # ── 3. 핵심 특징 (4슬롯) ─────────────────────────────────────────────
    mot_title_table = table(
        ["value", "제목", "step1.q11 선택지"],
        [[val(k), f"<b>{esc(v.title)}</b>", esc(CHOICE["step1.q11"][k])]
         for k, v in rc.MOTIVATION_COPY.items()],
    )
    mot_desc_rows = []
    for k in rc.MOTIVATION_COPY:
        for g in ["NT", "ST", "NF", "SF"]:
            mot_desc_rows.append([f"{val(k)} × {val(g)}", esc(rc.MOTIVATION_DESCRIPTION[(k, g)])])
    mot_desc_table = table(["동기 × MBTI중간축", "설명 문구"], mot_desc_rows)

    rel_rows = []
    for q1 in CHOICE["step1.q01"]:
        for q2 in CHOICE["step1.q02"]:
            fc = rc.RELATIONSHIP_ROLE_COPY[(q1, q2)]
            rel_rows.append([f"{val(q1)} × {val(q2)}", f"<b>{esc(fc.title)}</b>", esc(fc.description)])
    rel_table = table(["q01(상황) × q02(역할)", "제목", "설명"], rel_rows)

    emo_label = {
        ("direct", "egen"): "직진 · 에겐",
        ("direct", "teto"): "직진 · 테토",
        ("explore", "egen"): "탐색 · 에겐",
        ("explore", "teto"): "탐색 · 테토",
    }
    emo_rows = [[esc(lab), f"<b>{esc(rc.EMOTIONAL_PROCESSING_COPY[key].title)}</b>",
                 esc(rc.EMOTIONAL_PROCESSING_COPY[key].description)]
                for key, lab in emo_label.items()]
    emo_table = table(["표현축 × 에겐테토축", "제목", "설명"], emo_rows)

    str_table = table(
        ["MBTI", "제목", "설명"],
        [[code_chip(m.value), f"<b>{esc(rc.MBTI_STRENGTH_COPY[m].title)}</b>",
          esc(rc.MBTI_STRENGTH_COPY[m].description)] for m in MBTI],
    )
    features_body = f"""
<p class="lead">항상 <b>동원력 · 관계 속의 나 · 마음 정리법 · 타고난 무기</b> 4개를 이 순서로 반환해요.</p>
<div class="slot"><h4><span class="slot-n">1</span> 동원력 · <span class="src">step1.q11 × MBTI중간축(NT/ST/NF/SF)</span></h4>
<div class="two-col"><div>{mot_title_table}</div><div>{mot_desc_table}</div></div></div>
<div class="slot"><h4><span class="slot-n">2</span> 관계 속의 나 · <span class="src">step1.q01 × step1.q02</span></h4>{rel_table}</div>
<div class="slot"><h4><span class="slot-n">3</span> 마음 정리법 · <span class="src">표현방식축 × 에겐테토축</span></h4>{emo_table}</div>
<div class="slot"><h4><span class="slot-n">4</span> 타고난 무기 · <span class="src">MBTI 16종</span></h4>{str_table}</div>"""
    sections.append(
        (
            "features",
            "결과 · features",
            "핵심 특징 (4슬롯)",
            f"{qchip('step1.q11')}{qchip('step1.q01')}{qchip('step1.q02')}"
            f"{axchip('expr')}{axchip('egen')}{mbtichip()}",
            "6 · 24 · 16 · 4 · 16",
            features_body,
        )
    )

    # ── 4. 캐릭터 소개 ───────────────────────────────────────────────────
    story_table = table(
        ["MBTI", "명사", "소제목", "스토리"],
        [[code_chip(m.value), esc(noun(m)), f"<b>{esc(rc.CHARACTER_STORY_COPY[m].title)}</b>",
          esc(rc.CHARACTER_STORY_COPY[m].description)] for m in MBTI],
    )
    sections.append(
        (
            "story",
            "결과 · character_story",
            "캐릭터 소개",
            mbtichip(),
            "16",
            f'<p class="lead">MBTI 16종별 캐릭터 스토리. 모두 “~가 도착했습니다”로 끝나요.</p>{story_table}',
        )
    )

    # ── 5. 이렇게 다뤄주세요 (4슬롯) ─────────────────────────────────────
    sup_rows = []
    for k in CHOICE["step1.q12"]:
        for g in ["NT", "ST", "NF", "SF"]:
            sup_rows.append([f"{val(k)} × {val(g)}", esc(rc.SUPPORT_PREFERENCE_COPY[(k, g)])])
    sup_table = table(["q12(원하는 도움) × MBTI중간축", "문구"], sup_rows)
    dist_table = table(
        ["애착 점수", "문구"],
        [
            ["<span class='val'>0~24</span>", esc(rc.RELATIONSHIP_DISTANCE_COPY["0_24"])],
            ["<span class='val'>25~49</span>", esc(rc.RELATIONSHIP_DISTANCE_COPY["25_49"])],
            ["<span class='val'>50~74</span>", esc(rc.RELATIONSHIP_DISTANCE_COPY["50_74"])],
            ["<span class='val'>75~100</span>", esc(rc.RELATIONSHIP_DISTANCE_COPY["75_100"])],
        ],
    )
    conf_table = table(
        ["step2.q02 × step2.q03", "Q02 선택지", "Q03 선택지", "문구"],
        [
            [
                f"{val(conflict_style)} × {val(message_style)}",
                esc(CHOICE["step2.q02"][conflict_style]),
                esc(CHOICE["step2.q03"][message_style]),
                esc(copy),
            ]
            for (conflict_style, message_style), copy in rc.CONFLICT_SUPPORT_COPY.items()
        ],
    )
    attraction_table = table(
        ["MBTI", "문구"],
        [
            [f"<span class='val'>{esc(mbti.value)}</span>", esc(copy)]
            for mbti, copy in rc.ATTRACTION_GUIDE_COPY.items()
        ],
    )
    cando_body = f"""
<p class="lead">순서 고정: <b>원하는 도움 · 관계 거리 · 갈등 푸는 법 · 호감 포인트</b>.</p>
<div class="slot"><h4><span class="slot-n">1</span> 힘들 때 원하는 도움 · <span class="src">step1.q12 × MBTI중간축</span></h4>{sup_table}</div>
<div class="two-col">
  <div class="slot"><h4><span class="slot-n">2</span> 편안한 관계 거리 · <span class="src">애착 점수</span></h4>{dist_table}</div>
  <div class="slot"><h4><span class="slot-n">3</span> 갈등을 푸는 방식 · <span class="src">step2.q02 × step2.q03</span></h4>{conf_table}</div>
</div>
<div class="slot"><h4><span class="slot-n">4</span> 호감 포인트 · <span class="src">MBTI 16종</span></h4>{attraction_table}</div>"""
    sections.append(
        (
            "cando",
            "결과 · can_do",
            "이렇게 다뤄주세요 (4슬롯)",
            f"{qchip('step1.q12')}{qchip('step2.q02')}{qchip('step2.q03')}"
            f"{axchip('att')}{mbtichip()}",
            "20 · 4 · 4 · 16",
            cando_body,
        )
    )

    # ── 6. 이렇게 하면 고장나요 (4슬롯) ──────────────────────────────────
    comm_table = table(
        ["MBTI T/F", "문구"],
        [["<span class='val'>T</span>", esc(rc.COMMUNICATION_WARNING_COPY["T"])],
         ["<span class='val'>F</span>", esc(rc.COMMUNICATION_WARNING_COPY["F"])]],
    )
    soc_table = table(
        ["MBTI E/I × 애착유형", "문구"],
        [
            [
                "<span class='val'>E · 밀착</span>",
                esc(rc.SOCIAL_ENERGY_WARNING_COPY[("E", "high")]),
            ],
            [
                "<span class='val'>E · 거리조절</span>",
                esc(rc.SOCIAL_ENERGY_WARNING_COPY[("E", "low")]),
            ],
            [
                "<span class='val'>I · 밀착</span>",
                esc(rc.SOCIAL_ENERGY_WARNING_COPY[("I", "high")]),
            ],
            [
                "<span class='val'>I · 거리조절</span>",
                esc(rc.SOCIAL_ENERGY_WARNING_COPY[("I", "low")]),
            ],
        ],
    )
    anger_table = table(
        ["step1.q06", "선택지", "문구"],
        [[val(k), esc(CHOICE["step1.q06"][k]), esc(rc.ANGER_TRIGGER_WARNING_COPY[k])]
         for k in CHOICE["step1.q06"]],
    )
    mbti_trigger_table = table(
        ["MBTI", "문구"],
        [[code_chip(k.value), esc(v)] for k, v in rc.MBTI_TRIGGER_WARNING_COPY.items()],
    )
    warn_body = f"""
<p class="lead">순서 고정: <b>대화 상처 · 사회적 에너지 · 분노 버튼 · 유형별 발작 버튼</b>.
Q06은 사용자가 고른 걸 그대로, 첫 슬롯은 MBTI T/F, 두 번째 슬롯은 MBTI E/I×애착유형, 마지막 슬롯은 MBTI 네 글자 전체를 써요.</p>
<div class="two-col">
  <div class="slot"><h4><span class="slot-n">1</span> 대화에서 상처받는 지점 · <span class="src">MBTI T/F</span></h4>{comm_table}</div>
  <div class="slot"><h4><span class="slot-n">2</span> 사회적 에너지 경계 · <span class="src">MBTI E/I × 애착유형</span></h4>{soc_table}</div>
</div>
<div class="slot"><h4><span class="slot-n">3</span> 가장 빠른 분노 버튼 · <span class="src">step1.q06</span></h4>{anger_table}</div>
<div class="slot"><h4><span class="slot-n">4</span> 유형별 발작 버튼 · <span class="src">MBTI</span></h4>{mbti_trigger_table}</div>"""
    sections.append(
        (
            "warnings",
            "결과 · warnings",
            "이렇게 하면 고장나요 (4슬롯)",
            f"{qchip('step1.q06')}{axchip('att')}{mbtichip()}",
            "2 · 4 · 6 · 16",
            warn_body,
        )
    )

    # ── 7. 충전 방법 ─────────────────────────────────────────────────────
    clause_table = table(
        ["step1.q07", "선택지", "메커니즘", "첫 문장"],
        [[val(k), esc(CHOICE["step1.q07"][k]), esc(ch.BASE_CHARGING_MECHANISM[k]),
          esc(ch.BASE_CHARGING_CLAUSE[k])]
         for k in ch.BASE_CHARGING_CLAUSE],
    )
    trigger_table = table(
        ["step1.q11", "선택지", "두 번째 문장"],
        [[val(k), esc(CHOICE["step1.q11"][k]), esc(ch.MOTIVATION_TRIGGER_DESCRIPTION[k])]
         for k in ch.MOTIVATION_TRIGGER_DESCRIPTION],
    )
    kw1 = table(["step1.q07", "키워드"], [[val(k), esc(v)] for k, v in ch.BASE_CHARGING_KEYWORD.items()])
    kw2 = table(["step1.q08", "키워드"], [[val(k), esc(v)] for k, v in ch.EMERGENCY_CHARGING_KEYWORD.items()])
    kw3 = table(["MBTI", "키워드"], [[code_chip(k.value), esc(v)] for k, v in ch.MBTI_CHARGING_KEYWORD.items()])
    charge_body = f"""
<p class="lead">메인 설명 = <b>[Q07 첫 문장] + [Q11 두 번째 문장]</b> → 6 × 6 = 36가지.
키워드 3개는 Q07·Q08·MBTI에서 각각 만들어요. 충전 점수는 API에서 반환하지 않아요.</p>
<div class="two-col"><div>{clause_table}</div><div>{trigger_table}</div></div>
<h4>키워드 3개 · Q07(평소회복) / Q08(환기) / MBTI(유형별 회복)</h4>
<div class="three-col">{kw1}{kw2}{kw3}</div>"""
    sections.append(
        (
            "charging",
            "결과 · charging",
            "충전 방법",
            f"{qchip('step1.q07')}{qchip('step1.q11')}{qchip('step1.q08')}{mbtichip()}",
            "문장 36 · 키워드 6·4·16",
            charge_body,
        )
    )

    # ── 8. 함께하면 좋은 친구 ────────────────────────────────────────────
    friend_map_table = table(
        ["내 MBTI", "추천 친구(잘 맞음)", "반대 친구"],
        [[code_chip(m.value),
          f"{esc(cs.PRIMARY_COMPATIBLE_MBTI[m].value)} · {esc(noun(cs.PRIMARY_COMPATIBLE_MBTI[m]))}",
          f"{esc(cs.OPPOSITE_MBTI[m].value)} · {esc(noun(cs.OPPOSITE_MBTI[m]))}"] for m in MBTI],
    )
    prim_desc_table = table(
        ["MBTI 중간 2축", "추천 친구 설명"],
        [[esc(MIDDLE_GROUP_LABEL[g]), esc(cs._primary_friend_description(_MIDDLE_GROUP_MBTI[g]))]
         for g in ["NT", "NF", "ST", "SF"]],
    )

    def opp(routine: int, attachment: int) -> str:
        scores = AxisScoresData(attachment=attachment, expression=0, routine=routine, egen=0)
        return esc(cs._opposite_friend_description(scores))

    opp_desc_table = table(
        ["자극 · 애착 사분면", "반대 친구 설명"],
        [
            ["탐험 · 거리조절", opp(0, 0)],
            ["탐험 · 밀착", opp(0, 100)],
            ["루틴 · 거리조절", opp(100, 0)],
            ["루틴 · 밀착", opp(100, 100)],
        ],
    )
    friend_body = f"""
<p class="lead">개인 결과에 카드 2장. 추천 장난감은 MBTI로 고르고(잘 맞는 유형 / 반대 유형),
설명 문구는 축을 보조로 써요.</p>
<h4>추천/반대 MBTI 매핑 · 16</h4>
{friend_map_table}
<div class="two-col">
  <div><h4>추천 친구 설명 · 4 (MBTI 중간축)</h4>{prim_desc_table}</div>
  <div><h4>반대 친구 설명 · 4 (자극×애착)</h4>{opp_desc_table}</div>
</div>"""
    sections.append(
        (
            "friends",
            "결과 · compatible_friends",
            "함께하면 좋은 친구",
            f"{mbtichip()}{axchip('rout')}{axchip('att')}",
            "매핑 16 · 설명 4+4",
            friend_body,
        )
    )

    # ── 9. 궁합 결과 (두 사람) ───────────────────────────────────────────
    head_table = table(
        ["총점 구간", "헤드라인", "설명"],
        [[f"{lo}점~", f"<b>{esc(t)}</b>", esc(d)]
         for lo, (t, d) in [
             (88, cs.compatibility_headline(90)),
             (76, cs.compatibility_headline(80)),
             (64, cs.compatibility_headline(70)),
             (0, cs.compatibility_headline(50)),
         ]],
    )
    dim_rows = []
    for key in ["distance", "conflict", "care", "pace"]:
        title, desc, _short = cs.DIMENSION_COPY[key]
        dim_rows.append([val(key), f"<b>{esc(title)}</b>", esc(desc), esc(cs.RELATIONSHIP_STRENGTH_COPY[key])])
    dim_table = table(["항목", "이름", "설명", "강점 문구"], dim_rows)
    habit_table = table(["항목", "관계 습관 팁"], [[val(k), esc(v)] for k, v in cs.RELATIONSHIP_HABIT_COPY.items()])
    tip_table = table(["상대 support_preference", "맞춤 팁"], [[val(k), esc(v)] for k, v in cs.SUPPORT_TIPS.items()])
    compat_body = f"""
<p class="lead">두 사람 결과를 비교해 5개 점수(거리감·대화복구력·챙김·호흡·MBTI)를 가중합해요.
<span class="val">총점 = 거리 .20 + 갈등 .20 + 챙김 .15 + 호흡 .15 + MBTI .30</span>.
상세 문장은 두 사람의 점수차·닉네임으로 실시간 생성돼서 조합이 매우 많아요 — 아래는 뼈대만.</p>
<h4>총점 → 헤드라인 · 4구간</h4>
{head_table}
<h4>4개 세부 항목</h4>
{dim_table}
<div class="two-col">
  <div><h4>관계 습관 팁 · 4</h4>{habit_table}</div>
  <div><h4>약한 항목별 맞춤 팁 (support 기준) · 5</h4>{tip_table}</div>
</div>"""
    sections.append(
        (
            "compat",
            "궁합 결과 · 두 사람",
            "궁합 (compatibility)",
            f"{qchip('step1.q01')}{qchip('step1.q02')}{qchip('step1.q11')}{qchip('step1.q12')}"
            f"{qchip('step2.q02')}{qchip('step2.q08')}{axchip('att')}{axchip('expr')}"
            f"{axchip('rout')}{mbtichip()}",
            "구간 4 · 항목 4 · 팁 4+5",
            compat_body,
        )
    )

    return sections


_CSS = """
:root{
  --bg:#f6f7fb; --surface:#ffffff; --surface-2:#f1f3f9; --text:#1a1d29;
  --text-dim:#5a5f72; --border:#e4e7f0; --border-strong:#d2d6e4;
  --accent:#4b5bd0; --accent-soft:#e9ecfb; --mono-bg:#eceffa; --mono-text:#3a4170;
  --ax-expr:#b1741a; --ax-att:#bb4f74; --ax-egen:#6f52c9; --ax-rout:#1f8479;
  --shadow:0 1px 2px rgba(24,28,50,.04),0 4px 16px rgba(24,28,50,.05);
}
@media (prefers-color-scheme:dark){
  :root{
    --bg:#0f1016; --surface:#171922; --surface-2:#1f222e; --text:#e7e8f1;
    --text-dim:#9a9fb4; --border:#2a2d3b; --border-strong:#363a4d;
    --accent:#8b9bf3; --accent-soft:#20243d; --mono-bg:#22273a; --mono-text:#aeb6e6;
    --ax-expr:#e0a24d; --ax-att:#e688ab; --ax-egen:#a892f0; --ax-rout:#54bcae;
    --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 20px rgba(0,0,0,.28);
  }
}
:root[data-theme="light"]{
  --bg:#f6f7fb; --surface:#ffffff; --surface-2:#f1f3f9; --text:#1a1d29;
  --text-dim:#5a5f72; --border:#e4e7f0; --border-strong:#d2d6e4;
  --accent:#4b5bd0; --accent-soft:#e9ecfb; --mono-bg:#eceffa; --mono-text:#3a4170;
  --ax-expr:#b1741a; --ax-att:#bb4f74; --ax-egen:#6f52c9; --ax-rout:#1f8479;
  --shadow:0 1px 2px rgba(24,28,50,.04),0 4px 16px rgba(24,28,50,.05);
}
:root[data-theme="dark"]{
  --bg:#0f1016; --surface:#171922; --surface-2:#1f222e; --text:#e7e8f1;
  --text-dim:#9a9fb4; --border:#2a2d3b; --border-strong:#363a4d;
  --accent:#8b9bf3; --accent-soft:#20243d; --mono-bg:#22273a; --mono-text:#aeb6e6;
  --ax-expr:#e0a24d; --ax-att:#e688ab; --ax-egen:#a892f0; --ax-rout:#54bcae;
  --shadow:0 1px 2px rgba(0,0,0,.3),0 6px 20px rgba(0,0,0,.28);
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--text);
  font-family:'Pretendard','Apple SD Gothic Neo',-apple-system,BlinkMacSystemFont,'Malgun Gothic',system-ui,sans-serif;
  line-height:1.6;-webkit-font-smoothing:antialiased;}
.mono,.code,.val,.count,.nav-count,td,th{font-variant-numeric:tabular-nums}
a{color:var(--accent);text-decoration:none}
.topbar{position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);
  backdrop-filter:blur(10px);border-bottom:1px solid var(--border);
  display:flex;align-items:center;gap:16px;padding:12px 24px;flex-wrap:wrap}
.topbar h1{font-size:15px;margin:0;letter-spacing:-.01em;font-weight:700}
.topbar .sub{color:var(--text-dim);font-size:12.5px}
.filter{margin-left:auto;display:flex;align-items:center;gap:8px}
.filter input{background:var(--surface);border:1px solid var(--border-strong);color:var(--text);
  border-radius:8px;padding:7px 11px;font-size:13px;width:220px;font-family:inherit}
.filter input:focus{outline:2px solid var(--accent);outline-offset:1px}
.theme-btn{background:var(--surface);border:1px solid var(--border-strong);color:var(--text-dim);
  border-radius:8px;padding:7px 10px;font-size:12px;cursor:pointer;font-family:inherit}
.layout{max-width:1240px;margin:0 auto;padding:24px;display:grid;
  grid-template-columns:200px minmax(0,1fr);gap:32px;align-items:start}
nav.toc{position:sticky;top:72px;display:flex;flex-direction:column;gap:1px;font-size:13px}
nav.toc a{display:flex;justify-content:space-between;gap:8px;align-items:baseline;
  color:var(--text-dim);padding:6px 10px;border-radius:7px;border-left:2px solid transparent}
nav.toc a:hover{background:var(--surface-2);color:var(--text)}
nav.toc a.active{color:var(--text);background:var(--surface-2);border-left-color:var(--accent);font-weight:600}
.nav-count{font-size:10.5px;color:var(--text-dim);font-weight:400;white-space:nowrap}
main{display:flex;flex-direction:column;gap:20px;min-width:0}
.card{background:var(--surface);border:1px solid var(--border);border-radius:14px;
  padding:22px 24px;box-shadow:var(--shadow);scroll-margin-top:64px}
.card-head{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;margin-bottom:12px}
.kicker{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--accent);font-weight:700;
  font-family:ui-monospace,'SF Mono',Menlo,monospace}
.card-title h2{margin:3px 0 0;font-size:21px;letter-spacing:-.02em;font-weight:750;text-wrap:balance}
.count{flex:none;font-size:11.5px;color:var(--text-dim);background:var(--surface-2);
  border:1px solid var(--border);border-radius:20px;padding:4px 11px;font-family:ui-monospace,monospace}
.inputs{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:6px}
.note{font-size:12.5px;color:var(--text-dim);margin:4px 0 0}
.lead{font-size:13.5px;color:var(--text-dim);margin:6px 0 16px;max-width:70ch}
.lead b{color:var(--text);font-weight:650}
.chip{display:inline-flex;align-items:center;font-size:11.5px;padding:3px 9px;border-radius:20px;
  font-weight:600;border:1px solid transparent;white-space:nowrap}
.chip-q{background:var(--mono-bg);color:var(--mono-text);font-family:ui-monospace,'SF Mono',Menlo,monospace;
  border-color:var(--border-strong)}
.question-chip{position:relative;cursor:help;outline:none}
.question-chip:focus-visible{box-shadow:0 0 0 2px var(--surface),0 0 0 4px var(--accent)}
.question-tooltip{position:absolute;z-index:50;top:calc(100% + 9px);left:0;width:max-content;
  max-width:min(440px,calc(100vw - 40px));padding:13px 14px;border:1px solid var(--border-strong);
  border-radius:10px;background:var(--surface);color:var(--text);box-shadow:0 12px 32px rgba(0,0,0,.22);
  font-family:system-ui,-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;font-size:12px;
  font-weight:400;line-height:1.45;white-space:normal;opacity:0;visibility:hidden;pointer-events:none;
  transform:translateY(-3px);transition:opacity .12s ease,transform .12s ease,visibility .12s}
.question-chip:hover .question-tooltip,.question-chip:focus .question-tooltip{opacity:1;visibility:visible;
  transform:translateY(0)}
.question-tooltip-id{display:block;margin-bottom:3px;color:var(--accent);font-family:ui-monospace,
  'SF Mono',Menlo,monospace;font-size:10.5px;font-weight:700}
.question-tooltip strong{display:block;font-size:13px;margin-bottom:8px}
.question-tooltip ul{display:grid;gap:6px;margin:0;padding:0;list-style:none}
.question-tooltip li{display:grid;grid-template-columns:minmax(92px,max-content) 1fr;gap:8px;
  align-items:start;color:var(--text-dim)}
.question-tooltip .val{color:var(--text)}
.inputs .question-chip:last-of-type .question-tooltip{right:0;left:auto}
.chip-mbti{background:var(--accent-soft);color:var(--accent);border-color:color-mix(in srgb,var(--accent) 25%,transparent)}
.chip-ax{color:#fff}
.ax-expr{background:var(--ax-expr)} .ax-att{background:var(--ax-att)}
.ax-egen{background:var(--ax-egen)} .ax-rout{background:var(--ax-rout)}
@media (prefers-color-scheme:dark){.chip-ax{color:#12131a}}
:root[data-theme="dark"] .chip-ax{color:#12131a}
:root[data-theme="light"] .chip-ax{color:#fff}
.code{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:12px;font-weight:700;
  background:var(--accent-soft);color:var(--accent);padding:2px 7px;border-radius:6px;margin-right:3px;
  border:1px solid color-mix(in srgb,var(--accent) 20%,transparent)}
.val{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:11.5px;color:var(--text-dim);
  background:var(--surface-2);padding:1px 6px;border-radius:5px;border:1px solid var(--border)}
h4{font-size:13.5px;margin:22px 0 9px;letter-spacing:-.01em;font-weight:700;
  display:flex;align-items:center;gap:8px;flex-wrap:wrap}
h4 .src{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:11px;color:var(--text-dim);
  font-weight:500;background:var(--surface-2);padding:2px 8px;border-radius:6px;border:1px solid var(--border)}
.slot-n{flex:none;width:20px;height:20px;border-radius:6px;background:var(--accent);color:#fff;
  display:inline-flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;
  font-family:ui-monospace,monospace}
.slot{border-top:1px solid var(--border);padding-top:4px;margin-top:4px}
.slot:first-of-type{border-top:0}
.table-wrap{overflow-x:auto;border:1px solid var(--border);border-radius:10px;margin:2px 0}
table.spec{border-collapse:collapse;width:100%;font-size:13px;min-width:min(100%,540px)}
table.spec th,table.spec td{text-align:left;padding:9px 12px;vertical-align:top;border-bottom:1px solid var(--border)}
table.spec thead th{position:sticky;top:0;background:var(--surface-2);color:var(--text-dim);
  font-size:11px;letter-spacing:.03em;text-transform:uppercase;font-weight:700;z-index:1;white-space:nowrap}
table.spec tbody tr:last-child td{border-bottom:0}
table.spec tbody tr:hover td{background:var(--surface-2)}
table.spec td b{font-weight:650}
.matrix th.rowh,.matrix th.corner{background:var(--surface-2);font-weight:700;white-space:nowrap}
.matrix td{font-size:12.5px}
.matrix .corner{font-size:10.5px;text-transform:none;letter-spacing:0}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:18px}
.three-col{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
@media (max-width:760px){.two-col,.three-col{grid-template-columns:1fr}}
.pole{font-weight:700;font-size:12px} .pole.neg{color:var(--text-dim)} .pole.pos{color:var(--text)}
.arrow{color:var(--text-dim);font-size:11px;margin:0 4px;font-family:ui-monospace,monospace}
.q-inline,.rule{font-family:ui-monospace,'SF Mono',Menlo,monospace;font-size:11.5px;color:var(--text-dim)}
.rule{color:var(--accent)}
.ub-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media (max-width:760px){.ub-grid{grid-template-columns:1fr}}
.ub-card{border:1px solid var(--border);border-radius:10px;padding:13px 15px;background:var(--surface-2)}
.ub-top{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:6px;font-size:14px}
.ub-tags{font-size:11px;color:var(--text-dim);margin-left:auto;font-weight:500}
.ub-card p{margin:0;font-size:12.5px;color:var(--text-dim)}
.fixed-note{border:1px dashed var(--border-strong);border-radius:10px;padding:14px 16px;
  background:var(--surface-2);align-self:start}
.fixed-note ul{margin:8px 0 0;padding-left:18px;font-size:12.5px;color:var(--text-dim)}
.fixed-note li{margin:4px 0}
.fixed-note b{color:var(--text)}
.hidden{display:none!important}
footer{max-width:1240px;margin:0 auto;padding:8px 24px 48px;color:var(--text-dim);font-size:11.5px;
  font-family:ui-monospace,'SF Mono',Menlo,monospace}
@media (max-width:900px){
  .layout{grid-template-columns:1fr;gap:16px}
  nav.toc{position:static;flex-direction:row;flex-wrap:wrap;gap:6px;
    border:1px solid var(--border);padding:10px;border-radius:12px;background:var(--surface)}
  nav.toc a{border-left:0;border:1px solid var(--border)}
  nav.toc .nav-count{display:none}
}
@media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
"""

_JS = """
const q=document.getElementById('flt');
const rows=[...document.querySelectorAll('tr.row, td.row')];
const cards=[...document.querySelectorAll('.card')];
q.addEventListener('input',()=>{
  const t=q.value.trim().toLowerCase();
  rows.forEach(r=>{r.classList.toggle('hidden', t && !r.textContent.toLowerCase().includes(t));});
  cards.forEach(c=>{
    if(!c.querySelector('tr.row, td.row')) return;
    const visible=[...c.querySelectorAll('tr.row, td.row')].some(r=>!r.classList.contains('hidden'));
    c.classList.toggle('hidden', t && !visible);
  });
});
const btn=document.getElementById('themeBtn');
btn.addEventListener('click',()=>{
  const cur=document.documentElement.getAttribute('data-theme')
    || (matchMedia('(prefers-color-scheme:dark)').matches?'dark':'light');
  document.documentElement.setAttribute('data-theme', cur==='dark'?'light':'dark');
});
const links=[...document.querySelectorAll('nav.toc a')];
const map=new Map(links.map(a=>[a.getAttribute('href').slice(1),a]));
const io=new IntersectionObserver((es)=>{
  es.forEach(e=>{if(e.isIntersecting){links.forEach(l=>l.classList.remove('active'));
    map.get(e.target.id)?.classList.add('active');}});
},{rootMargin:'-20% 0px -70% 0px'});
document.querySelectorAll('section.card').forEach(s=>io.observe(s));
"""


@lru_cache(maxsize=1)
def render_result_map() -> str:
    """결과 조합 지도 전체 HTML 문서를 반환한다 (프로세스당 1회 생성 후 캐시)."""
    sections = _build_sections()
    nav_items = "".join(
        f'<a href="#{sid}">{esc(title)}<span class="nav-count">{esc(count)}</span></a>'
        for sid, _kicker, title, _inputs, count, _body in sections
    )
    sections_html = "".join(section(*s) for s in sections)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<title>Pakit 결과 조합 지도</title>
<style>{_CSS}</style>
</head>
<body>
<div class="topbar">
  <div><h1>Pakit 결과 조합 지도</h1></div>
  <div class="sub">각 결과 칸 → 입력 질문·축 → 가능한 모든 값</div>
  <div class="filter">
    <input id="flt" type="search" placeholder="문구·코드 검색…" aria-label="문구 검색">
    <button id="themeBtn" class="theme-btn" type="button">◐ 테마</button>
  </div>
</div>
<div class="layout">
  <nav class="toc">{nav_items}</nav>
  <main>{sections_html}</main>
</div>
<footer>content: {esc(rc.RESULT_CONTENT_VERSION)} · compat: {esc(cs.COMPATIBILITY_PROFILE_VERSION)}
 · 실제 제출 경로(classify_submission) 기준 · 소스에서 자동 생성</footer>
<script>{_JS}</script>
</body>
</html>"""
