# Feature Specification: Security, Privacy, and Governance Hardening

**Feature Branch**: `codex/009-security-privacy-governance`  
**Created**: 2026-08-06  
**Status**: Draft  
**Input**: PRD SEC-001 through SEC-012

## User Scenarios & Testing

### User Story 1 — Prevent unsafe actions and data exposure (P1)

As a visitor or authenticated user, I want requests, sources, tools, generated code, uploads and
private records isolated so that malicious input cannot trigger SSRF, unauthorized tools, code
execution or cross-tenant disclosure.

**Acceptance**: threat fixtures reject private-network URLs, unsafe redirects, source/tool
injection, generated-code execution, unauthorized resources, and oversized or invalid uploads.

### User Story 2 — Govern private data lifecycle (P1)

As a data owner, I want explicit consent, retention, deletion, tombstones and no-training policy
so that private documents are never promoted to public evidence and deletion is auditable.

**Acceptance**: ownership and RLS checks are enforced, deletion is repeat-safe, retention removes
content while retaining irreversible aggregates, and privacy notice is available in both locales.

### User Story 3 — Operate with accountable security evidence (P2)

As an operator, I want secret checks, rate limits, audit events, redacted traces and CI security
gates so that production readiness is demonstrated with evidence rather than assumptions.

**Acceptance**: secrets are rejected from frontend/build artifacts, abuse limits are bounded,
security tests run in CI, audit events exclude content, and external review findings are tracked.

## Functional Requirements

- **FR-SEC-001**: Source fetches MUST validate scheme, host, redirects and private-network targets.
- **FR-SEC-002**: Untrusted source text MUST NOT authorize tools, code execution, or policy changes.
- **FR-SEC-003**: Private entities MUST enforce tenant ownership and least-privilege access.
- **FR-SEC-004**: Uploads MUST be bounded by type, size, malware/quarantine state and retention.
- **FR-SEC-005**: Secrets MUST remain server-side and security checks MUST scan frontend artifacts.
- **FR-SEC-006**: IP, visitor and authenticated limits MUST have an abuse/challenge boundary.
- **FR-SEC-007**: Source, report, admin and sensitive-action changes MUST produce redacted audit events.
- **FR-SEC-008**: Privacy notice, consent and account/data deletion MUST be available in en-US/es-MX.
- **FR-SEC-009**: Private documents MUST be excluded from training and public corpus promotion.
- **FR-SEC-010**: Traces MUST redact prompts, excerpts, PII and secrets while retaining safe correlation IDs.
- **FR-SEC-011**: CI MUST run security regression checks and block on critical failures.
- **FR-SEC-012**: External security review findings MUST be recorded with owner, severity and resolution.

## Success Criteria

- **SC-SEC-001**: 100% of SSRF, redirect, injection, tool and code-execution fixtures are rejected.
- **SC-SEC-002**: 0 cross-tenant access cases pass authorization tests.
- **SC-SEC-003**: 100% of accepted audit/trace records contain no prompt, excerpt, secret or PII.
- **SC-SEC-004**: CI security gate fails deterministically when a critical fixture regresses.
- **SC-SEC-005**: Deletion and retention tests leave no recoverable private content after expiry.

## Edge Cases

- DNS resolves a permitted hostname to a private address; reject after resolution.
- Redirect chain changes host or scheme; validate every hop and reject unsafe targets.
- A source contains instructions that resemble tool calls; treat them as inert evidence.
- A deletion request is repeated or arrives after expiry; return the same safe terminal state.
- A trace exporter is unavailable; use a no-op path without logging content.
