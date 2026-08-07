# Tasks: Security, Privacy, and Governance Hardening

## Phase 1: Threat contracts and tests

- [X] T001 Create security unit, integration and threat-test directories.
- [X] T002 Add synthetic SSRF, redirect, source injection, tool, code-execution and tenancy fixtures.
- [X] T003 Add `scripts/verify-security.ps1`, `pnpm test:security` and CI security gate.
- [X] T004 Add failing tests for URL validation, redirects, source/tool injection and generated code.
- [X] T005 Add failing tests for secrets, redaction, PII, ownership, RLS, retention and deletion.
- [ ] T006 Add failing tests for limits, challenge boundary, audit events and consent.

## Phase 2: Security boundaries (P1)

- [X] T007 Implement resolved-IP SSRF and redirect validation in ingestion source policy.
- [X] T008 Implement inert-source/tool/code-execution guardrails.
- [X] T009 Implement centralized redaction, PII-safe traces and audit event contracts.
- [X] T010 Integrate ownership/RLS, upload quarantine, retention/tombstones and deletion checks.
- [ ] T011 Implement consent/no-training policy and bilingual privacy/deletion responses.

## Phase 3: Abuse and governance (P2)

- [X] T012 Implement provider-independent IP/visitor/user rate-limit and challenge policy.
- [X] T013 Add frontend secret scan and CI security regression workflow.
- [ ] T014 Add security finding/external-review tracking artifact without claiming review completion.

## Phase 4: Verification and closure

- [ ] T015 Run targeted/full backend, frontend, SQL, Ruff/mypy and security gate; record evidence.
- [ ] T016 Update README, architecture, ADR, PRD/status matrix and privacy docs.
- [ ] T017 Run SpecKit Analyze/Converge; close only with zero mandatory tasks.

## Requirements Traceability

| Requirement | Tasks | Verification |
|---|---|---|
| FR-SEC-001..002 | T002, T004, T007..T008 | threat suite |
| FR-SEC-003..004 | T005, T010 | ownership/upload/retention suite |
| FR-SEC-005..006 | T003, T006, T012..T013 | secret/rate-limit/CI checks |
| FR-SEC-007..010 | T005..T006, T009, T011 | redaction/audit/privacy tests |
| FR-SEC-011..012 | T003, T013..T017 | CI and review evidence |
