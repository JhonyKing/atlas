# Feature status matrix

This matrix separates implementation evidence from the external or operational evidence required
by each feature's Definition of Done. A feature is not marked closed while any mandatory SpecKit
task remains open.

| Feature | Implementation complete | Tests executed | Evidence still pending | Definition of Done |
|---|---|---|---|---|
| 001 — Cited answer | MVP code, bilingual UX, corpus lifecycle, answer/evidence contracts, observability and retention are implemented. | Backend, contract, database, frontend and deterministic evaluation suites have recorded passing results in the feature artifacts. | T074 five-person usability study; T075 seven-day refresh validation; T076 complete quickstart; T077 README evidence update; T087 consolidated evidence record. | **Not met** — 5 mandatory tasks open. |
| 002 — Technology comparator | Comparison schemas, criteria normalization, quotas, deterministic executor, SSE lifecycle, bilingual UI and 20-request dataset are implemented. | Backend comparison suite, migration/SQL contracts, deterministic matrix cases and browser journeys have recorded passing results. | T032 verified fourth-corpus case; T038 live run against populated verified snapshot; T039 verified Anthropic collection; T040 live citation precision and latency measurements. | **Not met** — 4 mandatory tasks open. |
| 004 — Optional auth/private data | Provider-neutral sessions, anonymous continuity, ownership guards plus PostgreSQL RLS, quarantine uploads, account/upload/resource deletion, locale preference and redacted LangSmith traces are implemented. | Backend **225 passed, 4 skipped**, auth/private targeted suites, latency regression, four SQL contracts, frontend lint/typecheck, and **18 Playwright tests passed**; evidence is recorded in `docs/verification/004-auth-private-data.md`. | No open tasks in `specs/004-optional-auth-private-data/tasks.md`; production Supabase adapter and external provider review remain deployment work, not this local slice. | **Met** — 0 mandatory tasks open. |

## Branch mapping

- Stable Feature 003 branch: `codex/release-feature-003`, based on `a2cfed8` plus the artifact-evidence commit.
- Feature 004 branch: `codex/004-optional-auth-private-data`, based on `a2cfed8` plus only its seven feature commits.
- Legacy omnibus branch retained unchanged for rollback: `codex/001-cited-answer`.
