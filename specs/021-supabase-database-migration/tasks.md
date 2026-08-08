---

description: "Dependency-ordered tasks for the ATLAS Supabase database migration"
---

# Tasks: Supabase Database Migration

**Input**: Design documents from `specs/021-supabase-database-migration/`

**Prerequisites**: `spec.md`, `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/migration-evidence.schema.json`

**Scope guard**: This feature migrates the reproducible schema and approved public seed state. It does not copy private/user rows, local credentials, or test fixtures.

## Phase 1: Setup (Repository Migration Inventory)

**Purpose**: Establish the exact repository state that will be compared with Supabase.

- [x] T001 [P] Create a deterministic ordered revision manifest from `database/migrations/versions/` in `scripts/supabase/migration_manifest.py`, including revision IDs, down-revision links, and SHA-256 file hashes.
- [x] T002 [P] Add unit coverage for revision ordering, duplicate IDs, missing links, and the expected 27-revision count in `apps/backend/tests/unit/database/test_migration_manifest.py`.
- [x] T003 [P] Document the project-scoped OAuth MCP setup, environment gate, no-secret policy, and operator ownership checks in `docs/runbooks/supabase-migration.md`.
- [x] T004 [P] Add a non-secret example configuration and prohibited-secret checklist to `docs/runbooks/supabase-migration.md`; do not add tokens, passwords, service-role keys, or database URLs.

**Checkpoint**: Repository migration inventory is reproducible and the operator runbook is reviewable without contacting Supabase.

## Phase 2: Foundational (Evidence and Safety Contracts)

**Purpose**: Build the validation and evidence boundaries before any remote write.

- [x] T005 Implement typed `MigrationEvidence` and `DriftFinding` validation against `specs/021-supabase-database-migration/contracts/migration-evidence.schema.json` in `apps/backend/src/atlas/database/migration_evidence.py`.
- [x] T006 [P] Add unit tests for evidence validation, secret redaction, bounded detail, allowed statuses, and project-reference enforcement in `apps/backend/tests/unit/database/test_migration_evidence.py`.
- [x] T007 Implement a read-only evidence writer that emits `inspect`, `apply`, and `verify` artifacts under `evals/results/supabase-migration-<timestamp>.json` without row payloads in `scripts/supabase/evidence_writer.py`.
- [x] T008 [P] Add JSON Schema validation tests for the evidence contract in `apps/backend/tests/unit/database/test_migration_evidence_contract.py`.
- [x] T009 [P] Add a repository-side migration checksum/manifest verification command in `scripts/supabase/verify_repository_migrations.py` that fails closed on duplicate or out-of-order revisions.
- [x] T010 Define the remote safety gate in `scripts/supabase/environment_gate.py`: require the expected project reference, classify development/staging/production, detect unexplained existing data, and block writes for production or unknown environments.
- [x] T011 [P] Add unit tests for the environment gate and private-data boundary in `apps/backend/tests/unit/database/test_supabase_environment_gate.py`.

**Checkpoint**: Local contracts, redaction, repository state, and environment gating pass before MCP access is used.

## Phase 3: User Story 1 - Provision the ATLAS schema (Priority: P1) - MVP

**Goal**: Apply all reviewed repository migrations to the project-scoped Supabase development project and verify the complete schema without copying private data.

**Independent Test**: A fresh read-first run identifies the project and remote revision state; an approved apply run records all 27 revisions in order; a follow-up verify run finds no missing objects or duplicate changes.

### Tests for User Story 1

- [x] T012 [P] [US1] Add a migration-history comparison test that compares the 27 repository revisions with the MCP-reported remote history in `apps/backend/tests/integration/database/test_supabase_migration_history.py`.
- [x] T013 [P] [US1] Add schema-inventory assertions for tables, constraints, indexes, and migration markers in `apps/backend/tests/integration/database/test_supabase_schema_inventory.py`.
- [x] T014 [P] [US1] Add an idempotent rerun test that proves a second verification/apply attempt produces no duplicate objects or destructive changes in `apps/backend/tests/integration/database/test_supabase_idempotency.py`.

### Implementation for User Story 1

- [x] T015 [US1] Implement the read-first Supabase MCP inspection procedure in `scripts/supabase/inspect_remote.py`, recording project metadata, remote migrations, object inventory, and bounded seed identifiers.
- [x] T016 [US1] Implement repository-to-remote drift classification in `scripts/supabase/compare_state.py`, producing `DriftFinding` records for revisions, tables, functions, indexes, policies, extensions, and seeds.
- [x] T017 [US1] Implement the reviewed migration apply procedure in `scripts/supabase/apply_migrations.py`, applying only missing ordered revisions through the authenticated project-scoped MCP and stopping on the first failure.
- [x] T018 [US1] Add explicit confirmation and dry-run output to `scripts/supabase/apply_migrations.py` so no remote write can occur before the environment gate and owner approval are recorded.
- [x] T019 [US1] Run the read-first inspection against project `fcbclsaytbjpywlaplbh` and export the initial non-secret artifact under `evals/results/`.
- [x] T020 [US1] After approval and a development/staging classification, apply the 27 repository revisions and export the apply artifact under `evals/results/`.
- [x] T021 [US1] Verify the post-apply schema inventory and migration history, then export the no-drift verification artifact under `evals/results/`.

**Checkpoint**: User Story 1 is complete only when the remote history, schema inventory, idempotent rerun, and evidence artifacts all pass.

## Phase 4: User Story 2 - Preserve security and retrieval behavior (Priority: P1)

**Goal**: Prove that pgvector, retrieval functions, provenance relationships, and RLS/private-data boundaries survive migration.

**Independent Test**: Run the repository SQL security/retrieval checks against non-production identities and bounded test records; anonymous and cross-user access is denied, provenance remains queryable, and vector retrieval succeeds.

### Tests for User Story 2

- [x] T022 [P] [US2] Add a remote integration test harness for the SQL checks in `database/tests/001_foundation.sql`, `database/tests/003_hybrid_retrieval.sql`, and `database/tests/006_provenance.sql` in `apps/backend/tests/integration/database/test_supabase_retrieval_provenance.py`.
- [x] T023 [P] [US2] Add RLS isolation checks covering identities, uploads, reports, comparisons, and agent checkpoints in `apps/backend/tests/integration/database/test_supabase_rls.py`.
- [x] T024 [P] [US2] Add a vector extension/type/function availability check and verify any repository-defined retrieval indexes for `database/functions/search_evidence.sql` in `apps/backend/tests/integration/database/test_supabase_pgvector.py`.

### Implementation for User Story 2

- [x] T025 [US2] Implement bounded extension, function, index, provenance, and RLS inspection in `scripts/supabase/verify_security_retrieval.py`.
- [x] T026 [US2] Run the repository SQL security and retrieval checks against the remote development project using non-production identities and synthetic records only.
- [x] T027 [US2] Record extension status, retrieval status, provenance checks, RLS results, elapsed time, and any drift in the `verify` evidence artifact without storing row contents.
- [x] T028 [US2] Prove that schema migration excludes local fixtures and private/user data by reviewing the migration input manifest and recording the exclusion check in `docs/runbooks/supabase-migration.md`.

**Checkpoint**: User Story 2 is complete only when all relevant security/retrieval checks pass and their evidence is attached to the migration run.

## Phase 5: User Story 3 - Establish a repeatable migration workflow (Priority: P2)

**Goal**: Make future repository migrations auditable, testable, and safe to repeat in development and CI.

**Independent Test**: A no-op verification compares repository and remote inventories, reports exact drift, validates the evidence artifact, and exits non-zero on an unexplained mismatch or failed migration.

### Tests for User Story 3

- [x] T029 [P] [US3] Add a contract test for evidence artifact validation and required provenance fields in `apps/backend/tests/integration/database/test_supabase_evidence_artifact.py`.
- [x] T030 [P] [US3] Add failure-path tests proving later revisions are not applied after a failed revision in `apps/backend/tests/integration/database/test_supabase_stop_on_failure.py`.
- [x] T031 [P] [US3] Add a no-op drift verification test and bounded latency assertion in `apps/backend/tests/integration/database/test_supabase_noop_verify.py`.

### Implementation for User Story 3

- [x] T032 [US3] Add a CI-invokable verification wrapper in `scripts/verify-supabase-migration.ps1` that runs manifest checks, evidence-schema validation, and read-only drift inspection without exposing credentials.
- [x] T033 [US3] Add CI job wiring for read-only Supabase migration verification in `.github/workflows/supabase-migration.yml`, gated so apply operations cannot run from untrusted pull requests.
- [x] T034 [US3] Document the inspect/apply/verify lifecycle, rollback or recovery behavior, failure semantics, and evidence locations in `docs/runbooks/supabase-migration.md`.
- [x] T035 [US3] Add an ADR documenting Supabase as the selected development database operations channel while PostgreSQL contracts remain provider-independent in `docs/adr/0013-supabase-development-migration.md`.
- [x] T036 [US3] Update `docs/product/feature-status-matrix.md` and `docs/product/implementation-status.md` with Feature 021 status and explicit remote-verification evidence links.

**Checkpoint**: User Story 3 is complete only when a future migration can be inspected, reviewed, applied, verified, and audited from repository artifacts and CI controls.

## Requirements and Outcome Traceability

| Requirement/outcome | Implementing and verifying tasks |
|---|---|
| FR-001 / SC-001 | T010, T015, T019, T020, T021 |
| FR-002 / SC-001 | T001, T002, T009, T012, T017, T020, T021 |
| FR-003 / SC-002 | T013, T015, T016, T021 |
| FR-004 / SC-003 | T024, T025, T026, T027 |
| FR-005 / SC-003 | T023, T025, T026, T027 |
| FR-006 / SC-003 | T022, T025, T026, T027 |
| FR-007 | T015, T018, T019 |
| FR-008 / SC-005 | T003, T004, T010, T018, T032, T033, T038 |
| FR-009 | T017, T018, T030 |
| FR-010 / SC-004 | T014, T021, T031, T039 |
| FR-011 / SC-003 | T022, T023, T024, T026, T037, T039 |
| FR-012 / SC-005/SC-006 | T005, T007, T008, T019, T020, T021, T027, T029, T038, T039 |
| FR-013 / SC-005 | T028, T034, T042 |

## Phase 6: Polish and Cross-Cutting Verification

**Purpose**: Reconcile implementation with SpecKit artifacts and preserve portfolio-grade evidence.

- [x] T037 [P] Run Python type checks, linting, unit tests, and the database migration manifest tests; record commands and outcomes in `docs/verification/021-supabase-migration.md`.
- [x] T038 [P] Validate every generated evidence artifact against `specs/021-supabase-database-migration/contracts/migration-evidence.schema.json` and redact any accidental secret or private-row content before commit.
- [x] T039 Run the complete `specs/021-supabase-database-migration/quickstart.md` procedure twice and attach the final inspect/apply/verify artifact paths to `docs/verification/021-supabase-migration.md`.
- [x] T040 Run `$speckit-analyze` for `specs/021-supabase-database-migration/` and resolve all CRITICAL/HIGH coverage or consistency findings before implementation is marked complete.
- [x] T041 Run `$speckit-converge` for `specs/021-supabase-database-migration/`, append any genuinely remaining work to this file, and do not mark the feature complete while required tasks remain unchecked.
- [x] T042 Update `README.md` with the Supabase migration status, operator prerequisites, evidence locations, and the explicit statement that no production/private data migration is implied.
- [x] T043 [US2] Add the reviewed `0025_supabase_security_hardening` migration and advisor regression check so ATLAS functions use an explicit search path on hosted Supabase.
- [x] T044 [US2] Add the reviewed `0026_supabase_extension_security` migration and regression checks for extension schema placement and public helper RPC privileges.
- [x] T045 [US2] Add the reviewed `0027_revoke_public_rls_helper` migration and verify the hosted helper is no longer executable through the public RPC surface.

## Dependencies and Execution Order

### Phase Dependencies

- **Phase 1** has no dependency and creates the repository inventory.
- **Phase 2** depends on Phase 1 and blocks every remote operation.
- **Phase 3 (US1)** depends on Phase 2 and is the MVP schema slice.
- **Phase 4 (US2)** depends on the successful US1 schema verification.
- **Phase 5 (US3)** depends on US1 and US2 evidence, then makes the workflow repeatable.
- **Phase 6** depends on all required story tasks and is the Definition of Done gate.

### User Story Dependencies

- **US1 (P1)**: Starts after Phase 2; no dependency on another user story.
- **US2 (P1)**: Starts after US1 has a verified schema; it must not run against a production project.
- **US3 (P2)**: Starts after US1 and US2 have evidence artifacts to encode into repeatable CI checks.

### Parallel Opportunities

- T001-T004 can run in parallel because they touch separate inventory, test, and documentation files.
- T005-T011 can run in parallel after the file contract is agreed, except tests depend on their corresponding implementation.
- T012-T014 and T022-T024 and T029-T031 are parallel test authoring tasks.
- T037-T038 are parallel verification tasks after implementation.

## Implementation Strategy

### MVP First

1. Complete Phase 1 and Phase 2 locally.
2. Complete US1 read-first inspection and migration verification.
3. Stop and review the evidence artifact before any US2 or private-data operation.

### Incremental Delivery

1. US1 provisions and proves the schema.
2. US2 proves security, provenance, and retrieval behavior.
3. US3 makes future changes auditable through CI and runbooks.
4. Phase 6 closes documentation and SpecKit convergence.

### Definition of Done

- All applicable task checkboxes are complete.
- No unexplained drift remains.
- The remote project is classified as development or staging before writes.
- The final inspect/apply/verify artifacts validate against the JSON Schema.
- No secrets or private row payloads are committed.
- `README.md`, the ADR, runbook, verification note, and feature status matrix link to the evidence.
