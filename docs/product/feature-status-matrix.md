# Feature status matrix

This matrix separates implementation evidence from the external or operational evidence required
by each feature's Definition of Done. A feature is not marked closed while any mandatory SpecKit
task remains open.

| Feature | Implementation complete | Tests executed | Evidence still pending | Definition of Done |
|---|---|---|---|---|
| 001 — Cited answer | MVP code, bilingual UX, corpus lifecycle, answer/evidence contracts, observability and retention are implemented. | Backend, contract, database, frontend and deterministic evaluation suites have recorded passing results in the feature artifacts. | T074 five-person usability study; T075 seven-day refresh validation; T076 complete quickstart; T077 README evidence update; T087 consolidated evidence record. | **Not met** — 5 mandatory tasks open. |
| 002 — Technology comparator | Comparison schemas, criteria normalization, quotas, deterministic executor, SSE lifecycle, bilingual UI and 20-request dataset are implemented. | Backend comparison suite, migration/SQL contracts, deterministic matrix cases and browser journeys have recorded passing results. | T032 verified fourth-corpus case; T038 live run against populated verified snapshot; T039 verified Anthropic collection; T040 live citation precision and latency measurements. | **Not met** — 4 mandatory tasks open. |
| 003 — Reports | DOCX/PDF planning, rendering, validation, downloads, expiry/deletion, idempotency, bilingual parity and evidence-backed citations are implemented for the MVP vertical slice. | Backend, contract, SQL, Playwright, deterministic eval and visual-QA suites passed; final DOCX/PDF artifacts and SHA-256 manifest are stored under `evals/results/003-reports-artifacts/`. | No open tasks in `specs/003-reports/tasks.md`. Broader report catalog remains future scope, not an unclosed MVP task. | **Met for MVP vertical slice** — 0 mandatory tasks open. |

## Branch mapping

- Stable Feature 003 branch: `codex/release-feature-003`, based on `a2cfed8` plus the artifact-evidence commit.
- Feature 004 branch: `codex/004-optional-auth-private-data`, based on `a2cfed8` plus only its seven feature commits.
- Legacy omnibus branch retained unchanged for rollback: `codex/001-cited-answer`.
