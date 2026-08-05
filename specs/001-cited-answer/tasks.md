# Tasks: Verifiable Cited Answer

**Input**: Design documents from `specs/001-cited-answer/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, and
`quickstart.md`

**Tests**: Required by the ATLAS constitution. For every behavior task, write the listed test first,
run it, and record the expected failure before implementation.

**Organization**: Tasks are grouped by independently testable user story. Setup and foundational
work establish the smallest shared platform needed by all three stories.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Can run in parallel because it changes different files and has no dependency on another
  incomplete task in the same phase.
- **[Story]**: Maps a task to User Story 1, 2, or 3.
- Every task names its intended file or directory.

## Phase 1: Setup

**Purpose**: Reproducible monorepo, local infrastructure, and quality commands.

- [X] T001 Create repository hygiene files `.gitignore`, `.gitattributes`, and `.editorconfig`, excluding `.env*`, `.review_atlas/`, `tmp/`, build output, coverage, and local model artifacts
- [X] T002 [P] Create root Node workspace files `package.json`, `pnpm-workspace.yaml`, and `pnpm-lock.yaml` with pinned package-manager metadata and shared lint/typecheck/test scripts
- [X] T003 [P] Create Python project and lock files `apps/backend/pyproject.toml`, `apps/backend/uv.lock`, and `apps/backend/src/atlas/__init__.py` for Python 3.13 and the dependency lines approved in `plan.md`
- [X] T004 [P] Scaffold the strict TypeScript Next.js application in `apps/web/` with App Router, package metadata, linting, type checking, Vitest, and Playwright configuration
- [X] T005 [P] Create local PostgreSQL/pgvector infrastructure in `compose.yaml` and `infra/containers/postgres/` with a deterministic health check and persistent development volume
- [X] T006 [P] Create typed configuration examples and secret policy in `.env.example`, `apps/backend/src/atlas/config.py`, and `apps/web/src/lib/env.ts` without real credentials
- [X] T007 Create initial CI quality workflow in `.github/workflows/ci.yml` that installs frozen locks and exposes separate Python, web, database, and offline-eval jobs

**Checkpoint**: A clean clone can install locked dependencies and start the local database without
application source beyond scaffolding.

---

## Phase 2: Foundational

**Purpose**: Blocking contracts, persistence, providers, ingestion, privacy, and observability.

**CRITICAL**: No user-story implementation begins until these tasks pass.

- [X] T008 [P] Write failing configuration and secret-redaction tests in `apps/backend/tests/unit/test_config.py` and `apps/web/src/lib/env.test.ts`
- [X] T009 Implement validated settings, safe defaults, and secret-redacted representations in `apps/backend/src/atlas/config.py` and `apps/web/src/lib/env.ts` to satisfy T008
- [X] T010 [P] Write failing API health contract tests for `GET /healthz`, including database-ready and dependency-degraded responses, in `apps/backend/tests/contract/api/test_health.py`
- [X] T011 Implement the FastAPI application factory and `GET /healthz` route in `apps/backend/src/atlas/api/main.py` and `apps/backend/src/atlas/api/routes/health.py` to satisfy T010 without leaking credentials or internal exception details
- [X] T012 [P] Write failing database extension, role, RLS/grant, and schema contract tests in `database/tests/001_foundation.sql`
- [X] T013 Implement versioned Alembic/PostgreSQL migrations for schemas, least-privilege roles, `vector`, `pgmq`, `pg_cron`, and common timestamp/UUID helpers in `database/migrations/` to satisfy T012
- [X] T014 [P] Write failing domain-schema tests for Question, AnswerDraft, Claim, Evidence, Citation, CorpusStatus, and controlled errors in `apps/backend/tests/unit/domain/test_schemas.py`
- [X] T015 Implement strict Pydantic domain contracts and enums in `apps/backend/src/atlas/domain/` to satisfy T014 without importing provider SDK types
- [X] T016 [P] Write failing provider-port and deterministic-fake tests in `apps/backend/tests/unit/providers/test_ports.py`
- [X] T017 Implement `AnswerGenerator`, `EmbeddingProvider`, clock, pricing, and source-fetch ports plus deterministic fakes in `apps/backend/src/atlas/providers/ports.py` and `apps/backend/tests/fakes/`
- [X] T018 [P] Write failing OpenAI adapter contract tests with injected HTTP/SSE fixtures in `apps/backend/tests/contract/providers/test_openai_responses.py`
- [X] T019 Implement the async Responses API adapter with exact `gpt-5.6-luna`, medium effort, `store=false`, current-turn reasoning, Pydantic parsing, HMAC `safety_identifier`, telemetry, and bounded retries in `apps/backend/src/atlas/providers/openai_responses.py`
- [X] T020 [P] Write failing embedding adapter and dimension-invariant tests in `apps/backend/tests/contract/providers/test_openai_embeddings.py`
- [X] T021 Implement the `text-embedding-3-small` adapter and versioned embedding profile in `apps/backend/src/atlas/providers/openai_embeddings.py`
- [X] T022 [P] Write failing SSRF, redirect, content-size/type, prompt-injection-boundary, Markdown normalization, hashing, and structure-aware chunking tests in `apps/backend/tests/unit/ingestion/`
- [X] T023 Implement the allowlisted HTTP fetcher, normalizer, hasher, and heading-aware chunker in `apps/backend/src/atlas/ingestion/fetcher.py`, `normalizer.py`, and `chunker.py` to satisfy T022
- [X] T024 [P] Add official-source connector fixtures and failing discovery/version tests in `apps/backend/tests/fixtures/sources/` and `apps/backend/tests/unit/ingestion/test_connectors.py`
- [X] T025 Complete and record the terms, robots, licensing, allowed-path, attribution, review-date, and re-review-trigger decision for LangGraph, LangChain, and OpenAI in `docs/governance/source-reviews/`, leaving every source disabled unless its review explicitly passes
- [X] T026 Implement the LangGraph, LangChain, and OpenAI documentation/changelog/release connectors in `apps/backend/src/atlas/ingestion/connectors/`, enabling only the collections approved by T025
- [X] T027 [P] Write failing corpus/ingestion migration tests covering immutable versions, atomic promotion, failed-refresh preservation, snapshots, queue idempotency, and dead-letter state in `database/tests/002_corpus_ingestion.sql`
- [X] T028 Implement corpus, embedding, snapshot, ingestion-run, PGMQ queue, and daily Cron migrations/functions in `database/migrations/` and `database/functions/` to satisfy T027
- [X] T029 Write failing ingestion service and worker tests for scheduled/manual triggers, locks, retries, deduplication, embedding, and atomic promotion in `apps/backend/tests/integration/ingestion/test_worker.py`
- [X] T030 Implement durable enqueueing, ingestion orchestration, and the worker entry point in `apps/backend/src/atlas/ingestion/service.py` and `apps/backend/src/atlas/ingestion/worker.py` to satisfy T029
- [X] T031 [P] Write failing operator ingestion endpoint contract tests from `contracts/openapi.yaml` in `apps/backend/tests/contract/api/test_operator_ingestion.py`
- [X] T032 Implement authenticated operator ingestion endpoints in `apps/backend/src/atlas/api/routes/operator_ingestion.py` without exposing worker or database credentials
- [X] T033 [P] Write failing request-ID, content-free telemetry, price-table, and sensitive-log redaction tests in `apps/backend/tests/unit/observability/`
- [X] T034 Implement request context, structured logging, OpenTelemetry spans, effective-dated price lookup, and cost metrics in `apps/backend/src/atlas/observability/`
- [X] T035 [P] Write failing anonymous-cookie, HMAC identity, idempotency, concurrent rolling-window quota, retry-time, and global-budget tests in `apps/backend/tests/integration/security/test_anonymous_quota.py`
- [X] T036 Implement anonymous identity middleware and transactional quota reservation in `apps/backend/src/atlas/api/middleware/anonymous_identity.py`, `apps/backend/src/atlas/persistence/quota.py`, and `database/functions/reserve_answer_quota.sql` to satisfy T035

**Checkpoint**: Three collections can be refreshed durably; provider adapters and domain contracts
are testable; public questions can be identified and quota-reserved without fingerprinting.

---

## Phase 3: User Story 1 - Ask a Technical Question (Priority: P1) MVP

**Goal**: A visitor asks an in-scope question and receives a verified cited answer with visible
progress.

**Independent Test**: With seeded official-source fixtures and provider fakes, submit one supported
question and verify a terminal completed result in which every principal claim references retrieved
evidence and no draft claim is streamed early.

### Tests for User Story 1

- [X] T037 [P] [US1] Write failing hybrid-retrieval SQL tests for full-text candidates, exact vector candidates, filters, reciprocal-rank fusion, deduplication, and stable evidence IDs in `database/tests/003_hybrid_retrieval.sql`
- [X] T038 [P] [US1] Write failing retrieval-service tests for query constraints, top-k bounds, corpus snapshot selection, and deterministic ordering in `apps/backend/tests/unit/retrieval/test_service.py`
- [X] T039 [P] [US1] Write failing supported-path LangGraph tests for node order, state isolation, structured generation, evidence-ID validation, verified finalization, provider timeout, and cancellation in `apps/backend/tests/unit/agent/test_cited_answer_graph.py`
- [X] T040 [P] [US1] Write failing API/SSE contract tests for `POST /v1/answers`, `GET /v1/answers/{run_id}`, and the repeat-safe cancellation request `DELETE /v1/answers/{run_id}`, including empty, punctuation-only, over-limit, unrelated-multi-question, repeated-cancel, and entered-text-preservation cases, in `apps/backend/tests/contract/api/test_answers.py`
- [X] T041 [P] [US1] Write failing accessible question-form, invalid-input text preservation, progress live-region, explicit cancel, and completed-answer component tests in `apps/web/src/features/cited-answer/__tests__/`

### Implementation for User Story 1

- [X] T042 [US1] Implement versioned exact hybrid retrieval and RRF SQL in `database/functions/search_evidence.sql` with GIN/B-tree indexes in `database/migrations/` to satisfy T037
- [X] T043 [US1] Implement repository and retrieval services in `apps/backend/src/atlas/persistence/corpus_repository.py` and `apps/backend/src/atlas/retrieval/service.py` to satisfy T038
- [X] T044 [US1] Implement the typed LangGraph state, nodes, conditional edges, dependency context, and graph factory in `apps/backend/src/atlas/agent/cited_answer_graph.py` to satisfy T039
- [X] T045 [US1] Implement answer-run persistence, run evidence, claims, claim-evidence integrity, usage events, and terminal-state transitions in `database/migrations/` and `apps/backend/src/atlas/persistence/answer_repository.py`
- [X] T046 [US1] Implement verified event-stream serialization and disconnect cancellation in `apps/backend/src/atlas/api/answer_events.py` according to `contracts/answer-events.md`
- [X] T047 [US1] Implement `POST /v1/answers`, `GET /v1/answers/{run_id}`, and repeat-safe cancellation through `DELETE /v1/answers/{run_id}` in `apps/backend/src/atlas/api/routes/answers.py` with invalid-input handling, request deduplication, quota, controlled errors, cancellation, and no provisional claim text
- [X] T048 [US1] Implement typed API/SSE client and explicit cancellation handling in `apps/web/src/lib/atlas-api/` from `contracts/openapi.yaml`
- [X] T049 [US1] Implement the English question page, constraint controls, invalid-input text preservation, progress, explicit cancellation, completed claims, and quota/error states in `apps/web/src/app/page.tsx` and `apps/web/src/features/cited-answer/` to satisfy T041
- [X] T050 [US1] Add the supported-question, invalid-question, and explicit-cancellation Playwright journeys in `apps/web/tests/e2e/cited-answer-supported.spec.ts` and verify the independent-test checkpoint

**Checkpoint**: User Story 1 is deployable and demonstrable using the fake provider and seeded corpus.

---

## Phase 4: User Story 2 - Inspect the Evidence (Priority: P2)

**Goal**: A reader opens every citation and inspects canonical provenance, dates, version context,
and the exact supporting excerpt.

**Independent Test**: Open each citation in the prepared supported answer; verify the evidence panel
shows only database-owned metadata and that the canonical official URL can be followed with keyboard
navigation.

### Tests for User Story 2

- [X] T051 [P] [US2] Write failing claim-evidence referential-integrity and immutable-metadata tests in `database/tests/004_claim_evidence.sql`
- [X] T052 [P] [US2] Write failing citation/feedback API contract tests for retained, missing, expired, and replaced-feedback cases in `apps/backend/tests/contract/api/test_citations_feedback.py`
- [X] T053 [P] [US2] Write failing keyboard, focus, source-metadata, external-link, inference-label, and no-color-only citation component tests in `apps/web/src/features/evidence/__tests__/`

### Implementation for User Story 2

- [X] T054 [US2] Add composite foreign keys and database views that materialize canonical citation metadata from immutable corpus rows in `database/migrations/` and `database/functions/get_answer_result.sql` to satisfy T051
- [X] T055 [US2] Implement citation assembly and inference labeling in `apps/backend/src/atlas/domain/citations.py` and `apps/backend/src/atlas/persistence/answer_repository.py`
- [X] T056 [US2] Implement idempotent `PUT /v1/answers/{run_id}/feedback` and expired-content semantics in `apps/backend/src/atlas/api/routes/feedback.py` to satisfy T052
- [X] T057 [US2] Implement the accessible evidence panel, source metadata, canonical/revision links, and feedback controls in `apps/web/src/features/evidence/` to satisfy T053
- [ ] T058 [US2] Add the citation-inspection and feedback Playwright journey in `apps/web/tests/e2e/evidence-inspection.spec.ts` and verify the independent-test checkpoint

**Checkpoint**: User Stories 1 and 2 operate independently and citations are auditable end to end.

---

## Phase 5: User Story 3 - Receive an Honest Abstention (Priority: P3)

**Goal**: Unsupported, partial, contradictory, out-of-scope, and malicious-source cases fail safely
without fabricated claims or citations.

**Independent Test**: Run prepared no-evidence, contradiction, out-of-scope, and prompt-injection
fixtures; every run either returns supported-only partial content with limitations or an explicit
abstention.

### Tests for User Story 3

- [ ] T059 [P] [US3] Add failing graph-path tests for insufficient evidence, invented evidence IDs, claim without evidence, contradiction, partial support, and controlled provider refusal in `apps/backend/tests/unit/agent/test_abstention_paths.py`
- [ ] T060 [P] [US3] Add failing malicious-source and unauthorized-instruction fixtures plus integration tests in `apps/backend/tests/fixtures/security/` and `apps/backend/tests/integration/security/test_prompt_injection.py`
- [ ] T061 [P] [US3] Write failing abstention, disagreement, partial-answer, and out-of-scope UI tests in `apps/web/src/features/cited-answer/__tests__/abstention.test.tsx`

### Implementation for User Story 3

- [ ] T062 [US3] Implement deterministic evidence sufficiency, evidence-ID, citation coverage, temporal metadata, and terminal verification gates in `apps/backend/src/atlas/agent/verification.py` to satisfy T059
- [ ] T063 [US3] Implement supported-only partial answers, dated disagreement presentation, refusal handling, and structured abstention nodes in `apps/backend/src/atlas/agent/cited_answer_graph.py`
- [ ] T064 [US3] Harden evidence prompt boundaries and ensure the model has no source-selection or action tools in `apps/backend/src/atlas/providers/prompts/cited_answer.py` to satisfy T060
- [ ] T065 [US3] Implement accessible abstention, limitation, disagreement, and out-of-scope states in `apps/web/src/features/cited-answer/` to satisfy T061
- [ ] T066 [US3] Add Playwright journeys for abstention and prompt-injection resistance in `apps/web/tests/e2e/cited-answer-abstention.spec.ts`

**Checkpoint**: All three user stories are independently testable and safe-failure behavior is public.

---

## Phase 6: Polish and Cross-Cutting Quality Gates

**Purpose**: Retention, public corpus status, evaluation evidence, operations, and portfolio handoff.

- [ ] T067 [P] Write failing 30-day purge, aggregate-preservation, batching, idempotency, and no-user-dimension tests in `database/tests/005_retention.sql` and `apps/backend/tests/integration/retention/test_purge.py`
- [ ] T068 Implement aggregate rollup, cascading interaction-content deletion, expired-result tombstones, and daily retention scheduling in `database/functions/purge_expired_interactions.sql`, `database/migrations/`, and `apps/backend/src/atlas/persistence/retention.py` to satisfy T067
- [ ] T069 [P] Add corpus-status endpoint and UI tests in `apps/backend/tests/contract/api/test_corpus.py` and `apps/web/src/features/corpus/__tests__/corpus-status.test.tsx`, then implement `apps/backend/src/atlas/api/routes/corpus.py` and `apps/web/src/features/corpus/`
- [ ] T070 [P] Create the versioned evaluation dataset and deterministic evaluators in `evals/datasets/cited-answer-v1.jsonl`, `evals/evaluators/`, and `apps/backend/src/atlas/evaluation/` covering 30 in-scope, 10 temporal, abstention, contradiction, and injection cases
- [ ] T071 Create the evaluation CLI and CI regression gate in `apps/backend/src/atlas/evaluation/cli.py` and `.github/workflows/evals.yml`, recording model, prompt, retrieval, embedding, corpus snapshot, latency, tokens, cost, and required thresholds
- [ ] T072 [P] Add load/limit/cancellation checks for portfolio launch SLOs in `apps/backend/tests/load/` without asserting 10k/100k-user capacity
- [ ] T073 [P] Document architecture, graph, data flow, privacy/threat model, and measured trade-offs in `docs/architecture/001-cited-answer.md`, `docs/adr/`, and `docs/runbooks/`
- [ ] T074 Execute a moderated five-person external usability study for SC-007 using `docs/research/001-cited-answer-usability-protocol.md`, record only consented non-identifying observations and the four-of-five result in `evals/results/001-cited-answer-usability.md`, and create follow-up defects for any failed critical flow
- [ ] T075 Run the seven-day scheduled-refresh validation for SC-009, calculate per-collection and aggregate success rates from ingestion records, verify failed-run preservation, and record timestamps, failures, and the 95% result in `evals/results/001-cited-answer-refresh-7d.md`
- [ ] T076 Execute every scenario in `specs/001-cited-answer/quickstart.md`, record the consolidated results in `evals/results/001-cited-answer-baseline.md`, and fix any divergence before completion
- [ ] T077 Update `README.md` with problem, scoped demo, setup, architecture, evaluation table, cost/latency results, usability and refresh-validation results, security limits, known limitations, and links to the feature artifacts

---

## Dependencies and Execution Order

### Phase dependencies

```text
Phase 1 Setup
  -> Phase 2 Foundational
      -> Phase 3 US1 (public cited answer MVP)
          -> Phase 4 US2 (evidence inspection)
          -> Phase 5 US3 (honest abstention)
              -> Phase 6 polish and measured release
```

- Phase 2 blocks every user story.
- US1 is the first deployable MVP.
- US2 depends on the answer/citation records introduced by US1 but is independently acceptance-tested.
- US3 shares the US1 graph but owns its own negative paths and independent acceptance fixtures.
- US2 and US3 may proceed in parallel after US1 if changes to shared graph/result contracts are
  coordinated; sequential execution is recommended for a solo portfolio project.

### Entity and contract mapping

- US1: `answer_runs`, `run_evidence`, `claims`, `claim_evidence`, `usage_events`, answer/SSE routes.
- US2: citation views, canonical source metadata, `feedback`, retained-answer and feedback routes.
- US3: verification statuses, limitations, abstention/disagreement terminal results.
- Foundation: collections, sources, source versions, chunks, embeddings, snapshots, ingestion runs.

## Parallel Opportunities

### Setup

After T001, T002-T006 touch independent workspace areas. T007 waits for their command names.

### User Story 1

```text
T037 database retrieval tests
T038 backend retrieval tests
T039 graph tests
T040 API/SSE/cancellation/validation tests
T041 web component tests
```

These can be authored together after Phase 2; implementations T042-T049 then follow their respective
failing tests and integration dependencies.

### User Story 2

T051, T052, and T053 can be authored in parallel. T054-T057 follow; T058 is the integration gate.

### User Story 3

T059, T060, and T061 can be authored in parallel. T062-T065 follow; T066 is the integration gate.

## Implementation Strategy

### MVP first

1. Complete Setup and Foundational.
2. Complete US1 only.
3. Stop and run its independent test with fakes and seeded corpus.
4. Run the first offline baseline and record deficiencies.
5. Continue to evidence inspection and safe-failure stories without adding deferred PRD scope.

### Incremental delivery

- Increment 1: reproducible ingestion and retrieval foundation.
- Increment 2: supported cited answers with progress and quota.
- Increment 3: inspectable evidence and feedback.
- Increment 4: abstention, contradiction, and injection resistance.
- Increment 5: retention, public metrics, and portfolio documentation.

### Task discipline

- Execute one task or one tightly coupled test/implementation pair at a time.
- Confirm the listed test fails for the expected reason before its implementation task.
- Do not add authentication, Spanish localization, report generation, live-web search, reranking,
  HNSW, multiple answer models, or durable LangGraph memory to this feature.
- Update spec/plan/contracts before accepting behavior that differs from these artifacts.
