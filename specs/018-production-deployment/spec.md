# Feature Specification: Production Deployment

**Feature Branch**: `018-production-deployment`

**Created**: 2026-08-07

**Status**: Implementation foundation in progress; hosted beta evidence pending

**Input**: Product requirements for taking ATLAS from local development to a verifiable beta deployment using Vercel for the web application, Supabase for managed data/auth/storage, and a managed container runtime for the API and worker.

## User Scenarios & Testing

### User Story 1 - Open the beta web application (Priority: P1)

As a portfolio reviewer, I want to open a stable public ATLAS URL and use the same Spanish and English research flows that work locally, so I can evaluate the product without installing Docker.

**Why this priority**: A publicly reachable, reproducible product is required for the portfolio and is the first externally observable deployment outcome.

**Independent Test**: Open the production URL from a clean browser session, switch between `es-MX` and `en-US`, inspect the corpus status, submit one cited-answer question, and verify that the result or an evidence-based abstention is rendered.

**Acceptance Scenarios**:

1. **Given** a clean browser with no local environment, **When** the reviewer opens the production URL, **Then** the web application loads over HTTPS and displays the ATLAS landing flow without a localhost dependency.
2. **Given** the Spanish locale is selected, **When** the reviewer navigates through answer, comparison, reports, corpus, news, and private-data controls, **Then** visible labels and error states are Spanish and links remain on the deployed origin.
3. **Given** a preview deployment, **When** the reviewer opens it, **Then** it uses preview configuration and cannot read production secrets or production private data.

### User Story 2 - Run the API against managed production data (Priority: P1)

As an operator, I want the API, ingestion worker, migrations, and scheduled jobs to use a managed Supabase project, so production data survives local-machine shutdown and is protected by explicit access policies.

**Why this priority**: The current database is local Docker PostgreSQL. A beta deployment is not real until persistence, authentication, vector search, retention, and private-data boundaries work outside the developer machine.

**Independent Test**: Provision an isolated Supabase project, apply the versioned migrations to an empty database, load a small approved corpus, run health/readiness checks, and execute answer, comparison, report, news, auth, upload, and deletion smoke tests using non-local API credentials.

**Acceptance Scenarios**:

1. **Given** an empty production database, **When** the release migration command runs, **Then** the complete migration chain reaches its head and the required vector, provenance, retention, news, report, review, and private-data structures exist.
2. **Given** a production API request, **When** it reads public corpus data, **Then** it uses the managed database and returns evidence metadata with no local file or localhost fallback.
3. **Given** an authenticated user, **When** the user uploads, lists, and deletes private resources, **Then** ownership and row-level policies prevent access by another user and deletion is repeat-safe.

### User Story 3 - Release safely through CI/CD (Priority: P1)

As a maintainer, I want a merge or release to pass automated gates before changing beta traffic, so deployment failures, migration drift, leaked secrets, citation regressions, and unavailable dependencies are detected before users see them.

**Why this priority**: Deployment is a production change, not a manual copy operation. The portfolio needs evidence of controlled releases, not only a URL.

**Independent Test**: Open a pull request that intentionally breaks a contract, migration, build, secret scan, or smoke test and verify that the release is blocked; then run a valid release and inspect its immutable artifacts and health checks.

**Acceptance Scenarios**:

1. **Given** a pull request, **When** required checks run, **Then** static checks, unit/integration tests, database migration validation, browser tests, deterministic evaluation gates, and deployment configuration validation must pass before merge.
2. **Given** a production release, **When** the web and API deploy, **Then** migrations run in an explicit, auditable step before traffic is declared healthy; a failed migration stops the release.
3. **Given** a failed release or unhealthy deployment, **When** the rollback runbook is followed, **Then** the previous application version remains recoverable without deleting evidence or silently changing the schema.

### User Story 4 - Observe and operate the beta (Priority: P2)

As an operator, I want traces, structured logs, cost/latency signals, backups, alerts, and runbooks for the deployed system, so I can diagnose a failed answer and prove the beta's reliability.

**Why this priority**: ATLAS is evidence-first and already instruments LangSmith-oriented traces. Production observability must preserve that evidence while redacting secrets and private content.

**Independent Test**: Trigger a successful answer, an abstention, a provider failure, a private-data denial, and a slow request in the beta environment; verify trace correlation, redaction, alerts, and the documented response procedure.

**Acceptance Scenarios**:

1. **Given** a request with a correlation ID, **When** it crosses the web, API, retrieval, model, verification, and persistence boundaries, **Then** the operator can follow one redacted trace without seeing API keys, session tokens, or private document contents.
2. **Given** an availability, latency, error-rate, cost, or citation-quality threshold breach, **When** the monitoring window evaluates, **Then** an alert is emitted with a link to the relevant runbook.
3. **Given** a beta data store, **When** the backup and restore check runs, **Then** the operator can restore a documented snapshot in a separate environment and verify corpus and private-data boundaries.

## Edge Cases

- Vercel must not receive server-only API keys, database passwords, Supabase service-role keys, or LangSmith tokens in browser bundles.
- A preview deployment must not point at production private data by default.
- A migration that is not backward-compatible with the currently running API must fail the release or use an explicitly documented expand/contract sequence.
- Supabase is unavailable, has stale credentials, or returns a connection-pool exhaustion error; the API must report a truthful readiness failure and avoid claiming a verified answer.
- A provider request times out after a deployment; the trace must remain correlated and the user must receive the existing abstention/error contract.
- A scheduled news or retention job runs twice; it must be idempotent and must not duplicate evidence or delete another user's data.
- The deployed API is reachable but the configured CORS origin, callback URL, or public API origin is wrong; the smoke test must fail with an actionable diagnostic.
- A production deploy is rolled back while a migration is already applied; the rollback procedure must be compatible with the schema state and must not use destructive down-migrations automatically.
- Vercel build, managed API build, or worker startup fails; the old healthy version must remain serving traffic when the platform supports it.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST provide a public HTTPS web deployment for the Next.js application on Vercel with separate preview and production configuration.
- **FR-002**: The production web deployment MUST call a configured HTTPS API origin and MUST never require `localhost` at runtime.
- **FR-003**: The system MUST provide a separately deployable API and ingestion-worker runtime suitable for long-running FastAPI requests, background jobs, scheduled retention/news work, and LangSmith traces; the API/worker runtime MUST NOT depend on Vercel function limits.
- **FR-004**: Production persistence MUST use a dedicated Supabase project with PostgreSQL, pgvector, authentication, storage, row-level security, and connection pooling configured for the ATLAS data model.
- **FR-005**: Versioned migrations MUST be the source of truth, MUST run against a fresh production-like database in CI, and MUST run through an explicit release step before an application version is declared healthy.
- **FR-006**: The deployment MUST keep public, authenticated, and private data boundaries equivalent to the existing domain contracts; production credentials MUST be least-privilege and environment-scoped.
- **FR-007**: Preview, staging, and production environments MUST have distinct URLs, secrets, database targets, auth redirect URLs, CORS allowlists, and LangSmith project/tags.
- **FR-008**: The release pipeline MUST execute required checks for lint, typecheck, unit/integration tests, migrations/contracts, browser journeys, deterministic RAG evaluation, security/secret scanning, and deployment smoke tests before promoting traffic.
- **FR-009**: The release pipeline MUST publish immutable build identifiers, migration revision, corpus snapshot/version, model-router configuration, locale configuration, and evaluation summary as deployment evidence.
- **FR-010**: A release MUST expose `/healthz` and a readiness check that reports database/provider dependencies truthfully; a successful web build alone MUST NOT count as a healthy ATLAS deployment.
- **FR-011**: Production observability MUST emit correlated structured logs and LangSmith/OpenTelemetry traces for answer, comparison, report, news, ingestion, auth, and private-data flows with sensitive values redacted.
- **FR-012**: The deployment MUST define backups, restore verification, retention, alerts, incident response, rollback, and recovery time/recovery point targets in operator documentation.
- **FR-013**: The production smoke suite MUST prove Spanish and English UI paths, cited-answer verification/abstention, comparator evidence mapping, report artifact creation, previous-day news behavior, anonymous quota behavior, authenticated ownership, and private-resource deletion.
- **FR-014**: The deployment MUST document any functionality that remains intentionally disabled in beta and MUST fail closed rather than silently falling back to local fixtures or fake providers.
- **FR-015**: The feature MUST NOT claim that ATLAS is deployed, publicly reachable, or using Supabase until a real environment passes the smoke evidence checklist with captured URLs, timestamps, revision IDs, and redacted logs.

### Key Entities

- **Deployment environment**: A named preview, staging, or production configuration with its own URLs, secrets, database target, auth redirects, and observability namespace.
- **Release evidence bundle**: Immutable metadata proving the source revision, build identifiers, migration head, corpus/model/locale versions, checks, smoke results, and health status.
- **Migration release**: The ordered schema change set applied to a managed database with compatibility and rollback notes.
- **Operational runbook**: A versioned procedure for deploy, rollback, backup/restore, incident response, and dependency failure.
- **Secret boundary**: The set of values allowed in server-only runtime configuration and the set explicitly prohibited from browser bundles, logs, traces, and artifacts.

## Success Criteria

### Measurable Outcomes

- **SC-001**: A clean reviewer can load the production web URL over HTTPS and complete the primary cited-answer flow in both supported locales without installing local dependencies.
- **SC-002**: A fresh production-like database reaches the migration head and passes all required SQL/API contracts in 100% of successful release candidates.
- **SC-003**: Every beta release has a recorded web URL, API URL, source revision, migration revision, corpus snapshot, model-router version, evaluation summary, health result, and timestamp.
- **SC-004**: No production secret, session token, private document content, or provider credential appears in the browser bundle or redacted deployment evidence across the release test suite.
- **SC-005**: A deliberately failing required check blocks promotion in 100% of tested release-gate runs.
- **SC-006**: The previous healthy application version can be restored using the documented rollback procedure without destructive automatic schema rollback.
- **SC-007**: The operator can correlate a successful request, abstention, provider error, and private-data denial to a redacted trace and structured log within five minutes.
- **SC-008**: Backup restore verification succeeds for a separate environment before the beta is declared operational.
- **SC-009**: The beta documents whether the PRD targets for 99.5% API availability, TTFT p50 below 1.5 seconds, normal p95 below 12 seconds, report completion below 3 minutes, uncontrolled errors below 1%, citation rate at least 95%, and cost budgets are measured, pending, or not yet met; no target is claimed without evidence.

## Scope Boundaries

- This feature defines and implements the production deployment path; it does not replace the existing local Docker development workflow.
- Vercel is the web hosting target. Supabase is the managed data/auth/storage target. The API and worker use a managed container runtime selected during implementation so long-running/background behavior is not forced into a web-function model.
- Provisioning accounts, domain ownership, billing, and production credentials are operator actions. Repository work may provide scripts, manifests, checks, and runbooks but must not invent credentials.
- A real beta deployment is a separate evidence milestone after repository implementation; local tests alone cannot close this feature.

## Assumptions

- The existing FastAPI API, ingestion worker, Alembic migration chain, Next.js web app, LangSmith instrumentation, and CI checks remain the domain source of truth.
- Supabase-compatible local PostgreSQL remains available for offline development and CI; production configuration is selected through environment variables and secret management.
- The API/worker hosting provider can run a container image, expose HTTPS, execute health checks, provide logs, and support a controlled release/rollback workflow.
- Vercel preview builds are allowed to use a non-production API/database target.
- The operator will supply Vercel, Supabase, domain, managed-container, model-provider, and LangSmith credentials when the implementation reaches the deployment-environment tasks.
- Beta launch may start with a small approved corpus and bounded traffic, but it must expose corpus freshness and incomplete coverage instead of presenting fixtures as live research.
