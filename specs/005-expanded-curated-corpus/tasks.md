# Tasks: Expanded Curated Corpus and Ingestion Governance

**Input**: Design documents from `specs/005-expanded-curated-corpus/`
**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`
**Tests**: Test-first tasks are mandatory because connectors, source policy, and private-content boundaries are security-sensitive.

## Phase 1: Setup

- [ ] T001 Create governance module directories under `apps/backend/src/atlas/ingestion/` and matching unit, contract, integration, and security test directories.
- [ ] T002 Add deterministic Feature 005 fixture catalog and clock helpers in `apps/backend/tests/fixtures/ingestion_governance.py`.
- [ ] T003 Add Feature 005 verification commands to `scripts/verify-ingestion.ps1` and root `package.json`.
- [ ] T004 Add governance feature settings with bounded defaults for refresh interval, TTL, retry count, and fetch size in `apps/backend/src/atlas/config.py`.

## Phase 2: Foundational contracts and persistence

- [ ] T005 [P] Add failing unit tests for catalog definitions, policy states, version transitions, and coverage aggregation in `apps/backend/tests/unit/ingestion/test_governance.py`.
- [ ] T006 [P] Add failing connector contract tests for GitHub releases, OpenAlex/Semantic Scholar metadata, pricing snapshots, and allowlist rejection in `apps/backend/tests/contract/ingestion/test_connectors.py`.
- [ ] T007 [P] Add failing normalization tests for HTML, Markdown, and PDF headings, tables, code blocks, hashes, and malformed input in `apps/backend/tests/unit/ingestion/test_normalization.py`.
- [ ] T008 [P] Add failing governance API contract tests for catalog, coverage, and disablement in `apps/backend/tests/contract/ingestion/test_governance_api.py`.
- [ ] T009 [P] Add failing SQL contract `database/tests/013_ingestion_governance.sql` for catalog policy, immutable versions, last-good preservation, and coverage tables.
- [ ] T010 [P] Add failing security regression tests for SSRF, unapproved redirect, private tenant leakage, disabled-source retrieval, and redaction in `apps/backend/tests/security/test_ingestion_governance.py`.
- [ ] T011 Implement typed governance entities and policy/state transition rules in `apps/backend/src/atlas/ingestion/governance.py`.
- [ ] T012 Implement deterministic in-memory governance repository with immutable source versions, change detection, last-good preservation, retries, and dead-letter transitions in `apps/backend/src/atlas/ingestion/governance.py`.
- [ ] T013 Create Alembic migration `database/migrations/versions/0022_ingestion_governance.py` for governed collections, sources, versions, policy reviews, connector runs, and coverage snapshots.
- [ ] T014 Add SQL constraints, indexes, and safe disablement transaction functions to `database/migrations/versions/0022_ingestion_governance.py`.

## Phase 3: User Story 1 — Approved catalog and bounded discovery (P1)

**Independent test**: The API and fixture refresh show the 16 approved deterministic collections and reject every destination outside its allowlist before fetching.

- [ ] T015 [P] [US1] Add catalog and discovery integration tests for 10 framework and 6 model-provider definitions in `apps/backend/tests/integration/ingestion/test_catalog_discovery.py`.
- [ ] T016 [P] [US1] Add governance route contract tests proving disabled collections cannot be refreshed in `apps/backend/tests/contract/ingestion/test_governance_api.py`.
- [ ] T017 [US1] Implement the deterministic 16-collection catalog and connector registry in `apps/backend/src/atlas/ingestion/catalog.py` and `apps/backend/src/atlas/ingestion/connectors/registry.py`.
- [ ] T018 [US1] Implement approved-host/path discovery planning and bounded candidate validation using `apps/backend/src/atlas/ingestion/fetcher.py` and `apps/backend/src/atlas/ingestion/governance.py`.
- [ ] T019 [US1] Add `GET /v1/corpus/governance` and `POST /v1/corpus/governance/{collection}/disable` routes in `apps/backend/src/atlas/api/routes/governance.py` and wire them in `apps/backend/src/atlas/api/main.py`.
- [ ] T020 [US1] Add the operator governance panel with Spanish and English labels in `apps/web/src/features/corpus/GovernancePanel.tsx` and wire it into `apps/web/src/app/page.tsx`.
- [ ] T021 [US1] Add Playwright catalog/coverage and disabled-source journeys in `apps/web/tests/e2e/ingestion-governance.spec.ts`.

## Phase 4: User Story 2 — Connectors, normalization, and versions (P2)

**Independent test**: Deterministic fixtures produce unchanged, changed, stale, and failed outcomes while preserving source versions and normalized structure.

- [ ] T022 [P] [US2] Add GitHub release/changelog fixture tests for tags, dates, links, duplicates, and malformed payloads in `apps/backend/tests/unit/ingestion/test_github_releases.py`.
- [ ] T023 [P] [US2] Add OpenAlex/Semantic Scholar fixture tests for identifiers, paper links, retractions, and conflicting metadata in `apps/backend/tests/unit/ingestion/test_scholarly.py`.
- [ ] T024 [P] [US2] Add pricing/model snapshot tests for effective dates, currency, change detection, and historical retention in `apps/backend/tests/unit/ingestion/test_pricing_snapshots.py`.
- [ ] T025 [P] [US2] Add retry/dead-letter and seven-day time-travel integration tests in `apps/backend/tests/integration/ingestion/test_refresh_lifecycle.py`.
- [ ] T026 [US2] Implement GitHub adapter in `apps/backend/src/atlas/ingestion/connectors/github_releases.py`.
- [ ] T027 [US2] Implement OpenAlex/Semantic Scholar adapter in `apps/backend/src/atlas/ingestion/connectors/scholarly.py`.
- [ ] T028 [US2] Implement effective-dated pricing/model snapshot adapter in `apps/backend/src/atlas/ingestion/connectors/pricing_snapshots.py`.
- [ ] T029 [US2] Extend `apps/backend/src/atlas/ingestion/normalizer.py` to preserve HTML/Markdown/PDF headings, tables, code blocks, page count, and content hashes with bounded errors.
- [ ] T030 [US2] Implement source version relation, stale/ current classification, update outcome, and last-good promotion in `apps/backend/src/atlas/ingestion/governance.py` and `apps/backend/src/atlas/ingestion/service.py`.
- [ ] T031 [US2] Add source metadata/provenance mapping for canonical URL, title, author/org, dates, license, hash, connector, and capture outcome in `apps/backend/src/atlas/ingestion/governance.py`.

## Phase 5: User Story 3 — Authorized private content (P3)

**Independent test**: An owner can ingest private material into a tenant-scoped record; another user receives safe denial and the public corpus remains unchanged.

- [ ] T032 [P] [US3] Add private connector ownership and no-public-promotion tests in `apps/backend/tests/integration/ingestion/test_private_connector.py`.
- [ ] T033 [P] [US3] Add cross-tenant and trace-redaction tests for private connector runs in `apps/backend/tests/security/test_ingestion_governance.py`.
- [ ] T034 [US3] Implement authorized private-content connector seam using Feature 004 ownership/quarantine services in `apps/backend/src/atlas/ingestion/connectors/private_content.py`.
- [ ] T035 [US3] Add private source state and retention metadata to governance persistence models/migration without weakening existing RLS in `apps/backend/src/atlas/ingestion/governance.py` and `database/migrations/versions/0022_ingestion_governance.py`.

## Phase 6: User Story 4 — Policy, takedown, retries, and coverage (P4)

**Independent test**: Review gates block enablement, approved correction/takedown disables retrieval atomically, and the dashboard exposes all operational states.

- [ ] T036 [P] [US4] Add policy review, correction, takedown, and atomic disablement tests in `apps/backend/tests/integration/ingestion/test_policy_lifecycle.py`.
- [ ] T037 [P] [US4] Add coverage snapshot API and seven-day target tests in `apps/backend/tests/unit/ingestion/test_coverage.py`.
- [ ] T038 [US4] Implement policy review gates and source-state transitions in `apps/backend/src/atlas/ingestion/governance.py`.
- [ ] T039 [US4] Implement bounded retry, dead-letter, preservation, and re-review triggers in `apps/backend/src/atlas/ingestion/governance.py` and `apps/backend/src/atlas/ingestion/worker.py`.
- [ ] T040 [US4] Implement coverage/freshness/disabled/retry/dead-letter aggregation and API serialization in `apps/backend/src/atlas/ingestion/governance.py` and `apps/backend/src/atlas/api/routes/governance.py`.
- [ ] T041 [US4] Add observability events with run ID, latency, outcome, and safe error code in `apps/backend/src/atlas/observability/events.py` and governance execution paths.

## Phase 7: Polish, evidence, and convergence

- [ ] T042 Run migration and SQL contracts, full backend regression, governance suites, lint, mypy, and browser tests; record evidence in `docs/verification/005-expanded-curated-corpus.md`.
- [ ] T043 Update `README.md` with Feature 005 scope, operator commands, allowlist behavior, and evidence path.
- [ ] T044 Create architecture note `docs/architecture/005-ingestion-governance.md`.
- [ ] T045 Create ADR `docs/adr/0004-curated-corpus-governance.md`.
- [ ] T046 Add deterministic eval cases for catalog coverage, blocked destination, version change, stale source, takedown, and private isolation in `evals/cases/005-expanded-curated-corpus.jsonl`.
- [ ] T047 Mark every completed task only after evidence is recorded, then run `speckit-analyze` and `speckit-converge` before declaring Feature 005 closed.

## Dependencies and Execution Order

- Phase 1 and Phase 2 block all user stories.
- US1 establishes the catalog and allowlist boundary.
- US2 depends on US1 and adds connector/version behavior.
- US3 depends on Feature 004 ownership/quarantine and may proceed after US1.
- US4 depends on version and run state from US2.
- Polish depends on all user stories.

## Parallel Opportunities

- T005–T010 can run in parallel after setup.
- T022–T024 and T032–T033 can run in parallel because they use independent fixtures.
- T036–T037 can run in parallel after governance state entities exist.
- T043–T046 can run in parallel after all evidence is collected.

## Requirements Traceability

| Requirement | Implementation tasks | Verification tasks |
|---|---|---|
| FR-ING-001 | T017 | T015, T042 |
| FR-ING-002–005 | T026–T028, T034–T035 | T006, T022–T024, T032 |
| FR-ING-006 | T018, T029 | T006, T010, T015 |
| FR-ING-007–009 | T029–T031 | T007, T025, T042 |
| FR-ING-010–012 | T038–T039 | T009–T010, T036 |
| FR-ING-013–015 | T040–T041, T042 | T037, T042, T046 |
| SC-ING-001–008 | T017–T041 | T005–T010, T015, T021–T025, T032–T037, T042, T046 |

## Implementation Strategy

1. Complete the catalog/discovery MVP (US1) and demonstrate it without live credentials.
2. Add deterministic connector/version fixtures (US2), then integrate bounded production seams.
3. Reuse Feature 004 private ownership for tenant-scoped content (US3).
4. Finish policy/takedown/coverage operations (US4), collect evidence, and converge before closure.
