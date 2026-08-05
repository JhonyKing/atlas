# ATLAS AI: cited-answer architecture

Status: implemented vertical slice, portfolio launch baseline  
Feature: `specs/001-cited-answer/`  
Last reviewed: 2026-08-04

## Purpose and boundaries

ATLAS answers one technical question at a time from a versioned, allowlisted corpus. It emits
progress first and claims/citations only in a terminal verified event. This feature deliberately
does not include live web search, user accounts, generated reports, or durable conversation memory;
the public cited-answer journey is available in en-US and es-MX, while source excerpts preserve
their original language. High-stakes advice is out of scope.

## Runtime topology

```mermaid
flowchart LR
  visitor["Anonymous visitor"] --> web["Next.js evidence UI"]
  web --> api["FastAPI API"]
  api --> identity["HMAC visitor identity"]
  identity --> quota["10 / 24h quota"]
  quota --> service["Answer run service"]
  service --> graph["LangGraph cited-answer graph"]
  graph --> retrieval["Hybrid retrieval"]
  retrieval --> postgres[("PostgreSQL + pgvector")]
  graph --> provider["OpenAI Responses adapter\ngpt-5.6-luna · medium"]
  provider --> verify["Deterministic verifier"]
  verify --> service
  service --> sse["SSE terminal event"]
  sse --> web
  worker["Operator / scheduled worker"] --> ingest["Allowlisted ingestion"]
  ingest --> postgres
  retention["Daily retention job"] --> purge["Bounded purge function"]
  purge --> postgres
```

## Answer graph and safe publication

1. The API validates one question, derives an HMAC visitor key, and reserves quota atomically.
2. Retrieval selects an immutable corpus snapshot, runs keyword and exact-vector search, fuses and
   deduplicates candidates, and applies product/version/date constraints.
3. The provider receives source excerpts inside explicit untrusted-evidence boundaries. It has no
   source-selection or action tools. The resolved model is exactly `gpt-5.6-luna`.
4. The verifier checks evidence IDs, claim coverage, temporal metadata, and contradiction paths.
   Unsupported claims are removed; a principal unsupported/contradicted result becomes
   `answer.abstained`.
5. Only `answer.completed` or `answer.abstained` contains the terminal result. Progress events do
   not expose drafts, excerpts, prompts, or model reasoning.
6. The web client renders source identity, publisher, canonical/revision links, excerpt, capture
   date, version, limitations, partial status, abstention explanation, and feedback controls.

## Data flow and storage

| Flow | System of record | Retention / integrity rule |
|---|---|---|
| Corpus discovery and promotion | `collections`, `sources`, `source_versions`, `chunks`, `corpus_snapshots` | Immutable versions; failed refresh preserves the active version |
| Answer interaction | `answer_runs`, `run_evidence`, `answer_claims`, `answer_citations` | Expires after 30 days; same-run composite foreign keys |
| Feedback | `feedback` | One replaceable visitor/run row; expires with its run |
| Quota | `usage_events` | HMAC visitor hash only; no question text |
| Quality operations | `daily_metrics` | Non-reversible aggregates with no visitor/run/question dimensions |
| Expired lookup | `answer_run_tombstones` | Run ID and timestamps only; supports controlled retention-expired behavior |

## Privacy and threat model

| Threat | Boundary / mitigation | Residual limitation |
|---|---|---|
| Prompt injection in source text | Escaped untrusted-evidence blocks, no source/action tools, deterministic abstention tests | A model can still misunderstand benign evidence; verification remains mandatory |
| Visitor correlation | Secure opaque cookie and server-side HMAC digest; raw cookie is never persisted or sent to the model | A deployment operator can still observe ordinary network metadata |
| SSRF or hostile redirects | HTTPS host/path allowlists, redirect re-validation, content-size/type limits | Allowlist review is required before enabling a connector |
| Fabricated citations | Evidence IDs and same-run composite FKs; terminal verifier rejects unknown or uncovered citations | Source correctness depends on the approved corpus |
| Retention failure | Batch `FOR UPDATE SKIP LOCKED`, aggregate-before-delete transaction, tombstones, idempotent retry | A scheduler outage delays deletion until the next successful run |
| Unauthorized operations | Operator routes use bearer token; public answer path has no action tools | Operator token rotation remains a deployment responsibility |

## Measured trade-offs

- Exact cosine search is the recall reference and avoids premature HNSW complexity; reranking and
  query rewriting remain deferred until measured latency or corpus scale requires them.
- `gpt-5.6-luna` at medium reasoning is the portfolio baseline; provider telemetry records model,
  prompt/retrieval/embedding versions, token classes, latency, and estimated cost.
- Local PostgreSQL uses host port `55432` because Windows PostgreSQL commonly occupies `5432`.
  Production should use managed PostgreSQL with `pgvector`, `pgmq`, and `pg_cron` when available.
- Evidence UI and SSE integration: 6/6 Playwright journeys passed. Backend regression: 102/102
  tests passed before the three launch smoke checks; retention integration: 1/1 and all 7 SQL
  contracts passed. The deterministic evaluation fixture reports 46/46, but that is a contract
  check, not a claim about model quality.
- Vitest/jsdom is currently blocked on the local Node 20 machine by an `ERR_REQUIRE_ESM` dependency
  mismatch; CI pins Node 24. TypeScript, ESLint, Playwright, pytest, ruff, and mypy remain green.

## Contract map

- Public HTTP and `CorpusStatus`: [`specs/001-cited-answer/contracts/openapi.yaml`](../../specs/001-cited-answer/contracts/openapi.yaml)
- SSE ordering and terminal behavior: [`specs/001-cited-answer/contracts/answer-events.md`](../../specs/001-cited-answer/contracts/answer-events.md)
- Data lifecycle: [`specs/001-cited-answer/data-model.md`](../../specs/001-cited-answer/data-model.md)
- Offline benchmark: [`evals/datasets/cited-answer-v1.jsonl`](../../evals/datasets/cited-answer-v1.jsonl)
