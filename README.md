# Pakit Backend

AI가 아닌 룰 기반으로 만드는 **나 사용 설명서** 서비스의 FastAPI 백엔드입니다.
현재 제품 기준은 [`PRD_나사용설명서.html`](./PRD_%E1%84%82%E1%85%A1%E1%84%89%E1%85%A1%E1%84%8B%E1%85%AD%E1%86%BC%E1%84%89%E1%85%A5%E1%86%AF%E1%84%86%E1%85%A7%E1%86%BC%E1%84%89%E1%85%A5.html)입니다.

## 시작하기

Python 3.12와 [uv](https://docs.astral.sh/uv/getting-started/installation/)가 필요합니다.

```bash
cp .env.example .env
uv sync
uv run uvicorn pakit.main:app --reload
```

- API 문서: <http://localhost:8000/docs>
- 상태 확인: <http://localhost:8000/health>
- API 상태 확인: <http://localhost:8000/api/v1/health>

## 자주 쓰는 명령

```bash
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run mypy
```

자동 수정은 `uv run ruff check --fix .`와 `uv run ruff format .`을 사용합니다.

## 구조

```text
src/pakit/
├── api/          # HTTP 라우터와 요청/응답 계약
├── core/         # 환경 설정과 공통 기반 코드
├── domain/       # 프레임워크와 분리된 도메인 모델
└── services/     # 유스케이스와 룰 기반 결과 조립
```

현재 `POST /api/v1/assessments/evaluate`는 PRD의 16개 MBTI 캐릭터와 4개 성향 축을
조합하는 최소 수직 슬라이스입니다. MBTI별 캐릭터 명사는 최종 디자인 에셋과 동일하게
확정되었으며, 아직 미확정인 형용사 문구는 응답의 `provisional`로 명시합니다.

프론트엔드는 완료된 22개 답변과 MBTI 퍼센트를
`POST /api/v1/assessments/submissions`로 제출할 수 있습니다. 현재 응답은 MBTI별 최종
캐릭터를 사용하되, 채점 규칙과 결과 카피가 확정되기 전까지 `mode: "mock"`으로 반환합니다.

상세 결정 사항과 다음 구현 순서는 [`docs/architecture.md`](./docs/architecture.md)를 참고하세요.
22개 문항의 기계 판독 가능한 ID 목록은
[`docs/assessment-identifiers.v1.json`](./docs/assessment-identifiers.v1.json)에 있습니다.
실행 가능한 요청·응답 명세와 예시는 서버 실행 후 `/docs`의 Swagger에서 확인할 수 있습니다.

## Codex로 작업하기

저장소 루트에서 Codex를 시작하고 이 프로젝트를 신뢰 대상으로 설정하면 다음 구성이
자동으로 적용됩니다.

- `AGENTS.md`: 항상 적용되는 아키텍처, 보안, 검증 규칙
- `.codex/config.toml`: workspace-write, 요청 기반 승인, 제한된 네트워크와 비밀 환경변수 보호
- `.agents/skills/pakit-product-change`: PRD 기반 제품 기능 변경 전용 워크플로

제품 동작을 바꾸는 작업은 스킬을 명시해 요청할 수 있습니다.

```text
$pakit-product-change를 사용해서 검사 점수 계산 규칙을 구현해줘.
```

모델, 개인 GitHub 연결, 알림 같은 사용자별 설정은 저장소에 고정하지 않습니다.
