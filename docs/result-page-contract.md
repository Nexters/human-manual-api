# 결과 페이지 API 계약 제안

## 1. 문서 상태

- 상태: **구조 제안** — 아직 API에 구현하지 않음
- 기준 화면: 사용자가 2026-08-12에 전달한 결과 페이지 와이어프레임 4장
- 대상 API: `POST /api/tests/submissions` 성공 응답
- 이번 범위: 결과 소개, 성향 프로필, 언박싱 키트, 핵심 기능, 사용 방법, 주의사항, 충전 방법
- 제외 범위: 친구 궁합과 호환성 상세 화면

2026-08-12에 추가로 확정된 개발 단계 정책은 다음과 같다.

- 희귀도 배지는 실제 통계가 아니라 고정 문구 `상위 4%`를 사용한다.
- 성향 축 4개 점수는 점수표 확정 전까지 목업값을 사용한다.
- 충전 점수는 계산 규칙 확정 전까지 목업값 `90`을 사용한다.
- 배경·상자·개봉 도구·아이콘의 실제 에셋 키는 추후 전달받아 반영한다.

이 문서는 화면에 필요한 데이터를 빠짐없이 정의하기 위한 구현 전 계약이다. 예시 문구와 숫자는
와이어프레임을 설명하기 위한 목업이며, 아래에서 **미확정**으로 표시한 값은 제품 규칙으로
사용하지 않는다.

## 2. 데이터 소유권

| 구분 | 소유 | 설명 |
|---|---|---|
| 섹션 제목과 고정 안내 문구 | 프론트엔드 | `UNBOXING KIT`, `KEY FEATURES`, `CHARGING` 등 |
| 레이아웃, 색상, 게이지 표현 | 프론트엔드 | 서버는 계산값과 안정적인 코드만 반환 |
| 이미지 파일과 URL | 프론트엔드 | 서버가 반환한 `asset_key`를 실제 에셋으로 변환 |
| MBTI 캐릭터 코드와 명사 | 백엔드 | MBTI 판정으로 16종 중 하나를 결정 |
| 성향 축 점수와 분류 | 백엔드 | 문항별 점수표가 확정된 뒤 계산 |
| 포장 상자와 개봉 도구 코드 | 백엔드 | 성향 축 조합으로 결정 |
| 사용자별 결과 문구 | 백엔드 | AI 없이 버전이 있는 룰과 콘텐츠로 조합 |
| 희귀도 배지 | 백엔드 | 현재 고정 문구 `상위 4%` 반환 |
| 충전 점수 | 백엔드 예정 | 현재 `90` 목업값, 계산 규칙은 미확정 |

## 3. 화면과 응답 필드 대응

### 3.1 상단 장난감 소개

| 화면 요소 | 응답 필드 | 상태 |
|---|---|---|
| `상위 4%` | `hero.rarity_label` | 확정: 현재 고정 문구 사용 |
| `새벽 2시에도 카톡 폭격하는` | `hero.descriptor` | 후보 카피, 최종 16종 미확정 |
| `팽이 지은` | `hero.display_title` | 조합 규칙 미확정 |
| 팽이 이미지 | `hero.character.asset_key` | 캐릭터 16종 매핑 확정 |
| 결과 배경 이미지 | `hero.background_asset_key` | 실제 키 전달 전까지 `null` |
| 말풍선 3개 | `hero.tags[]` | 콘텐츠 규칙 미확정 |

화면 제목 `장난감 소개서`와 스크롤 안내는 프론트엔드 고정 문구이므로 응답에 포함하지 않는다.

### 3.2 성향 프로필과 언박싱 키트

| 화면 요소 | 응답 필드 | 상태 |
|---|---|---|
| 성향 게이지 4개 | `profile.axes[]` | 축 코드 확정, 현재 점수는 목업 |
| 유형 요약 제목 | `profile.headline` | 콘텐츠 규칙 미확정 |
| 유형 요약 본문 | `profile.description` | 콘텐츠 규칙 미확정 |
| 포장 상자 | `unboxing_kit.packaging` | A1~A4 구조 확정, 화면과 PRD 조합 충돌 있음 |
| 개봉 도구 | `unboxing_kit.opening_tool` | B1~B4 구조 확정 |

`axes[]`의 `score`는 백엔드의 표준 방향을 기준으로 `0..100` 값을 반환한다. 프론트엔드는
`left_label`, `right_label`과 함께 렌더링하고 임의로 점수 방향을 뒤집지 않는다.

### 3.3 핵심 기능, 사용 방법, 주의사항

- `key_features[]`: 아이콘, 제목, 짧은 설명이 있는 카드 목록
- `can_do[]`: 사용자가 좋아하는 대우와 행동 목록
- `warnings[]`: 사용자에게 피해야 할 행동 목록

핵심 기능은 두 줄의 의미가 다르므로 단일 문자열이 아니라 `title`과 `description`으로 분리한다.
아이콘은 서버가 `icon_code`만 반환하고 실제 이미지 또는 이모지는 프론트엔드가 결정한다.
예시의 아이콘 코드는 실제 에셋 키를 전달받기 전까지 사용하는 제안값이다.

### 3.4 충전 방법

| 화면 요소 | 응답 필드 | 상태 |
|---|---|---|
| 충전 점수 `90` | `charging.score` | 현재 목업값 `90`, 계산 규칙 미확정 |
| 충전 설명 | `charging.description` | 콘텐츠 규칙 미확정 |
| 충전 활동 3개 | `charging.activities[]` | 활동 코드와 선택 규칙 미확정 |

친구 궁합 영역은 이번 응답 계약에서 제외한다. 추후 별도 제품 결정 후 추가한다.

## 4. 제안 성공 응답

아래 예시는 필드의 형태를 보여주기 위한 목업이다. `provisional_fields`에 포함된 값은 최종
제품 규칙이 아니다.

```json
{
  "result_id": null,
  "persisted": false,
  "mode": "mock",
  "assessment_version": "2026-08-12.1",
  "content_version": "mock-v2",
  "hero": {
    "rarity_label": "상위 4%",
    "descriptor": "새벽 2시에도 카톡 폭격하는",
    "display_title": "팽이 지은",
    "character": {
      "code": "spinning_top",
      "noun": "팽이",
      "asset_key": "image_top_340"
    },
    "background_asset_key": null,
    "tags": ["도파민 MAX", "장난꾸러기", "혼자서도 잘 놀아요"]
  },
  "profile": {
    "axes": [
      {
        "code": "expression",
        "score": 67,
        "left_label": "탐색",
        "right_label": "직진"
      },
      {
        "code": "attachment",
        "score": 100,
        "left_label": "밀착",
        "right_label": "거리조절"
      },
      {
        "code": "manner",
        "score": 75,
        "left_label": "에겐",
        "right_label": "테토"
      },
      {
        "code": "novelty",
        "score": 50,
        "left_label": "루틴",
        "right_label": "탐험"
      }
    ],
    "headline": "밤이 깊어질수록 텐션이 올라가는 장난꾸러기",
    "description": "해가 지면 비로소 에너지가 충전되는 타입이에요."
  },
  "unboxing_kit": {
    "packaging": {
      "code": "A1",
      "name": "취급주의 상자",
      "asset_key": null,
      "tags": ["직진형", "밀착형"],
      "reason_title": "왜 취급주의 상자인가요?",
      "reason": "할 말과 마음이 겉면에 드러나는 성향을 표현한 상자예요."
    },
    "opening_tool": {
      "code": "B3",
      "name": "마술봉",
      "asset_key": null,
      "tags": ["탐험형", "에겐형"],
      "reason_title": "왜 마술봉인가요?",
      "reason": "새로운 경험을 부드럽고 흥미롭게 시작하는 모습을 표현해요."
    }
  },
  "key_features": [
    {
      "icon_code": "fire",
      "title": "분위기를 띄워요",
      "description": "생각보다 빠른 행동력"
    },
    {
      "icon_code": "smile",
      "title": "일단 해봐요",
      "description": "생각보다 빠른 행동력"
    },
    {
      "icon_code": "sparkles",
      "title": "변화를 즐겨요",
      "description": "새로운 방식에 열린 태도"
    },
    {
      "icon_code": "magnifier",
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
      {"code": "hangout", "icon_code": "friends", "label": "친구들과 놀기"},
      {"code": "beer", "icon_code": "beer", "label": "맥주 한 잔"},
      {"code": "travel", "icon_code": "airplane", "label": "여행가기"}
    ]
  },
  "provisional_fields": [
    "hero.descriptor",
    "hero.display_title",
    "hero.background_asset_key",
    "hero.tags",
    "profile",
    "unboxing_kit",
    "key_features",
    "can_do",
    "warnings",
    "charging"
  ]
}
```

## 5. 타입 규격

### `profile.axes[]`

| 필드 | 타입 | 설명 |
|---|---|---|
| `code` | enum | `expression`, `attachment`, `manner`, `novelty` |
| `score` | integer | `0..100`; 왼쪽 극점 0, 오른쪽 극점 100 |
| `left_label` | string | 0점 방향의 화면 라벨 |
| `right_label` | string | 100점 방향의 화면 라벨 |

### `unboxing_kit.packaging`

| 필드 | 타입 | 설명 |
|---|---|---|
| `code` | enum | `A1`, `A2`, `A3`, `A4` |
| `name` | string | 상자 이름 |
| `asset_key` | string \| null | 프론트엔드 에셋 매핑 키. 실제 키 전달 전에는 null |
| `tags` | string[2] | 표현방식과 애착유형의 화면 라벨 |
| `reason_title` | string | 선정 이유 카드 제목 |
| `reason` | string | 선정 이유 본문 |

### `unboxing_kit.opening_tool`

| 필드 | 타입 | 설명 |
|---|---|---|
| `code` | enum | `B1`, `B2`, `B3`, `B4` |
| `name` | string | 개봉 도구 이름 |
| `asset_key` | string \| null | 프론트엔드 에셋 매핑 키. 실제 키 전달 전에는 null |
| `tags` | string[2] | 자극추구와 에겐테토의 화면 라벨 |
| `reason_title` | string | 선정 이유 카드 제목 |
| `reason` | string | 선정 이유 본문 |

### `key_features[]`

| 필드 | 타입 | 설명 |
|---|---|---|
| `icon_code` | string | 프론트엔드가 아이콘으로 변환할 코드. 현재 예시는 제안값 |
| `title` | string | 기능 제목 |
| `description` | string | 기능 보조 설명 |

### `charging.activities[]`

| 필드 | 타입 | 설명 |
|---|---|---|
| `code` | string | 충전 활동의 안정적인 ID |
| `icon_code` | string | 프론트엔드 아이콘 매핑 코드. 현재 예시는 제안값 |
| `label` | string | 화면 표시 문구 |

## 6. 기존 응답에서의 변경

현재 목업 응답은 `product`, `unboxing`, `manual` 중심이다. 결과 화면 계약을 구현할 때 다음과
같이 변경할 예정이다.

| 현재 필드 | 제안 필드 | 처리 |
|---|---|---|
| `product.*` | `hero.*` | 캐릭터와 상단 결과 정보를 확장 |
| `unboxing.*` | `unboxing_kit.*` | 코드뿐 아니라 표시 콘텐츠와 에셋 키 제공 |
| `manual.core_features` | `key_features[]` | 문자열을 제목·설명·아이콘 객체로 변경 |
| `manual.precautions` | `warnings[]` | 화면 용어에 맞춰 이동 |
| `manual.charging` | `charging` | 점수·설명·활동 객체로 확장 |
| `manual.bugs` | `can_do[]` | 동일 의미가 아니므로 기존 필드를 재사용하지 않고 새로 정의 |
| `manual.compatibility` | 제외 | 친구 궁합 결정 시 별도 계약으로 다룸 |
| `manual.rarity` | `hero.rarity_label` | 상단 고정 문구 `상위 4%`로 이동 |

이는 현재 `/api` 성공 응답의 구조를 바꾸는 변경이다. 구현 전에 프론트엔드와 전환 시점을
합의하거나, 기존 필드를 한시적으로 함께 제공하는 호환 기간을 둬야 한다.

## 7. 확인된 충돌과 미결정 사항

### 7.1 와이어프레임과 PRD의 축 방향

- PRD와 현재 도메인: `manner`는 `에겐 0 ↔ 테토 100`
- 와이어프레임 표시: `테토 ↔ 에겐`
- PRD와 현재 도메인: `novelty`는 `루틴 0 ↔ 탐험 100`
- 와이어프레임 표시: `탐험 ↔ 루틴`

백엔드 표준 방향은 현재 PRD와 도메인 정의를 유지한다. 와이어프레임 라벨 순서를 바꿀지,
두 축만 프론트엔드에서 역방향으로 표시할지는 제품 결정이 필요하다.

### 7.2 취급주의 상자 조합

- PRD: `A1 취급주의 상자 = 직진 × 밀착`
- 와이어프레임: `취급주의 상자 = 직진형 × 거리조절형`

예시 응답은 PRD 기준으로 `A1`, `직진형`, `밀착형`을 사용했다. 와이어프레임을 최종 기준으로
바꾸려면 A1~A4 매핑을 함께 수정해야 한다.

### 7.3 계산 규칙과 콘텐츠

다음 항목은 구현 전에 별도 결정 또는 콘텐츠 원본이 필요하다.

1. 22개 선택지에서 성향 축 4개 점수를 계산하는 가중치
2. `step2.q04` 슬라이더와 `step2.q06` 숫자 입력의 허용 범위 및 점수 변환
3. 충전 점수의 계산 방식
4. 형용사 16종의 최종 카피
5. 결과 설명, 태그, 기능, 사용 방법, 주의사항, 충전 활동의 콘텐츠 조합표
6. 배경, 포장 상자, 개봉 도구, 아이콘의 실제 에셋 키

## 8. 구현 순서

1. 축 방향과 A1 포장 조합 충돌 확정
2. 응답 스키마를 Pydantic 모델과 Swagger에 반영
3. 팽이 결과 하나를 `mock-v2` 고정 목업으로 제공하고 축 점수·충전 점수에 목업임을 표시
4. 프론트엔드가 결과 페이지 전체를 목업 데이터로 연결
5. 점수표와 콘텐츠 조합표 확정 후 결정적 룰로 교체
6. 결과 저장과 `result_id` 발급 추가
7. 호환성 계약 별도 설계
