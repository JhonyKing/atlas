# Tasks: Retrieval Quality and Multilingual Evidence

**Input**: Design documents from `specs/007-retrieval-quality-multilingual/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`

## Phase 1: Contracts and fixtures

- [X] T001 Create retrieval quality unit, integration and security test directories.
- [X] T002 Add deterministic bilingual, alias, version, contradiction and freshness fixtures.
- [X] T003 Add bounded retrieval quality settings and `scripts/verify-retrieval.ps1`/`pnpm test:retrieval`.
- [X] T004 Add query rewrite/filter contract tests for aliases, versions, provider/framework/date/language/source type.
- [X] T005 Add ranking/context tests for deduplication, diversity, parent-child windows and evidence budget.
- [X] T006 Add baseline/reranker comparison and metric tests.
- [X] T007 Add security tests proving rewrite cannot create destinations or bypass bounded input policy.

## Phase 2: Query preparation and ranking (P1)

- [X] T008 Implement typed query rewrites and filter contracts in `apps/backend/src/atlas/retrieval/query.py`.
- [X] T009 Integrate bounded rewrites and filters into `RetrievalService` without changing `Question`/`Evidence` contracts.
- [X] T010 Implement deterministic deduplication, MMR-style diversity and authority/freshness ranking in `ranking.py`.
- [X] T011 Implement parent-child context windows and hard evidence budget in `context.py`.
- [X] T012 Add multilingual language-preserving metadata and fallback behavior for unavailable embedding profiles.

## Phase 3: Measured reranking and metrics (P2)

- [X] T013 Implement typed reranker adapter and paired baseline/candidate enablement decision in `reranking.py`.
- [X] T014 Implement Hit@5, MRR, context precision/recall, citation precision, freshness, latency and cost metrics in `metrics.py`.
- [X] T015 Add temporal, cross-language, contradiction and source-version regression cases.
- [X] T016 Add benchmark tests proving no reranker enablement on quality/latency/cost regression.

## Phase 4: Verification and documentation

- [X] T017 Run targeted/full backend tests, lint, mypy and retrieval evals; record `docs/verification/007-retrieval-quality-multilingual.md`.
- [X] T018 Add `evals/cases/007-retrieval-quality-multilingual.jsonl` and metric summary output.
- [X] T019 Update README with retrieval quality commands and baseline/reranker policy.
- [X] T020 Create `docs/architecture/007-retrieval-quality-multilingual.md` and `docs/adr/0006-measured-retrieval-quality.md`.
- [ ] T021 Update PRD backlog/status matrix and run SpecKit Analyze/Converge before closure.

## Requirements Traceability

| Requirement | Implementation | Verification |
|---|---|---|
| FR-RET-001–002 | T004, T008–T009 | T004, T007, T017 |
| FR-RET-003, FR-RET-006 | T005, T010–T011 | T005, T015, T017 |
| FR-RET-004, FR-RET-007 | T006, T013–T014 | T006, T016–T018 |
| FR-RET-005, FR-RET-008 | T002, T012, T015 | T002, T007, T015, T017 |
| SC-RET-001–007 | T008–T021 | T004–T018 |
