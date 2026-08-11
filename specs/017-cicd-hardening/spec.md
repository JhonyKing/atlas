# Feature Specification: CI/CD Hardening

**Feature Branch**: `017-cicd-hardening`

**Created**: 2026-08-06

**Status**: Implemented

**Input**: User request to continue the project by improving the maturity and evidence of the
commit-to-merge CI/CD path.

## User Scenarios & Testing

### User Story 1 - Validate a clean database in CI (Priority: P1)

As a maintainer, I want every pull request to prove that a new database can be migrated and that
the database contracts pass, so schema drift cannot reach the main branch unnoticed.

**Why this priority**: The current database job checks only that PostgreSQL and pgvector start;
it does not prove that the versioned schema can be created.

**Independent Test**: Run the database CI job against a fresh PostgreSQL service and observe that
all migrations and selected SQL contracts complete successfully.

**Acceptance Scenarios**:

1. **Given** a fresh PostgreSQL service, **When** the database job runs, **Then** all versioned
   migrations apply successfully from the initial revision to the head revision.
2. **Given** the migrated database, **When** the foundation, ingestion, retrieval, retention,
   provenance, collection-expansion, and daily-news contracts run, **Then** each contract exits
   successfully.
3. **Given** a migration or contract failure, **When** the job completes, **Then** the job fails
   and the pull request cannot be considered green.

### User Story 2 - Run the browser journey in CI (Priority: P2)

As a maintainer, I want the user-facing cited-answer journey to run in CI, so a merge cannot break
the accessible bilingual interface while backend checks remain green.

**Why this priority**: Browser tests exist in the repository but are not currently invoked by the
CI workflow.

**Independent Test**: Run the web CI job on a clean runner and verify that the configured
Playwright journeys execute and fail the job on a browser regression.

**Acceptance Scenarios**:

1. **Given** a clean Node 24 environment, **When** the web job runs, **Then** dependencies install
   from the lockfile and the configured Playwright browsers are available.
2. **Given** the local web app and its API test doubles, **When** the browser suite runs, **Then**
   the cited-answer, abstention, evidence, comparison, and locale journeys complete.

### User Story 3 - Make evaluation scope explicit (Priority: P3)

As a reviewer, I want CI artifacts to state whether an evaluation used deterministic fixtures or
provided model results, so a green evaluation is not mistaken for a live RAG quality measurement.

**Why this priority**: The current offline gate is valuable but deterministic; reviewers need that
boundary to be visible in the pipeline artifact.

**Independent Test**: Inspect the uploaded evaluation JSON and confirm it records its execution mode,
dataset, thresholds, and summary.

**Acceptance Scenarios**:

1. **Given** CI runs the cited-answer dataset without external results, **When** the artifact is
   uploaded, **Then** it identifies `deterministic-fixture` execution mode.
2. **Given** a threshold regression, **When** the evaluator exits, **Then** the evaluation job fails.

## Edge Cases

- A migration must be repeat-safe when the database is already at the head revision.
- A SQL contract must stop at its first failure rather than report a false success.
- Browser installation or startup failure must fail the web job rather than silently skip E2E tests.
- CI must not require provider API keys or transmit user content to external services.
- A database job must not depend on the developer's local Docker volume or local migration state.

## Requirements

### Functional Requirements

- **FR-001**: The pull-request CI path MUST migrate a fresh PostgreSQL database to the current
  migration head.
- **FR-002**: The database CI path MUST run the repository's versioned SQL contract tests with
  `ON_ERROR_STOP` semantics.
- **FR-003**: The web CI path MUST execute the repository's Playwright browser suite in addition to
  lint, typecheck, unit tests, and build.
- **FR-004**: The browser CI path MUST use the repository's pinned Node and package-manager
  versions and MUST install dependencies from the lockfile.
- **FR-005**: The CI evaluation artifact MUST record dataset identity, execution mode, thresholds,
  and aggregate results.
- **FR-006**: CI MUST remain runnable without OpenAI, LangSmith, or other provider secrets.
- **FR-007**: A failed migration, SQL contract, browser test, static check, or evaluation threshold
  MUST produce a failing job status.
- **FR-008**: The feature MUST NOT claim that deterministic fixture evaluation is equivalent to a
  live retrieval/model evaluation.

### Key Entities

- **Migration head**: The latest versioned database schema revision expected by the application.
- **Database contract**: A versioned SQL assertion suite that checks required schema behavior.
- **CI evaluation artifact**: A machine-readable report containing evaluation identity, mode,
  thresholds, and results.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A fresh CI database reaches the migration head and passes all selected SQL contracts
  in 100% of successful runs.
- **SC-002**: Every pull request executes the configured Playwright browser suite; no browser test
  is silently omitted.
- **SC-003**: A deliberately failing migration, SQL contract, browser test, or evaluation threshold
  causes its CI job to exit non-zero.
- **SC-004**: Every evaluation artifact identifies its execution mode and dataset version.
- **SC-005**: The CI path completes without requiring external provider credentials.

## Assumptions

- PostgreSQL and pgvector remain the CI database baseline.
- The existing Alembic migration chain is the source of truth for schema creation.
- Existing Playwright tests use route interception or local test doubles and do not require live API
  keys.
- Branch protection is configured separately in GitHub repository settings and is outside this
  feature's repository-controlled files.
