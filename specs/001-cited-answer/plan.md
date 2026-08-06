# Implementation Plan: Verifiable Cited Answer

**Branch**: `codex/001-cited-answer` | **Date**: 2026-08-04 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-cited-answer/spec.md`

## Summary

Deliver the first public ATLAS vertical slice: an anonymous visitor asks a question about the
official LangGraph, LangChain, or OpenAI corpus and receives either a verified claim-level cited
answer or an explicit abstention. The implementation is a modular monolith with a Next.js web
client, an async FastAPI backend, a small explicit LangGraph workflow, Supabase PostgreSQL with
full-text and vector retrieval, and a Python ingestion worker sharing the backend package. OpenAI
Responses API uses `gpt-5.6-luna` behind an ATLAS adapter; all model output is structured and
validated before release.

## Technical Context

**Language/Version**: Python 3.13.x; TypeScript 5.x on Node.js 24 LTS; SQL on managed PostgreSQL

**Primary Dependencies**: FastAPI, Pydantic, LangGraph 1.2.x, official OpenAI Python SDK,
SQLAlchemy 2.x, psycopg 3, Alembic, pgvector, Next.js 16.2.x, React, OpenTelemetry

**Storage**: Supabase PostgreSQL with `pgvector`, `pg_cron`, and `pgmq`; local PostgreSQL/pgvector
container for development; immutable corpus versions and expiring interaction content

**Testing**: pytest, pytest-asyncio, Ruff, mypy, contract tests, PostgreSQL/pgTAP integration tests,
Vitest, Playwright, and versioned offline retrieval/citation/abstention evaluations

**Target Platform**: Linux containers for backend/worker, Node deployment for Next.js, current
evergreen desktop/mobile browsers, one public origin with private worker and database boundaries

**Project Type**: Web application monorepo implemented as a modular monolith with three runtime
entry points: web, API, and worker

**Performance Goals**: First useful progress within 1 second; verified answer visible within 5
seconds for at least 95% of normal questions and complete within 15 seconds; 95% citation precision;
90% correct abstention and temporal-answer targets from the feature spec

**Constraints**: Five catalogued official collections, with the initial three launch sources and
Anthropic/Gemini added only after source review; daily refresh plus manual operator trigger;
10 cited-answer questions per anonymous visitor per rolling 24 hours; 30-day content retention;
English-canonical content with `en-US`/`es-MX` public parity for this slice; no report generation,
uploads, accounts, saved conversations, or live-web research in this feature; model text is never
shown before citation validation

**Scale/Scope**: Portfolio launch, initially up to 1,000 monthly active visitors and five curated
collections; exact vector retrieval remains the recall ground truth and scale infrastructure is
added only after measured need

## Constitution Check

*GATE: Passed before Phase 0 research and re-checked after Phase 1 design.*

| Principle | Design Evidence | Status |
|-----------|-----------------|--------|
| Evidence Over Fluency | Immutable evidence IDs, claim-evidence links, deterministic citation gate, abstention paths, temporal evals | PASS |
| Spec Before Code | Approved spec and five recorded clarifications precede this plan; no source implementation exists | PASS |
| Test and Evaluate First | Tasks must begin with failing tests/evals; exact retrieval is baseline before HNSW/reranking | PASS |
| Explicit Contracts and Type Safety | Pydantic domain schemas, strict TypeScript, OpenAPI and SSE contracts, validated model output | PASS |
| Provider Independence | `AnswerGenerator` and `EmbeddingProvider` ports isolate OpenAI; model/effort/prices are versioned configuration | PASS |
| Security and Privacy | Allowlisted fetches, untrusted evidence boundary, pseudonymous visitor HMAC, 30-day purge, private admin/worker | PASS |
| Observable and Cost-Aware | Request IDs, token/cost fields, content-free spans, quota enforcement, global budget circuit breaker | PASS |
| Small Vertical Slices | One cited-answer journey; no microservices, persistent graph memory, general tool loop, reports, or auth | PASS |
| English-Canonical Engineering | Engineering identifiers and source contracts are English; public cited-answer UX has `en-US` and `es-MX` parity | PASS |

Post-design re-check: the Supabase queue is justified because daily ingestion is durable work that
must survive API restarts and preserve the previous corpus on failure. It reuses PostgreSQL rather
than adding Redis/Celery. No constitution exception is required.

## Architecture and Runtime Flow

### Public answer flow

```text
Next.js web
  -> FastAPI quota/idempotency gate
  -> LangGraph StateGraph
       validate_request
       retrieve_evidence
       evidence_gate --insufficient--> abstain
       compose_claims (GPT-5.6 Luna structured output)
       verify_citations --failed------> abstain
       finalize_answer
  -> verified SSE completion event
  -> PostgreSQL answer/claims/citations/metrics
```

Progress events announce stages, but claim text and citations are emitted only after validation.
Client disconnect cancels the async graph task. This one-shot feature does not use a durable
LangGraph checkpointer; domain runs and evidence are persisted directly. A future report/HITL
feature may add `AsyncPostgresSaver` with its own retention policy.

### Ingestion flow

```text
Supabase Cron or authenticated operator action
  -> enqueue idempotent collection refresh in PGMQ
  -> Python worker fetches allowlisted official source
  -> normalize and hash document
  -> insert immutable document version and chunks
  -> embed chunks
  -> atomic validation and promotion
  -> preserve previous active version on any failure
```

The first connectors consume official Markdown/LLM indexes and official repository release APIs
where available. HTML is a bounded fallback. Fetching validates scheme, host, redirect target,
resolved address, content type, and size before processing.

## Retrieval Baseline

1. Normalize the question and extract explicit product/version/date filters without an LLM.
2. Retrieve keyword candidates using an English `tsvector`, GIN, and `websearch_to_tsquery`.
3. Retrieve semantic candidates using `text-embedding-3-small` and exact cosine search.
4. Combine the two ranked lists with reciprocal-rank fusion and deduplicate by document section.
5. Filter by allowlisted collection, source type, active/historical version, and temporal constraint.
6. Return immutable evidence IDs and up to eight bounded evidence excerpts to the graph.

HNSW is deferred until corpus size or measured p95 latency requires it. Exact search remains the
recall reference. Reranking and LLM query rewriting are experiments, not baseline dependencies.

## OpenAI Baseline

- Model: exact slug `gpt-5.6-luna`; the `gpt-5.6` alias is prohibited because it routes to Sol.
- API: async official Python SDK with Responses API, `store=false`, no `previous_response_id`, and
  `reasoning.context="current_turn"`.
- Reasoning: `medium` baseline; compare `low` and `high` on the same eval set before changing.
- Output: `responses.parse` into an ATLAS Pydantic `AnswerDraft` with claims, evidence IDs, caveats,
  and answer/abstain status.
- Privacy: HMAC-derived `safety_identifier`; never send raw IP, cookie, or fingerprint.
- Caching: begin with implicit behavior; enable explicit stable-prefix caching only after telemetry
  proves reuse above the eligibility threshold.
- Telemetry: resolved model, prompt/retrieval versions, OpenAI response/request IDs, token classes,
  latency, retry count, cancellation, and price-table version.

## Project Structure

### Documentation (this feature)

```text
specs/001-cited-answer/
|-- spec.md
|-- plan.md
|-- research.md
|-- data-model.md
|-- quickstart.md
|-- checklists/
|   `-- requirements.md
|-- contracts/
|   |-- openapi.yaml
|   `-- answer-events.md
`-- tasks.md                 # generated by $speckit-tasks
```

### Source Code (repository root)

```text
apps/
|-- web/
|   |-- app/
|   |-- components/
|   |-- lib/
|   `-- tests/
`-- backend/
    |-- src/atlas/
    |   |-- api/
    |   |-- domain/
    |   |-- agent/
    |   |-- retrieval/
    |   |-- ingestion/
    |   |-- providers/
    |   |-- persistence/
    |   `-- observability/
    `-- tests/
        |-- unit/
        |-- contract/
        `-- integration/
database/
|-- migrations/
|-- functions/
`-- tests/
evals/
|-- datasets/
|-- evaluators/
`-- results/
infra/
|-- containers/
`-- deployment/
docs/
|-- adr/
|-- architecture/
|-- governance/
|   `-- source-reviews/
|-- research/
`-- runbooks/
```

**Structure Decision**: One Python package supplies both FastAPI and worker entry points. Retrieval,
ingestion, graph, providers, and persistence are modules rather than services. The web client is the
only separate language workspace. This keeps boundaries demonstrable without network hops or
duplicated contracts.

## Phase 0: Research Outcome

All technical unknowns were resolved in [research.md](./research.md). No unresolved clarification
markers remain. Exact dependency versions will be resolved and locked during scaffolding; supported
major/minor lines and runtime patches are recorded here.

## Phase 1: Design Outcome

- [data-model.md](./data-model.md) defines immutable corpus records, answer/evidence relationships,
  quota events, retention, and state transitions.
- [contracts/openapi.yaml](./contracts/openapi.yaml) defines the public and operator HTTP interface.
- [contracts/answer-events.md](./contracts/answer-events.md) defines verified SSE progress semantics.
- [quickstart.md](./quickstart.md) defines the end-to-end validation procedure.

## Complexity Tracking

No constitution violations require exceptions. The database-backed queue and worker are directly
required by the daily durable-ingestion acceptance criteria and reuse the selected system of record.
