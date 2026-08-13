# 결과 페이지 데이터 정의서

## 목적

피그마 결과 화면을 구현하기 위해 서버가 제공해야 하는 최소 데이터를 정리한다.

- 대상 API: `POST /api/tests/submissions`
- 현재 상태: 확정된 규칙 기반 항목과 미확정 목업 항목을 함께 반환
- 제외: 친구 궁합과 호환성

## 결과를 만드는 입력

| 입력 | 사용처 |
|---|---|
| MBTI 결과 | 장난감 캐릭터와 명사 선택 |
| 성향 축 4개 점수 | 형용사, 성향 게이지, 포장 상자, 개봉 도구 선택 |
| 테스트 답변 | 특징, 사용 방법, 주의사항, 충전 방법 문구 조합 |

핵심 특징은 `동원력`, `관계 속의 나`, `마음 정리법`, `타고난 무기` 네 슬롯으로 구성한다.
입력은 슬롯별로 다음과 같이 결정한다.

- 동원력: `step1.q11 + MBTI 보조`
- 관계 속의 나: `step1.q01 × step1.q02`
- 마음 정리법: 분류된 `표현방식 × 에겐테토` 두 축
- 타고난 무기: 제출된 MBTI 네 글자 전체로 결정하는 16종별 대표 특징

마음 정리법은 표현 시점과 감정을 풀어내는 결만 사용한다. 관계의 거리를 뜻하는 애착유형과
새로움 선호를 뜻하는 자극추구 축은 이 슬롯에 사용하지 않는다.
타고난 무기는 MBTI를 일부 글자나 유형군으로 묶지 않으며, 16개 유형마다 서로 다른 결과를
반환한다.

동원력과 관계 속의 나는 확정된 조합 카피를 반환한다. 마음 정리법과 타고난 무기는 조합별
카피가 확정될 때까지 현재 API 값을 임시값으로 취급한다. 사용 방법, 주의사항, 충전 방법도
문구 조합 규칙이 확정될 때까지 목업값을 사용한다.

## 결과 페이지에 필요한 데이터

| 영역 | 필드 | 화면에서 사용하는 값 |
|---|---|---|
| 결과 조회 | `result_code` | 개인 결과를 다시 조회하는 고유 코드 |
| 장난감 소개 | `overview` | 희귀도, 형용사, 명사, 최종 결과명, 캐릭터 ID, 태그 |
| 언박싱 키트 | `unboxing_kit` | 성향 축 4개 점수, 요약, 포장 상자, 개봉 도구 |
| 핵심 특징 | `features` | 4개의 제목과 한 줄 설명 |
| 사용 방법 | `can_do` | 사용자가 좋아하는 행동 4개 |
| 주의사항 | `warnings` | 사용자에게 피해야 할 행동 4개 |
| 충전 방법 | `charging` | 충전 점수, 설명, 충전 활동 3개 |

### `overview` 장난감 소개

| 필드 | 타입 | 설명 |
|---|---|---|
| `rarity` | string | 현재 고정 문구 `상위 4%` |
| `adjective` | string | 성향 축 판정으로 결정되는 형용사. 예: `새벽 2시에도 카톡 폭격하는` |
| `noun` | string | MBTI에 따라 결정되는 명사. 예: `팽이` |
| `result_name` | string | 형용사와 명사를 합친 최종 결과명. 예: `새벽 2시에도 카톡 폭격하는 팽이` |
| `character_id` | string | 프론트엔드가 캐릭터 이미지를 찾을 때 사용하는 고정 영문 ID |
| `image_url` | string | 서버가 제공하는 캐릭터 이미지 경로 |
| `tags` | string[] | 말풍선 태그 3개 |

결과명은 PRD의 확정 규칙대로 `형용사 + 명사`로 만든다.

### `unboxing_kit` 언박싱 키트

| 필드 | 타입 | 설명 |
|---|---|---|
| `axis_scores.attachment` | integer | 거리조절 `0` ↔ 밀착 `100` |
| `axis_scores.expression` | integer | 탐색 `0` ↔ 직진 `100` |
| `axis_scores.routine` | integer | 탐험 `0` ↔ 루틴 `100` |
| `axis_scores.egen` | integer | 테토 `0` ↔ 에겐 `100` |
| `title` | string | 유형 요약 제목 |
| `description` | string | 유형 설명 |
| `packaging` | object | 포장 상자 정보 |
| `opening_tool` | object | 개봉 도구 정보 |

축 이름과 좌우 라벨은 고정 UI 문구이므로 프론트엔드가 관리한다. 네 점수는 축별 세 문항의
신호를 동일 가중치로 평균하고 가장 가까운 정수로 반올림한 값이다.

포장 상자와 개봉 도구는 같은 형태를 사용한다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `type` | string | 아래 목록에서 선택하는 고정 영문 ID |
| `name` | string | 결과 페이지에 표시할 한글 이름 |
| `tags` | string[] | 관련 성향 태그 2개 |
| `reason` | string | 해당 상자 또는 도구가 나온 이유 |

포장 상자 `type`은 다음 4개만 사용한다.

| `type` | `name` |
|---|---|
| `fragile_box` | 취급주의 상자 |
| `minimal_box` | 미니멀 상자 |
| `matryoshka_box` | 마트료시카 상자 |
| `locked_box` | 자물쇠 상자 |

개봉 도구 `type`은 다음 4개만 사용한다.

| `type` | `name` |
|---|---|
| `glove` | 손/장갑 |
| `utility_knife` | 커터칼 |
| `magic_wand` | 마술봉 |
| `chainsaw` | 전기톱 |

### `features` 핵심 특징

`features`는 항상 아래 순서로 4개를 반환한다.

1. 동원력: 나를 움직이게 만드는 것
2. 관계 속의 나: 사람들 사이에서 자연스럽게 맡는 역할
3. 마음 정리법: 생각과 감정을 내 안에서 정리하는 방식
4. 타고난 무기: MBTI 16종 각각의 대표 특징

세부 기획은 [`key-feature-product-plan.md`](./key-feature-product-plan.md)를 따른다.

| 필드 | 타입 | 설명 |
|---|---|---|
| `features[].title` | string | 특징 제목 |
| `features[].description` | string | 특징 보조 설명 |

### `can_do`와 `warnings`

각각 화면에 표시할 문자열을 4개씩 반환한다.

### `charging` 충전 방법

| 필드 | 타입 | 설명 |
|---|---|---|
| `score` | integer | 충전 점수. 현재 목업값 `90` |
| `description` | string | 충전 방법 설명 |
| `activities[].type` | string | 충전 활동의 안정적인 영문 ID |
| `activities[].label` | string | 화면 표시 문구 |

`activities`는 항상 3개를 반환한다.

## 최소 응답 예시

아래 값은 화면 연동용 목업이며 최종 결과 규칙이 아니다.

```json
{
  "result_code": "demo-result-code",
  "overview": {
    "rarity": "상위 4%",
    "adjective": "새벽 2시에도 카톡 폭격하는",
    "noun": "팽이",
    "result_name": "새벽 2시에도 카톡 폭격하는 팽이",
    "character_id": "spinning_top",
    "tags": ["도파민 MAX", "장난꾸러기", "혼자서도 잘 놀아요"]
  },
  "unboxing_kit": {
    "axis_scores": {
      "attachment": 20,
      "expression": 65,
      "routine": 20,
      "egen": 75
    },
    "title": "밤이 깊어질수록 텐션이 올라가는 장난꾸러기",
    "description": "해가 지면 비로소 에너지가 충전되는 타입이에요.",
    "packaging": {
      "type": "fragile_box",
      "name": "취급주의 상자",
      "tags": ["직진형", "거리조절형"],
      "reason": "마음을 크게 담아 쉽게 드러내는 성향을 표현한 상자예요."
    },
    "opening_tool": {
      "type": "magic_wand",
      "name": "마술봉",
      "tags": ["탐험형", "에겐형"],
      "reason": "새로운 경험을 흥미롭게 바꾸는 모습을 닮았어요."
    }
  },
  "features": [
    {
      "title": "분위기를 띄워요",
      "description": "생각보다 빠른 행동력"
    },
    {
      "title": "일단 해봐요",
      "description": "생각보다 빠른 행동력"
    },
    {
      "title": "변화를 즐겨요",
      "description": "새로운 방식에 열린 태도"
    },
    {
      "title": "탐험형",
      "description": "직접 부딪히며 발견"
    }
  ],
  "can_do": [
    "같이 놀아주세요",
    "새로운 제안을 던져주세요",
    "리액션을 아끼지 말아주세요",
    "자유롭게 맡겨주세요"
  ],
  "warnings": [
    "똑같은 일만 반복시켜요",
    "선택을 지나치게 제한해요",
    "재미없는 분위기를 오래 끌어요",
    "아이디어를 시작부터 막아버려요"
  ],
  "charging": {
    "score": 90,
    "description": "친구들과 놀 때 가장 빠르게 충전돼요",
    "activities": [
      {"type": "hangout", "label": "친구들과 놀기"},
      {"type": "beer", "label": "맥주 한 잔"},
      {"type": "travel", "label": "여행가기"}
    ]
  }
}
```

## 프론트엔드가 관리하는 값

다음 고정 UI 문구는 API에 포함하지 않는다.

- `UNBOXING KIT`, `KEY FEATURES`, `WHAT IT CAN DO`, `WARNING`, `CHARGING`
- 성향 축 이름과 좌우 라벨
- 섹션 설명과 버튼 문구
- 레이아웃, 색상, 게이지 표현
- `type`에 대응하는 상자와 개봉 도구 이미지
- 핵심 특징 4개의 아이콘
- `activities[].type`에 대응하는 충전 활동 아이콘

## 나중에 확정할 항목

- 성향 축 4개 점수 계산 규칙
- 충전 점수 계산 규칙
- 결과 문구 조합표
- 취급주의 상자 성향 조합의 피그마·PRD 차이
- 친구 궁합과 호환성
