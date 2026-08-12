# Pakit Backend Agent Guide

## Mission

Build the FastAPI backend for “나 사용 설명서.” Treat `PRD_나사용설명서.html` as the
product source of truth. `docs/architecture.md` records engineering decisions and explicitly
unresolved product questions.

## Source hierarchy

Apply sources in this order and report material conflicts instead of guessing:

1. The user's current request
2. Confirmed requirements in `PRD_나사용설명서.html`
3. Decisions in `docs/architecture.md`
4. Existing API contracts and tests

Use the repo skill `$pakit-product-change` for changes to assessment, scoring, classification,
result content, sharing, compatibility, or persistence behavior.

## Working agreements

- Use Python 3.12 and `uv`; do not add pip/Poetry requirement files.
- Keep the modular-monolith boundaries: HTTP in `api`, framework-free concepts in `domain`,
  use cases in `services`, and runtime concerns in `core`.
- Keep business rules deterministic. The current product explicitly does not use AI to generate
  result copy.
- Do not silently invent unresolved questions, final adjectives, character assets, compatibility
  rules, or retention policy. Mark placeholders and update `docs/architecture.md` when a product
  decision is supplied.
- Preserve API compatibility under `/api/v1`. If a breaking change is necessary, call it out.
- Never read or modify `.env` unless the user explicitly asks. Use `.env.example` for configuration
  shape and safe defaults.
- Never commit secrets or real user response data.
- Do not pin a Codex model or personal connector in repository configuration.

## Required workflow

1. Read the relevant PRD section and nearby tests before editing domain behavior.
2. Make the smallest coherent change and add or update tests in the same change.
3. Update `.env.example`, README, and architecture notes when their public contract changes.
4. Run `uv run ruff check .`, `uv run ruff format --check .`, `uv run mypy`, and
   `uv run pytest --cov --cov-report=term-missing` before handing off.
5. Report any skipped check and the exact reason.

## Review checklist

- Validate all external input with Pydantic models.
- Keep route handlers thin; put branching product logic in services/domain code.
- Test boundary values, especially the 50-point axis split and invalid scores.
- Avoid logging names, free-text answers, tokens, or full assessment payloads.
- For persistence changes, include a reversible Alembic migration and preserve historical result
  snapshots.
- Update README/API examples when developer-facing behavior changes.
