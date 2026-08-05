# Technology comparator baseline

Date: 2026-08-05
Mode: local deterministic/fixture validation

## Gates

| Gate | Result |
|---|---|
| Backend pytest (`apps/backend/tests`) | 168 passed, 4 skipped |
| Alembic migration (`upgrade head`) | Passed through `0014_comparison_cell_context` |
| Comparison offline evaluator | 2/2 cases passed; structure 1.0, states 1.0, evidence parity 1.0 |
| Frontend ESLint | Passed |
| Frontend TypeScript | Passed |
| Frontend Playwright | 11 passed |

## Notes

- LangSmith configuration and live smoke tracing were verified separately in project `atlas-ai`.
- The full online 60-case LangSmith evaluation is intentionally not run in this baseline because it
  sends provider requests and may incur cost.
- Vitest's current Windows resolver fails before test collection when resolving `vitest.config.ts`
  through the bundled runtime; lint, typecheck and Playwright remain green.
- Four-technology comparison cases remain open until a fourth corpus collection is approved and
  ingested. The current verified corpus contains LangGraph, LangChain and OpenAI.
- The runtime comparison endpoint is now wired with quota, snapshot selection, persistence and a
  fail-closed executor; the runtime now includes a development-only deterministic executor and a
  verified-corpus OpenAI embedding/retrieval/structured-extraction executor. A live run against a
  populated production snapshot remains a convergence check.

## Latest convergence check (2026-08-05)

- Backend suite: **174 passed, 4 skipped**.
- Runtime smoke with `use_real_provider=False`: terminal `comparison.completed` SSE with a safe
  development-only matrix; no unverified production claim is implied.
- New unit coverage verifies extraction evidence allow-listing, executor wiring, and persisted
  terminal matrix state.
- Offline comparator dataset: **20 requests / 16 matrix cases**, all deterministic cases passing
  with matrix structure, state accuracy and evidence-ID parity at **1.0**. Live citation precision
  and latency measurements remain opt-in until a populated verified corpus is available.
- Vitest locale/component suite: **8 files, 20 tests passed** with the bundled Node 24 runtime.
  The regular sandboxed Node 20 launcher is blocked by Windows path permissions before test
  collection; this does not reproduce when the approved bundled runtime is used.
