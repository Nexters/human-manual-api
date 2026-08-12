---
name: pakit-product-change
description: Implement Pakit product behavior from the PRD without inventing unresolved requirements. Use for assessment questions, scoring, MBTI or axis classification, result copy, character mapping, sharing, compatibility, result persistence, or API changes that alter user-visible product behavior. Do not use for infrastructure-only work, generic refactors, or isolated bug fixes that do not change product rules.
---

# Pakit product change

Follow this workflow for every product-facing backend change.

## 1. Establish the requirement

1. Read the relevant section in `PRD_나사용설명서.html` and its surrounding section.
2. Read `docs/architecture.md`, especially unresolved decisions.
3. Classify each requirement as:
   - confirmed by the PRD;
   - provisional or explicitly unresolved;
   - an engineering choice that preserves product behavior.
4. Do not convert provisional copy, questions, assets, thresholds, retention periods, or
   compatibility rules into permanent behavior. If a missing decision materially changes the
   result, stop and ask for it. Otherwise use a conspicuous placeholder and report it.

## 2. Trace the behavior

Before editing, identify the affected path from HTTP schema through domain/service logic to stored
or returned output. Preserve these invariants:

- Keep result generation deterministic; do not add an AI API unless the PRD changes explicitly.
- Keep internal MBTI/axis classifications separate from user-visible wording.
- Version questions, scoring rules, and content when they become persistent.
- Store a result snapshot for shareable results so later copy changes do not rewrite history.
- Avoid logging names, free-text answers, tokens, or complete assessment payloads.
- Preserve `/api/v1` compatibility or explicitly identify a breaking change.

## 3. Implement and prove

1. Keep route handlers thin and place branching product logic in domain or service modules.
2. Validate external input with Pydantic and make score direction explicit in field descriptions.
3. Add tests for the happy path, invalid input, boundary values, and every affected matrix quadrant.
4. Update `docs/architecture.md` when the user supplies a new product decision. Do not edit the PRD
   itself unless the user asks.
5. Run:

   ```bash
   uv run ruff check .
   uv run ruff format --check .
   uv run mypy
   uv run pytest --cov --cov-report=term-missing
   ```

6. Report changed behavior, verification results, assumptions, and remaining product decisions.

