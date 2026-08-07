# Tasks: Scale, Reliability, and Launch SLOs

## Phase 1: Measurement contracts

- [ ] T001 Create SLO unit, integration and load-definition directories.
- [ ] T002 Add deterministic read/answer/report/ingestion/spike workload fixtures.
- [ ] T003 Add `scripts/verify-slo.ps1` and `pnpm test:slo`.
- [ ] T004 Add failing tests for SLO metrics, missing measurements, cache invalidation and separate limits.

## Phase 2: Reliability boundaries (P1)

- [ ] T005 Add measured pooling/index observation contracts without claiming unmeasured capacity.
- [ ] T006 Add resilience load cases for timeout, retry, circuit and fallback.
- [ ] T007 Add cache/source-version invalidation regression cases.
- [ ] T008 Add anonymous/authenticated limit measurement cases.

## Phase 3: Load and launch evidence

- [ ] T009 Implement deterministic workload runner and SLO gate metrics.
- [ ] T010 Record local smoke evidence; keep live load results explicitly pending.
- [ ] T011 Add citation/cost launch gates and failure explanations.
- [ ] T012 Add deployment, backup, alert, rollback and incident runbook.
- [ ] T013 Add 10k/100k MAU scale decision record with assumptions and limitations.

## Phase 4: Closure

- [ ] T014 Run backend/frontend tests, Ruff/mypy, SLO suite and SpecKit Analyze/Converge.
- [ ] T015 Update README, architecture, ADR, PRD/status matrix and verification evidence.

## Requirements Traceability

| Requirement | Tasks | Verification |
|---|---|---|
| FR-SCL-001..004 | T005..T007 | reliability and cache tests |
| FR-SCL-005..008 | T004, T008..T011 | workload/SLO gate |
| FR-SCL-009..010 | T012..T015 | runbook and scale record |
