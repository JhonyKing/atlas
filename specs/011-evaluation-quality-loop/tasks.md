# Tasks: Evaluation, Observability, and Quality Loop

## Phase 1: Dataset and evaluator contracts

- [X] T001 Create evaluation unit, integration and offline-gate directories.
- [X] T002 Add manifest and golden dataset category-count fixtures.
- [X] T003 Add `scripts/verify-evals.ps1` and `pnpm test:evals`.
- [X] T004 Add deterministic schema/link/length/duplicate/report evaluators and tests.
- [X] T005 Add retrieval/freshness/citation evaluator coverage and tests.

## Phase 2: Quality review and online signals

- [X] T006 Add typed generation quality judge contract with bias/version metadata.
- [X] T007 Add PII-minimized feedback/difficult-case queue contract and tests.
- [X] T008 Add online format/security/anomaly/latency/cost signal evaluators.
- [X] T009 Add safe trace-tag contract for node/tool/model/prompt/retrieval/index/corpus/locale.

## Phase 3: Regression and release gates

- [X] T010 Add regression sample command for prompt/retrieval/model/chunking changes.
- [X] T011 Implement fail-closed promotion gate for citation/hallucination/schema/cost/latency.
- [X] T012 Add private aggregate dashboard/public methodology artifact.

## Phase 4: Closure

- [X] T013 Run deterministic/offline/full backend/frontend tests and record evidence.
- [X] T014 Update README, architecture, ADR, PRD/status matrix and evaluation docs.
- [X] T015 Run SpecKit Analyze/Converge and close only with zero mandatory tasks.

## Requirements Traceability

| Requirement | Tasks | Verification |
|---|---|---|
| FR-EVA-001..003 | T002..T005 | dataset/evaluator suites |
| FR-EVA-004..006 | T006..T009 | judge/queue/online signal tests |
| FR-EVA-007..008 | T010..T011 | regression/promotion gate |
| FR-EVA-009..010 | T009, T012..T015 | redaction and aggregate artifacts |
