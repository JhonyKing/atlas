# Feature Specification: Expanded Curated Corpus and Ingestion Governance

**Feature Branch**: `005-expanded-curated-corpus`

**Created**: 2026-08-06

**Status**: Draft

**Input**: PRD v1.1 requirements ING-001 through ING-015 for expanding the curated technical
corpus while preserving allowlists, provenance, legal review, freshness, and safe source disablement.

## User Scenarios & Testing

### User Story 1 - Discover approved technical sources (Priority: P1)

As a researcher, I want ATLAS to maintain a broad catalog of authoritative framework, model,
release, and paper sources, so answers can use current technical evidence without accepting arbitrary
web content.

**Why this priority**: The corpus is the evidence foundation for every answer, comparison, and report.

**Independent Test**: Inspect the catalog and run a dry refresh; every enabled source is in an
approved collection, has an owner and policy status, and produces bounded fetch candidates.

**Acceptance Scenarios**:

1. **Given** an approved collection, **When** a refresh is planned, **Then** only its declared
   official domains, APIs, sitemaps, or release feeds are candidates.
2. **Given** an unsupported or unapproved URL, **When** discovery encounters it, **Then** ATLAS
   rejects it before fetching and records a safe disabled reason.
3. **Given** the initial catalog, **When** an operator lists enabled collections, **Then** it covers
   10–15 frameworks and 6–8 model providers with explicit source types.

### User Story 2 - Refresh and preserve source versions (Priority: P2)

As a corpus operator, I want scheduled refreshes to detect changes, preserve historical versions,
and expose freshness, so evidence remains reproducible and stale material is not silently treated as
current.

**Why this priority**: Current answers require deterministic capture dates, hashes, and version links.

**Independent Test**: Run a connector against deterministic fixtures containing unchanged, changed,
and removed pages; verify change detection, version relations, stale classification, and retry state.

**Acceptance Scenarios**:

1. **Given** a source with a 6–24 hour schedule, **When** its content changes, **Then** a new
   version is captured with a new hash and a relation to the previous version.
2. **Given** a failed fetch, **When** bounded retries are exhausted, **Then** the item enters a
   dead-letter state while the last good version remains available.
3. **Given** a source older than its freshness policy, **When** it is shown to researchers, **Then**
   its stale status and capture date are visible.

### User Story 3 - Ingest authorized private content safely (Priority: P3)

As an authenticated researcher, I want an authorized private-content connector, so my own material
can enrich private research without entering the public corpus or crossing tenant boundaries.

**Why this priority**: Feature 004 established ownership and quarantine; this story reuses that
boundary for governed ingestion.

**Independent Test**: Submit an authorized private source, verify tenant ownership and normalization,
then attempt access as another user and verify safe denial and no public-corpus record.

**Acceptance Scenarios**:

1. **Given** an authenticated owner grants access to private content, **When** ingestion runs,
   **Then** the content is stored under that owner with the same provenance and retention controls.
2. **Given** another user requests the private source, **When** authorization is evaluated, **Then**
   ATLAS returns safe not-found semantics and emits no private metadata.
3. **Given** a private source is revoked, **When** its owner disables it, **Then** future retrieval
   excludes it while the audit record remains content-free.

### User Story 4 - Govern, review, and disable sources (Priority: P4)

As a corpus reviewer, I want legal/policy gates, coverage reporting, corrections, and atomic
takedown, so every enabled source is explainable and can be disabled safely.

**Why this priority**: A portfolio-grade corpus needs operational governance, not only fetch code.

**Independent Test**: Create sources with approved, pending-review, corrected, and disabled states;
verify the dashboard, policy gates, correction history, and atomic disablement.

**Acceptance Scenarios**:

1. **Given** a source without robots, terms-of-service, or license approval, **When** an operator
   tries to enable it, **Then** enablement is blocked with a review reason.
2. **Given** a takedown or correction request, **When** it is approved, **Then** the source and
   derived retrieval records are disabled atomically and the previous state is auditable.
3. **Given** the coverage dashboard, **When** an operator opens it, **Then** it shows collection
   coverage, freshness, disabled sources, retry/dead-letter counts, and the seven-day target.

## Edge Cases

- A feed returns a redirect outside the approved domain or an SSRF-sensitive private address.
- A page changes only its navigation or formatting while the meaningful content is unchanged.
- A release is deleted upstream after ATLAS captured it.
- A paper has multiple identifiers, a retraction, or conflicting metadata from two registries.
- A pricing page exposes regional or currency-specific values that cannot be normalized safely.
- A PDF contains tables, code blocks, scanned images, or malformed text extraction.
- A connector times out during a retry window or returns a partial response.
- A source is disabled while an answer or ingestion job is in progress.
- A private tenant attempts to reference a public source under a misleading ownership claim.
- A correction and takedown request arrive concurrently.

## Requirements

### Functional Requirements

- **FR-ING-001**: The system MUST maintain an approved catalog covering 10–15 frameworks and 6–8
  model providers, with each collection declaring source type, owner, policy state, and allowlist.
- **FR-ING-002**: The system MUST support official documentation, GitHub release/changelog, and
  OpenAlex/Semantic Scholar metadata connectors with canonical links to their upstream records.
- **FR-ING-003**: GitHub release/changelog collections MUST support a configurable refresh interval
  between 6 and 24 hours and record the last successful refresh.
- **FR-ING-004**: Pricing and model-list collections MUST capture effective dates, detect changes,
  and preserve prior snapshots rather than overwriting them.
- **FR-ING-005**: Authorized user-content collections MUST remain private to the owning tenant and
  MUST never be promoted to the public corpus by default.
- **FR-ING-006**: Discovery MUST use only approved domains, APIs, versioned pages, or sitemaps and
  MUST reject unapproved destinations, redirects, unsafe network targets, and unbounded fetches.
- **FR-ING-007**: Normalization MUST preserve headings, tables, code blocks, source identity, and
  enough structure to reconstruct the captured document.
- **FR-ING-008**: Every captured item MUST store canonical URL, title, author or organization,
  published/captured dates, license, content hash, connector, and update outcome.
- **FR-ING-009**: The system MUST relate versions, classify historical versus current material,
  and mark items stale according to collection-specific TTL policies.
- **FR-ING-010**: Robots, terms-of-service, license, and human approval gates MUST block enablement
  until the required review state is recorded.
- **FR-ING-011**: The system MUST support atomic source disablement, takedown, correction, and
  re-review workflows without deleting the audit history.
- **FR-ING-012**: Each connector MUST use bounded retries, dead-letter handling, preservation of the
  last good version, and an explicit re-review trigger after repeated failure.
- **FR-ING-013**: The system MUST expose coverage, freshness, disabled-state, retry, and dead-letter
  metrics per collection and for the corpus as a whole.
- **FR-ING-014**: Ingestion and source-state events MUST include request/run identifiers, outcome,
  latency, and safe error codes without secrets or private content.
- **FR-ING-015**: The system MUST provide deterministic fixtures and an operator quickstart for
  validating a full refresh and the seven-day operational target.

### Key Entities

- **Collection**: Approved source group with connector type, scope, owner, schedule, TTL, and policy state.
- **SourceRecord**: Canonical source identity, URL, metadata, license, current state, and connector outcome.
- **SourceVersion**: Immutable captured content hash, dates, normalized structure, and parent-version relation.
- **ConnectorRun**: Bounded execution with request/run IDs, schedule, status, retries, latency, and error code.
- **PolicyReview**: Robots, terms, license, approval, correction, takedown, and re-review decisions.
- **CoverageSnapshot**: Collection metrics for coverage, freshness, disabled sources, retries, and dead letters.

## Success Criteria

### Measurable Outcomes

- **SC-ING-001**: The enabled catalog contains 10–15 framework collections and 6–8 model-provider
  collections, each with an approved allowlist and policy state.
- **SC-ING-002**: At least 99% of scheduled GitHub refreshes complete or enter a visible retry/dead-
  letter state within the configured 6–24 hour window; no failed run silently replaces the last good version.
- **SC-ING-003**: 100% of captured records contain all required provenance fields and a verifiable content hash.
- **SC-ING-004**: 100% of discovery attempts outside an approved destination are rejected before network fetch.
- **SC-ING-005**: 95% of fixture documents preserve headings, tables, and code blocks after normalization.
- **SC-ING-006**: 100% of disabled or takedown sources are excluded from new retrieval results within one minute.
- **SC-ING-007**: The coverage dashboard reports freshness, disabled, retry, and dead-letter metrics for every collection.
- **SC-ING-008**: No automated test, log, trace, or public-corpus record contains private tenant content or secrets.

## Assumptions

- Initial connectors use deterministic local fixtures for tests; production credentials and provider quotas are configured separately.
- The public corpus remains allowlist-only; arbitrary web search is out of scope for this feature.
- Feature 004 private ownership and quarantine services are the authorization boundary for private content.
- A seven-day operational validation is represented by deterministic time-travel fixtures plus an operator-run checklist.
- Human review is required for legal/policy enablement and takedown decisions.
- English is canonical for engineering metadata; Spanish UI labels can be added without changing evidence identity.
