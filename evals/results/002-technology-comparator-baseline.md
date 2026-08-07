# Technology comparator baseline

Date: 2026-08-05
Mode: local deterministic/fixture validation

## Gates

| Gate | Result |
|---|---|
| Backend pytest (`apps/backend/tests`) | 178 passed, 4 skipped |
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
- The four-technology fixture and journey now use Anthropic. The verified corpus contains five
  ready collections and 20 official sources; Anthropic and Gemini were ingested after review.
- The runtime comparison endpoint is wired with quota, snapshot selection, persistence and a
  fail-closed executor; a live Spanish four-technology run completed against the promoted snapshot
  `660b0578-992f-43d2-9722-fa0c49568bbd`.

## Latest convergence check (2026-08-05)

- Backend suite: **178 passed, 4 skipped**.
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

## Latest real-corpus validation (2026-08-06)

- Promoted snapshot: `660b0578-992f-43d2-9722-fa0c49568bbd`.
- Five collections ready; 20 official sources, 20 pages and 4,220 chunks in total.
- Anthropic: 4 sources / 677 chunks. Gemini: 4 sources / 898 chunks.
- Live Spanish four-technology comparison completed all SSE stages against the promoted snapshot.

## Retrieval and refresh validation (2026-08-06)

- Retrieval ablations cover hybrid `k=4/8/10`, reranking and the anti-hallucination policy flag;
  deterministic ground-truth metrics are repeatable at 1.0 for the 11 cases with IDs.
- Failed-refresh safety validation day 1 preserved the promoted snapshot ID. Days 2-7 remain
  scheduled work for the seven-day acceptance criterion.
- T040 live measurement: a Spanish four-technology / three-criterion run completed 12 cells in
  **76,712 ms** with HTTP 200 and no failed SSE event. Offline citation precision remains **1.0**;
  live citation precision is intentionally unreported until real-source ground-truth IDs are
  manually reviewed (`evals/results/live-comparator-t040.json`).
- Follow-up live run on 2026-08-07 completed the same 12 cells in **68,751 ms** with HTTP 200 and
  no failed SSE event. Its cell-level evidence IDs are preserved in
  `evals/results/live-comparator-t040-20260807.json`; citation precision remains pending manual
  ground-truth review.
