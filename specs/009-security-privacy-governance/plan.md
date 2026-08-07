# Implementation Plan: Security, Privacy, and Governance Hardening

**Branch**: `codex/009-security-privacy-governance` | **Date**: 2026-08-06

## Architecture

1. Reuse and harden source URL validation and redirect policy in `atlas/ingestion`.
2. Add a central redaction and audit-event boundary in `atlas/security`.
3. Add secret scanning and security regression scripts under `scripts/` and `.github/workflows/`.
4. Keep private ownership/RLS, upload quarantine, retention and deletion contracts explicit.
5. Add rate-limit/challenge policy as a provider-independent port.

## Quality Gates

- threat tests before security code;
- no private content in logs/traces/audit events;
- full backend regression, Ruff/mypy and frontend secret scan;
- database SQL/RLS checks where applicable;
- external review remains a separately recorded operational gate.
