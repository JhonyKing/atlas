# Tasks: Model Router, GPT-5.6 Luna, and Cost Controls

## Phase 1: Contracts and tests

- [X] T001 Create model-router unit, integration and security test directories.
- [ ] T002 Add approved model/provider, failure, price, cache and benchmark fixtures.
- [X] T003 Add `scripts/verify-model-router.ps1` and `pnpm test:model-router`.
- [X] T004 Add contract tests for Luna default, complexity routing, unknown-model rejection and safe telemetry.
- [X] T005 Add resilience tests for timeout, retry jitter, circuit open/close and fallback.
- [X] T006 Add pricing, budget, cache invalidation and A/B promotion-gate tests.

## Phase 2: Routing and provider boundary

- [X] T007 Implement typed model contracts and Luna server setting.
- [X] T008 Implement complexity/freshness/contradiction/report-depth router policy.
- [ ] T009 Implement provider adapters and common response normalization.
- [X] T010 Implement bounded timeout/retry/circuit/fallback policy.

## Phase 3: Cost, cache and evaluation

- [X] T011 Implement effective-dated pricing and token/cost records.
- [ ] T012 Implement daily budget enforcement and redacted telemetry.
- [X] T013 Implement tenant-safe versioned cache/evidence-pack keys.
- [X] T014 Implement batch benchmark and A/B promotion decision.
- [ ] T015 Add multilingual embedding profile selection without changing Evidence.

## Phase 4: Verification and closure

- [ ] T016 Run targeted/full backend tests, Ruff, mypy and benchmark; record verification evidence.
- [ ] T017 Update README, architecture doc, ADR and PRD/status matrix.
- [ ] T018 Run SpecKit Analyze/Converge and close only with zero mandatory tasks.
