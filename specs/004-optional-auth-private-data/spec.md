# Feature Specification: Optional Authentication and Private Data

**Feature Branch**: `004-optional-auth-private-data`

**Created**: 2026-08-06

**Status**: Draft

**Input**: Product backlog requirements IDN-001 through IDN-009 for optional authentication,
sessions, uploads, ownership, and deletion while preserving the anonymous journey.

## User Scenarios & Testing

### User Story 1 - Sign in without losing anonymous work (Priority: P1)

As an ATLAS visitor, I want to optionally create an account and sign in, so I can continue using
the product anonymously or keep my own work across sessions without changing anonymous quota rules.

**Why this priority**: Authentication is the boundary required before private threads, uploads, or
saved reports can be safely introduced.

**Independent Test**: Use the application anonymously, sign in, renew a session, sign out, and
confirm that anonymous requests remain available while authenticated requests use only the signed-in
user's ownership boundary.

**Acceptance Scenarios**:

1. **Given** an anonymous visitor with a completed answer, comparison, or report, **When** the
   visitor signs in, **Then** the anonymous work remains available according to an explicit
   migration choice and the anonymous quota counter is not reset or duplicated.
2. **Given** a valid session, **When** the visitor refreshes the page or renews the session, **Then**
   the user remains authenticated without exposing tokens to client logs or generated artifacts.
3. **Given** an invalid, expired, or revoked session, **When** a protected resource is requested,
   **Then** ATLAS returns an unauthenticated response and does not reveal whether another user's
   resource exists.
4. **Given** an authenticated user, **When** the user signs out, **Then** the session is revoked
   and subsequent protected requests require authentication again.

### User Story 2 - Keep private research work under personal ownership (Priority: P2)

As an authenticated researcher, I want saved conversations, threads, run history, feedback, and
reports to belong only to me, so I can return to my work without exposing it to another visitor.

**Why this priority**: Ownership is the core value of authentication and must cover existing
research artifacts rather than only new profile data.

**Independent Test**: Create a private thread and report as User A, verify User A can list and read
them, verify User B receives not-found semantics, then delete the data and confirm it is no longer
available.

**Acceptance Scenarios**:

1. **Given** an authenticated user creates a thread, saved answer, comparison, or report, **When**
   the user returns later, **Then** the item appears in that user's history with locale preference
   and lifecycle status.
2. **Given** User A owns a private item, **When** User B requests, downloads, edits, or deletes it,
   **Then** ATLAS returns safe not-found semantics without leaking identifiers or metadata.
3. **Given** a user changes locale preference, **When** the user starts a new session, **Then** the
   preference is applied to presentation while evidence identity remains unchanged.
4. **Given** a report or artifact reaches expiration or deletion, **When** the owner requests it,
   **Then** it remains unavailable and storage details are not disclosed.

### User Story 3 - Upload private source material safely (Priority: P3)

As an authenticated researcher, I want to upload private documents for my own research, so I can
use ATLAS with material that is not part of the public curated corpus.

**Why this priority**: Uploads expand the portfolio story, but they must follow the ownership and
security boundary established by the first two stories.

**Independent Test**: Upload an allowed document as User A, verify it is visible only to User A,
reject unsupported, oversized, malformed, or unsafe files, and delete the upload with an auditable
result.

**Acceptance Scenarios**:

1. **Given** an authenticated user selects an allowed file within the configured size limit, **When**
   the upload completes, **Then** the file is associated with that user, receives provenance and
   retention metadata, and is not added to the public corpus automatically.
2. **Given** a file has an unsupported type, invalid signature, excessive size, malware verdict, or
   parsing failure, **When** it is uploaded, **Then** ATLAS rejects it before indexing and reports a
   controlled reason without persisting unsafe content.
3. **Given** User A owns an upload, **When** User B attempts to read, retrieve, or delete it,
   **Then** the request fails with safe not-found semantics.
4. **Given** an owner requests account or upload deletion, **When** deletion completes, **Then** the
   private file, derived chunks, embeddings, reports, and ownership metadata are removed or marked
   irreversibly deleted according to the retention policy, with an audit record containing no raw
   file contents.

## Edge Cases

- Anonymous work cannot be safely migrated because ownership or consent is ambiguous.
- A user signs in from two browsers while one session is revoked.
- Session renewal races with logout or account deletion.
- A report is being downloaded while its owner deletes the account.
- A private upload has duplicate content, an encrypted archive, a macro, or a misleading extension.
- Malware scanning or parsing times out after the upload bytes were received.
- A database policy denies access even though the application layer has a valid user ID.
- A user requests deletion twice or retries after a partial deletion.
- Anonymous and authenticated quotas are requested in the same rolling window.

## Requirements

### Functional Requirements

- **FR-IDN-001**: The system MUST support optional authentication; anonymous cited-answer and
  comparison journeys MUST continue to work without an account.
- **FR-IDN-002**: The system MUST provide login, logout, session renewal, revocation, and a safe
  unauthenticated response without exposing session tokens in browser logs, prompts, traces, or
  generated artifacts.
- **FR-IDN-003**: The system MUST preserve anonymous quota semantics when an anonymous visitor signs
  in; migration of existing work MUST be explicit, consent-aware, and repeat-safe.
- **FR-IDN-004**: The system MUST associate threads, saved conversations, run history, feedback,
  reports, artifacts, and locale preferences with an authenticated user ownership boundary.
- **FR-IDN-005**: The system MUST enforce ownership in both application authorization and the
  persistence boundary; cross-user reads, updates, downloads, and deletes MUST return safe not-found
  semantics.
- **FR-IDN-006**: The system MUST allow authenticated users to create, list, inspect, and delete
  private uploads without automatically promoting them into the public corpus.
- **FR-IDN-007**: The system MUST validate upload size, declared and detected type, file signature,
  malware status, parsing result, and retention policy before indexing or embedding.
- **FR-IDN-008**: The system MUST provide repeat-safe account, upload, thread, report, and derived
  data deletion with an auditable result that contains no raw private content.
- **FR-IDN-009**: The system MUST keep provider keys, raw session tokens, raw visitor identifiers,
  private file contents, and cross-tenant metadata out of client bundles, prompts, logs, and traces.
- **FR-IDN-010**: The system MUST record request ID, authenticated subject, ownership decision,
  session event, upload scan outcome, deletion outcome, and latency without recording secrets or
  private content.

## Success Criteria

- **SC-IDN-001**: Anonymous users can complete the existing cited-answer and comparison journeys
  with no authentication prompt in 100% of regression journeys.
- **SC-IDN-002**: At least 99% of valid login, logout, and session-renewal journeys reach the
  expected terminal state in under 3 seconds in the supported portfolio workload.
- **SC-IDN-003**: 100% of cross-user access tests for threads, reports, artifacts, uploads, and
  feedback return safe not-found semantics and disclose no private metadata.
- **SC-IDN-004**: 100% of accepted private uploads have an ownership record, scan result, content
  hash, retention deadline, and provenance record before indexing.
- **SC-IDN-005**: 100% of rejected unsafe uploads create no searchable chunks, embeddings, or public
  corpus records.
- **SC-IDN-006**: Repeated deletion requests are idempotent, and 100% of deletion tests confirm
  that protected data is no longer retrievable after the terminal deletion state.
- **SC-IDN-007**: No automated test or trace contains a raw session token, provider key, raw visitor
  identifier, or private upload excerpt.

## Key Entities

- **User**: Authenticated subject and profile preferences.
- **Session**: Revocable authenticated session with expiry and audit events.
- **OwnershipGrant**: Explicit link between a user and a thread, run, report, artifact, feedback
  item, or upload.
- **PrivateUpload**: User-owned file metadata, hash, scan state, provenance, retention, and delete
  state; never a public corpus record by default.
- **DeletionJob**: Repeat-safe deletion request covering derived chunks, embeddings, artifacts, and
  audit outcome.

## Assumptions

- Authentication is optional and uses a provider adapter with secure, http-only session handling;
  the implementation plan will compare the existing Supabase-compatible PostgreSQL boundary with a
  custom session service before choosing one.
- The first slice supports one email/OAuth sign-in path, one user locale preference, and a bounded
  private upload type/size allowlist; social-provider breadth is deferred.
- Existing anonymous identity remains the source of anonymous quota accounting. Automatic migration
  of anonymous work is disabled unless the user explicitly consents and ownership can be proven.
- Private uploads have a separate retention policy and are excluded from the public corpus until a
  later ingestion-governance feature approves promotion.
- Human review remains required for malware-scanner and account-deletion provider configuration;
  automated tests cannot replace provider-level security review.

