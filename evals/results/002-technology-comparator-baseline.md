# Technology comparator baseline

Date: 2026-08-05
Mode: local deterministic/fixture validation

## Gates

| Gate | Result |
|---|---|
| Backend pytest (`apps/backend/tests`) | 177 passed, 4 skipped |
| Alembic migration (`upgrade head`) | Passed through `0015_expand_corpus_collections` |
| Comparison offline evaluator | 17/17 matrix cases passed; structure 1.0, states 1.0, evidence parity 1.0 |
| Frontend ESLint | Passed |
| Frontend TypeScript | Passed |
| Frontend Playwright | 12 passed |

## Notes

- LangSmith configuration and live smoke tracing were verified separately in project `atlas-ai`.
- The full online 60-case LangSmith evaluation is intentionally not run in this baseline because it
  sends provider requests and may incur cost.
- Vitest's regular sandboxed Node 20 launcher fails before test collection because of Windows path
  permissions; the approved bundled Node 24 runtime passes all 20 component tests.
- The four-technology fixture and journey now use Anthropic. The current verified corpus still
  contains only LangGraph, LangChain and OpenAI; Anthropic remains pending source review and ingest.
- The runtime comparison endpoint is now wired with quota, snapshot selection, persistence and a
  fail-closed executor; the runtime now includes a development-only deterministic executor and a
  verified-corpus OpenAI embedding/retrieval/structured-extraction executor. A live run against a
  populated production snapshot remains a convergence check.

## Latest convergence check (2026-08-05)

- Backend suite: **177 passed, 4 skipped**.
- Runtime smoke with `use_real_provider=False`: terminal `comparison.completed` SSE with a safe
  development-only matrix; no unverified production claim is implied.
- New unit coverage verifies extraction evidence allow-listing, executor wiring, and persisted
  terminal matrix state.
- Offline comparator dataset: **20 requests / 17 matrix cases**, all deterministic cases passing
  with matrix structure, state accuracy and evidence-ID parity at **1.0**. Live citation precision
  and latency measurements remain opt-in until a populated verified corpus is available.
- Vitest locale/component suite: **8 files, 20 tests passed** with the bundled Node 24 runtime.
  The regular sandboxed Node 20 launcher is blocked by Windows path permissions before test
  collection; this does not reproduce when the approved bundled runtime is used.
- Live local API smoke after restarting the backend: `/healthz` returned **200** and a two-technology
  `/v1/comparisons` request emitted accepted → retrieval → normalization → verification → completed
  SSE events with a development-only matrix.
- Four-technology Chromium journey: **1 passed**, including English/Spanish rendering and keyboard
  selection; full Playwright baseline is now **12 passed**.
