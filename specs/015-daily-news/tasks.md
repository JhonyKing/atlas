# Tasks: Previous-Day Evidence News

**Input**: [spec.md](spec.md), [plan.md](plan.md)

## Phase 1: Source and model

- [X] T001 [P] Create the versioned feed allowlist in `corpus/manifests/news-v1.yaml` (pending operator review).
- [X] T002 [P] Add candidate/selection schemas and migration in `apps/backend/src/atlas/news/` (`database/migrations/versions/0010_daily_news.py`).
- [X] T003 Add fixture-feed tests for dates, malformed items, limits and attribution.

## Phase 2: Selection (P1)

- [X] T004 Implement safe feed fetch with timeout, size, redirect, robots/licensing and SSRF checks.
- [X] T005 Implement UTC previous-day filtering and deterministic documented ranking.
- [X] T006 Implement `unavailable` selection when evidence is insufficient and return the reason code.
- [X] T007 Add scheduled refresh and idempotent daily selection without blocking cited answers.
- [X] T008 Add `GET /v1/news/daily` OpenAPI contract and safe unavailable response.

## Phase 3: Bilingual presentation (P2)

- [X] T009 Add localized `DailyNews` card at `/en` and `/es` with original-language labels.
- [X] T010 Add API/UI tests for locale parity, attribution, dates, links and unavailable state.
- [X] T011 Add retention, correction/takedown and copyright documentation.
- [X] T012 Run analyze/converge and capture evidence of one real execution. (Evidence:
  `evals/results/daily-news-real-execution.json` records four successful RSS fetches, 60 candidates,
  UTC previous-day filtering and a technology-relevant selected story. Permanent activation remains
  review-gated.)

## Requirement coverage

| Requirement | Tasks |
|---|---|
| FR-NEWS-001 | T005, T008, T009, T010 |
| FR-NEWS-002 | T001, T002, T003, T004, T011 |
| FR-NEWS-003 | T005, T006, T010 |
| FR-NEWS-004 | T003, T004, T010 |
| FR-NEWS-005 | T006, T008, T010 |
| FR-NEWS-006 | T008, T009, T010 |
| FR-NEWS-007 | T004, T010 |
| FR-NEWS-008 | T007, T012 |
| SC-NEWS-001 | T003, T008, T010 |
| SC-NEWS-002 | T005, T010 |
| SC-NEWS-003 | T006, T008, T009, T010 |
| SC-NEWS-004 | T005, T010, T012 |
