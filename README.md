# Pakit Backend

**나 사용 설명서** 서비스의 FastAPI 백엔드입니다.
현재 제품 기준은 [`PRD_나사용설명서.html`](./PRD_%E1%84%82%E1%85%A1%E1%84%89%E1%85%A1%E1%84%8B%E1%85%AD%E1%86%BC%E1%84%89%E1%85%A5%E1%86%AF%E1%84%86%E1%85%A7%E1%86%BC%E1%84%89%E1%85%A5.html)입니다.

## 시작하기

Python 3.12와 [uv](https://docs.astral.sh/uv/getting-started/installation/)가 필요합니다.

```bash
cp .env.example .env
uv sync
uv run uvicorn pakit.main:app --reload
```

- API 문서: <http://localhost:8000/docs>
- 수동 테스트 페이지: <http://localhost:8000/test/>
- 상태 확인: <http://localhost:8000/health>
- API 상태 확인: <http://localhost:8000/api/health>

브라우저 요청은 로컬 프론트엔드 `http://localhost:3000`, `http://localhost:5173`과 운영
프론트엔드 `https://pakit.kr`에서 허용됩니다. 이 목록은 서버 코드에 고정되어 있으며 `.env`로
재정의하지 않습니다.

## 로컬에서 실행하기

먼저 `.env.example`을 복사하고 `PAKIT_DATABASE_PASSWORD`와 `POSTGRES_PASSWORD`에 같은
로컬 DB 비밀번호를 설정합니다.

```bash
cp .env.example .env
```

로컬에서는 PostgreSQL만 Docker로 실행합니다. `compose.local.yaml`은 DB 포트를 로컬
루프백 주소에만 열며 배포에는 사용하지 않습니다.

```bash
docker compose -f compose.yaml -f compose.local.yaml up -d db
uv run alembic upgrade head
uv run uvicorn pakit.main:app --reload
```

개발을 마치면 DB 컨테이너만 중지할 수 있습니다. `postgres_data` 볼륨은 그대로 유지됩니다.

```bash
docker compose -f compose.yaml -f compose.local.yaml stop db
```

## Docker Compose로 배포하기

배포 서버에서는 기존 `compose.yaml`로 API, PostgreSQL, 프론트엔드를 함께 실행합니다. 이때
백엔드 저장소의 상위 경로에 `frontend-app`이 있어야 합니다.

```bash
docker compose up --build -d
```

운영 PostgreSQL은 외부 포트를 열지 않고 Docker 내부 네트워크에서만 접근합니다. 데이터는
`postgres_data` 볼륨에 저장되므로 일반적인 컨테이너 재시작과 재배포 후에도 유지됩니다. API
컨테이너는 시작 전에 `alembic upgrade head`를 자동 실행합니다. `docker compose down -v`는
데이터 볼륨까지 삭제하므로 운영 서버에서 실행하지 않습니다.

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

프론트엔드는 완료된 24개 답변과 선택한 MBTI 유형을
`POST /api/tests/submissions`로 제출할 수 있습니다. 응답은 결과 페이지의 7개 영역으로
구성되며, 응답의 `result_code`를 사용해 `GET /api/results/{result_code}`로 다시 조회할 수
있습니다. 성향 점수·형용사·MBTI별 캐릭터 명사·언박싱 아이템과 언박싱 소개 문구는 룰로
결정합니다. 핵심 특징 아래의 장난감 이야기도 MBTI별 16종 고정 카피로 반환하며, `이렇게
다뤄주세요`와 `이렇게 하면 고장나요`의 네 문구도 테스트 답변·성향 점수·MBTI를 조합해
반환합니다. 충전 설명과 활동은 휴일·약속 취소 답변의 조합으로 결정하며, 충전 점수는 현재
목업값입니다. 제출 결과는 URL-safe 8자리 `result_code`와 함께
PostgreSQL에 닉네임을 포함한 결과 스냅샷으로 저장되며, 이후 카피가 바뀌어도 생성 당시 결과
그대로 조회됩니다. 원본 답변은 보존 정책이 확정되지 않아 현재 저장하지 않습니다.

친구 궁합은
`GET /api/compatibility?mine=demo-result-code&friend=demo-friend-code`로 확인할 수 있습니다.
현재 궁합 점수와 문구는 프론트엔드 연동용 고정 목업값입니다.

상세 결정 사항과 다음 구현 순서는 [`docs/architecture.md`](./docs/architecture.md)를 참고하세요.
24개 문항의 기계 판독 가능한 ID 목록은
[`docs/assessment-identifiers.v1.json`](./docs/assessment-identifiers.v1.json)에 있습니다.
실행 가능한 요청·응답 명세와 예시는 서버 실행 후 `/docs`의 Swagger에서 확인할 수 있습니다.
결과 페이지 와이어프레임 기반의 응답 계약은
[`docs/result-page-contract.md`](./docs/result-page-contract.md)에 있습니다.

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
