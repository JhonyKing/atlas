# Tasks: Previous-Day Evidence News

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Source and model

- [ ] T001 [P] Create the versioned feed allowlist in `corpus/manifests/news-v1.yaml`.
- [ ] T002 [P] Add candidate/selection schemas and migration in `apps/backend/src/atlas/news/`.
- [ ] T003 Add fixture-feed tests for dates, deduplication, malformed items, limits and attribution.

## Phase 2: Selection (P1)

- [ ] T004 Implement safe feed fetch with timeout, size, redirect, robots/licensing and SSRF checks.
- [ ] T005 Implement UTC previous-day filtering and deterministic documented ranking.
- [ ] T006 Implement `unavailable` selection when evidence is insufficient and persist the reason code.
- [ ] T007 Add scheduled refresh and idempotent daily selection without blocking cited answers.
- [ ] T008 Add `GET /v1/news/daily` OpenAPI contract, request correlation and safe telemetry.

## Phase 3: Bilingual presentation (P2)

- [ ] T009 Add localized `DailyNews` card at `/en` and `/es` with original-language labels.
- [ ] T010 Add API/UI tests for locale parity, attribution, dates, links and unavailable state.
- [ ] T011 Add retention, correction/takedown and copyright documentation.
- [ ] T012 Run analyze/converge and capture evidence of one real execution.

