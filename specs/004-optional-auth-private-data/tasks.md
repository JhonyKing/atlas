# Tasks: Optional Authentication and Private Data

**Input**: Design documents from `specs/004-optional-auth-private-data/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`, `quickstart.md`

**Tests**: Test-first tasks are included because authentication, ownership, uploads, and deletion are security-sensitive and the specification requires measurable verification.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Establish feature-specific modules and test fixtures without changing anonymous behavior.

- [x] T001 Create feature module directories under `apps/backend/src/atlas/auth/`, `apps/backend/src/atlas/privacy/`, and `apps/backend/src/atlas/uploads/`
- [ ] T002 [P] Create frontend feature directories under `apps/web/src/features/auth/` and `apps/web/src/features/private-data/`
- [ ] T003 [P] Add feature environment settings and safe defaults in `apps/backend/src/atlas/config.py`
- [ ] T004 [P] Add deterministic fake-auth and private-data fixtures in `apps/backend/tests/fixtures/auth_private_data.py`
- [ ] T005 [P] Add the feature quickstart commands to `Makefile` or the repository task runner configuration

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Implement the shared identity, authorization, privacy, and observability primitives required by all stories.

**Checkpoint**: No user story work is complete until these primitives pass their contract and security tests.

- [x] T006 [P] Write the AuthPort, session, ownership, and deletion service interfaces in `apps/backend/src/atlas/auth/ports.py`
- [x] T007 [P] Write redaction helpers for session tokens, provider keys, visitor IDs, and private content in `apps/backend/src/atlas/privacy/redaction.py`
- [ ] T008 Create the User, Session, OwnershipGrant, PrivateUpload, and DeletionJob SQLAlchemy models in `apps/backend/src/atlas/auth/models.py` and `apps/backend/src/atlas/uploads/models.py`
- [ ] T009 Create Alembic migration `database/migrations/versions/0018_identity.py` for users, sessions, and ownership grants
- [ ] T010 Create Alembic migration `database/migrations/versions/0019_private_data.py` for private uploads and deletion jobs
- [ ] T011 [P] Add database row-level security policies and indexes in `database/migrations/versions/0020_private_data_rls.py`
- [ ] T012 [P] Add SQL tests for identity isolation in `database/tests/009_identity_rls.sql`
- [ ] T013 [P] Add SQL tests for private-resource isolation and deletion scope in `database/tests/010_private_data_rls.sql`
- [x] T014 [P] Add request-context fields and ownership-decision events to `apps/backend/src/atlas/observability/events.py`
- [ ] T015 [P] Add contract-test helpers for authenticated and anonymous requests in `apps/backend/tests/contract/auth/conftest.py`
- [x] T016 Add a deterministic local AuthPort adapter in `apps/backend/src/atlas/auth/fake_provider.py`
- [x] T017 Add unit tests proving fake-provider sessions expire, revoke, and never expose raw tokens in `apps/backend/tests/unit/auth/test_fake_provider.py`

## Phase 3: User Story 1 - Sign in without losing anonymous work (Priority: P1) - MVP

**Goal**: Users can sign in, renew, log out, and retain the existing anonymous cited-answer/comparator behavior and quota semantics.

**Independent Test**: Run the US1 contract and browser tests; an anonymous request still works, a signed-in request receives a session, renewal rotates it, logout revokes it, and replaying a revoked token fails without leaking token data.

### Tests for User Story 1 (write first and verify failure)

- [x] T018 [P] [US1] Add OpenAPI contract tests for `GET/DELETE /v1/auth/session` in `apps/backend/tests/contract/auth/test_session_contract.py`
- [x] T019 [P] [US1] Add OpenAPI contract tests for `POST /v1/auth/renew` in `apps/backend/tests/contract/auth/test_renew_contract.py`
- [x] T020 [P] [US1] Add integration tests for anonymous quota preservation and optional sign-in in `apps/backend/tests/integration/auth/test_anonymous_transition.py`
- [ ] T021 [P] [US1] Add Playwright journeys for sign-in, renewal, logout, and revoked-session rejection in `apps/web/tests/auth/session.spec.ts`

### Implementation for User Story 1

- [x] T022 [US1] Implement provider-independent session issuance and validation in `apps/backend/src/atlas/auth/service.py`
- [x] T023 [US1] Implement login/session bootstrap endpoint in `apps/backend/src/atlas/api/routes/auth.py`
- [x] T024 [US1] Implement renewal token rotation and revocation endpoint in `apps/backend/src/atlas/api/routes/auth.py`
- [x] T025 [US1] Add auth dependency that distinguishes anonymous visitor context from authenticated subject in `apps/backend/src/atlas/api/dependencies.py`
- [ ] T026 [US1] Preserve anonymous HMAC quota accounting when a user authenticates in `apps/backend/src/atlas/quotas/service.py`
- [ ] T027 [US1] Add Spanish and English auth labels, errors, and locale selection in `apps/web/src/features/auth/i18n.ts`
- [ ] T028 [US1] Add sign-in, session status, renew, and logout UI state in `apps/web/src/features/auth/SessionPanel.tsx`
- [ ] T029 [US1] Wire session bootstrap and logout controls into `apps/web/src/app/page.tsx`
- [ ] T030 [US1] Add redacted auth audit events and request IDs to all auth routes in `apps/backend/src/atlas/api/routes/auth.py`

**Checkpoint**: US1 is independently demonstrable without private uploads or saved-resource migration.

## Phase 4: User Story 2 - Keep private research work under personal ownership (Priority: P2)

**Goal**: Authenticated users can create, list, inspect, and delete their own threads, reports, feedback, and artifacts; another user cannot access them.

**Independent Test**: Create resources as user A, verify user A can list/read/delete them, verify user B receives the documented not-found/forbidden response, and verify anonymous endpoints remain unchanged.

### Tests for User Story 2 (write first and verify failure)

- [x] T031 [P] [US2] Add contract tests for `GET /v1/private/resources` in `apps/backend/tests/contract/auth/test_private_resources_contract.py`
- [x] T032 [P] [US2] Add integration tests for ownership across threads, reports, feedback, and artifacts in `apps/backend/tests/integration/security/test_cross_user_resources.py`
- [ ] T033 [P] [US2] Add database policy tests proving user A cannot query or delete user B rows in `database/tests/011_cross_user_resources.sql`
- [ ] T034 [P] [US2] Add Playwright journey for private history and report ownership in `apps/web/tests/auth/private-resources.spec.ts`

### Implementation for User Story 2

- [x] T035 [US2] Add ownership grants and resource-owner lookup service in `apps/backend/src/atlas/privacy/ownership.py`
- [x] T036 [US2] Enforce application-level ownership checks for existing thread, report, feedback, and artifact repositories in `apps/backend/src/atlas/privacy/guards.py`
- [ ] T037 [US2] Enforce database RLS session variables and policies for owned resources in `database/migrations/versions/0020_private_data_rls.py`
- [x] T038 [US2] Implement private-resource list and deletion endpoints in `apps/backend/src/atlas/api/routes/private_data.py`
- [ ] T039 [US2] Add authenticated history/report navigation and ownership errors in `apps/web/src/features/private-data/PrivateResourcesPanel.tsx`
- [x] T040 [US2] Add repeat-safe deletion command handling with idempotency keys in `apps/backend/src/atlas/privacy/deletion.py`
- [ ] T041 [US2] Add ownership-decision traces without raw private content in `apps/backend/src/atlas/observability/events.py`

**Checkpoint**: US1 and US2 work independently, and cross-user access tests pass at both API and database layers.

## Phase 5: User Story 3 - Upload private source material safely (Priority: P3)

**Goal**: Authenticated users can upload bounded private files that are quarantined, scanned, parsed, and indexed only after ownership and safety checks succeed.

**Independent Test**: Upload a valid file as user A, observe quarantine-to-clean-to-indexed status, reject an unsafe or oversized file before indexing, and verify user B cannot read or delete user A's upload.

### Tests for User Story 3 (write first and verify failure)

- [ ] T042 [P] [US3] Add contract tests for `POST /v1/private/uploads` and `DELETE /v1/private/uploads/{upload_id}` in `apps/backend/tests/contract/auth/test_upload_contract.py`
- [ ] T043 [P] [US3] Add integration tests for file signature, MIME, size, scan, parse, and indexing gates in `apps/backend/tests/integration/security/test_private_upload_pipeline.py`
- [ ] T044 [P] [US3] Add database tests proving rejected uploads create no chunks or embeddings in `database/tests/012_upload_quarantine.sql`
- [ ] T045 [P] [US3] Add Playwright journey for valid, rejected, and cross-user upload operations in `apps/web/tests/auth/private-uploads.spec.ts`

### Implementation for User Story 3

- [ ] T046 [US3] Implement upload metadata, allowlist validation, and content-signature checks in `apps/backend/src/atlas/uploads/validation.py`
- [ ] T047 [US3] Implement quarantine storage adapter and scan-status transitions in `apps/backend/src/atlas/uploads/quarantine.py`
- [ ] T048 [US3] Implement `POST /v1/private/uploads` and upload-status responses in `apps/backend/src/atlas/api/routes/private_data.py`
- [ ] T049 [US3] Gate parsing, chunking, embedding, and retrieval on clean scan plus ownership in `apps/backend/src/atlas/uploads/pipeline.py`
- [ ] T050 [US3] Implement repeat-safe upload deletion and retention cleanup in `apps/backend/src/atlas/uploads/deletion.py`
- [ ] T051 [US3] Add private upload progress, rejection, and retention messages in Spanish and English in `apps/web/src/features/private-data/PrivateUploadPanel.tsx`
- [ ] T052 [US3] Add upload lifecycle and deletion traces with redacted storage keys in `apps/backend/src/atlas/observability/events.py`

**Checkpoint**: US3 is independently demonstrable and cannot publish rejected/private content to the public corpus.

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Close evidence, documentation, security, and reproducibility requirements for the feature.

- [ ] T053 [P] Add security regression suite for SC-IDN-003, SC-IDN-005, and SC-IDN-007 in `apps/backend/tests/security/test_auth_private_data_regressions.py`
- [ ] T054 [P] Add deterministic eval cases for login success, ownership denial, upload rejection, and idempotent deletion in `evals/cases/004-auth-private-data.jsonl`
- [ ] T055 [P] Add browser smoke commands and expected evidence to `specs/004-optional-auth-private-data/quickstart.md`
- [ ] T056 Run the complete quickstart, contract, integration, database, and browser suites and record results in `docs/verification/004-auth-private-data.md`
- [ ] T057 Update `README.md` with the optional-auth flow, anonymous compatibility, private-data boundaries, and local test commands
- [ ] T058 [P] Create architecture note `docs/architecture/004-identity-private-data.md` from the approved plan and implemented boundaries
- [ ] T059 [P] Create ADR `docs/adr/0003-optional-auth-boundary.md` documenting AuthPort, anonymous preservation, RLS, quarantine, and deletion decisions
- [ ] T060 Review LangSmith/observability traces to confirm no raw tokens, provider keys, visitor identifiers, or private content are emitted in `docs/verification/004-auth-private-data.md`
- [ ] T061 Mark every completed task in this file only after its test/evidence is recorded, then run `speckit-analyze` and `speckit-converge` before declaring Feature 004 closed

## Dependencies & Execution Order

- **Phase 1** has no feature dependencies.
- **Phase 2** depends on Phase 1 and blocks all user stories.
- **US1** depends on Phase 2 and is the MVP slice.
- **US2** depends on Phase 2 and reuses US1's authenticated subject; its ownership tests may start after the identity interfaces exist.
- **US3** depends on Phase 2 and the ownership guard from US2 before indexing private material.
- **Polish** depends on the desired user stories and is mandatory for closure.

### Parallel opportunities

- T002-T005 can run in parallel after T001.
- T006-T007, T011-T015 can run in parallel once paths exist.
- Within each story, contract, integration, database, and browser tests can be written in parallel before implementation.
- T058-T060 can run in parallel after implementation and evidence collection.

## Requirements Traceability

Every functional requirement and buildable success criterion from `spec.md` is covered by at
least one executable task and one verification/evidence task:

| Requirement | Implementation tasks | Verification/evidence tasks |
|---|---|---|
| FR-IDN-001 | T022-T029 | T020-T021, T055 |
| FR-IDN-002 | T022-T025 | T018-T021 |
| FR-IDN-003 | T026 | T020, T021 |
| FR-IDN-004 | T035-T039 | T032-T034 |
| FR-IDN-005 | T036-T037 | T032-T033, T053 |
| FR-IDN-006 | T038-T040 | T031-T034 |
| FR-IDN-007 | T046-T049 | T042-T045 |
| FR-IDN-008 | T040, T050 | T053, T056 |
| FR-IDN-009 | T007, T030, T041, T052 | T017, T053, T060 |
| FR-IDN-010 | T014, T030, T041, T052 | T056, T060 |
| SC-IDN-001 | T026-T029 | T020-T021, T055 |
| SC-IDN-002 | T022-T025 | T018-T021, T056 |
| SC-IDN-003 | T036-T040 | T032-T034, T053 |
| SC-IDN-004 | T046-T049 | T043-T045, T056 |
| SC-IDN-005 | T047-T049 | T043-T044, T053 |
| SC-IDN-006 | T040, T050 | T053, T056 |
| SC-IDN-007 | T007, T030, T041, T052 | T017, T053, T060 |

## Implementation Strategy

1. Complete Setup and Foundational phases.
2. Implement and validate US1 as the MVP; stop at its checkpoint for a demo.
3. Add US2 ownership enforcement and validate cross-user denial at API and database layers.
4. Add US3 quarantine and safe private ingestion.
5. Complete the mandatory evidence and documentation tasks before marking this feature closed.
