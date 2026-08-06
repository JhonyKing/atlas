# Implementation Plan: Evidence-Backed Technology Comparator

**Branch**: `codex/002-technology-comparator` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

## Summary

Add a bounded comparison workflow that retrieves evidence independently for two to four supported
technologies, normalizes values into explicit cell states, and returns a cited matrix in English or
Spanish. The workflow reuses the verified corpus, evidence contracts, anonymous identity, quota,
LangSmith tracing, and bilingual UI from the cited-answer slice. It is a comparison product, not a
generic chat endpoint.

## Technical Context

**Language/Version**: Python 3.13; strict TypeScript 5.x; Node.js 24 LTS

**Primary Dependencies**: FastAPI, Pydantic, PostgreSQL/pgvector, existing retrieval and citation
services, LangGraph-compatible explicit workflow, Next.js, Playwright, pytest, Vitest

**Storage**: PostgreSQL for comparison runs, normalized cells, evidence links, usage events and
30-day anonymous content retention; existing immutable corpus snapshots remain the evidence source.

**Testing**: pytest unit/contract/integration tests, PostgreSQL contract tests, Vitest, Playwright,
offline deterministic comparison dataset, and citation/evidence parity checks.

**Target Platform**: Existing web/API/worker modular monolith and local Docker PostgreSQL; no new
service is introduced.

**Performance Goals**: Progress visible within two seconds; normal comparison terminal result within
30 seconds; at least 95% of populated cells cite supporting evidence in the launch dataset.

**Constraints**: Two-to-four supported technologies; eight fixed initial criteria; no unrestricted
web research; no reports, accounts, uploads or saved history in this feature; source instructions
remain untrusted data; anonymous comparison quota defaults to five accepted comparisons per rolling
24 hours and must remain separate from the ten-question cited-answer quota.

**Scale/Scope**: Portfolio MVP for the five governed catalog collections, with Anthropic prioritized
as the fourth comparison row and Gemini available as the fifth corpus collection; each comparison
request remains bounded to two through four technology rows. Reranking and broad model routing
remain separate experiments.

## Constitution Check

| Principle | Design Evidence | Status |
|---|---|---|
| Evidence Over Fluency | Every populated cell has immutable evidence IDs; missing and contradictory states are explicit. | PASS |
| Spec Before Code | This specification precedes the plan, tasks, tests and implementation. | PASS |
| Test and Evaluate First | Contract, domain, retrieval, locale and deterministic dataset tests precede implementation. | PASS |
| Explicit Contracts and Type Safety | Versioned request, run, matrix and cell schemas cross every boundary. | PASS |
| Provider Independence | Retrieval, normalization and generation use internal ports and existing adapters. | PASS |
| Security and Privacy | Existing allowlist, prompt-injection boundary, anonymous HMAC identity and retention policy are reused. | PASS |
| Observable and Cost-Aware | Run IDs, quota, latency, cost metadata and LangSmith stage traces are required. | PASS |
| Small Vertical Slices | P1 delivers two-technology comparison before four-technology polish. | PASS |
| English-Canonical Engineering | Code and contracts remain English; public labels have `en-US`/`es-MX` parity. | PASS |

## Architecture and Runtime Flow

```text
Next.js comparison page
  -> FastAPI validation, idempotency and comparison quota
  -> Comparison workflow
       validate_selection
       fan_out_retrieval (one branch per technology and criterion)
       normalize_cells
       evidence_gate
       compose_matrix_summary
       verify_citations
       finalize_comparison
  -> verified comparison SSE/status response
  -> PostgreSQL comparison run, cells, evidence links and metrics
```

The retrieval branches share one selected corpus snapshot and preserve product/version/date/source
filters. Normalization never invents a missing unit or silently merges incompatible definitions.
The model may write a concise summary only after cell evidence is assembled; the matrix remains the
authoritative structured result.

## Data and Contract Design

- `ComparisonRequest` accepts technologies, criteria, filters, locale and idempotency key.
- `ComparisonRun` records lifecycle state, request ID, visitor hash, selected snapshot and quota
  accounting.
- `ComparisonMatrix` stores stable technology and criterion order plus locale-independent values.
- `ComparisonCell` stores state (`supported`, `unsupported`, `partial`, `contradictory`), value,
  unit, explanation and evidence IDs.
- `ComparisonEvidence` references immutable corpus rows; it never stores model-authored URLs.

Public contracts are defined in [contracts/openapi.yaml](contracts/openapi.yaml) and the streaming
events in [contracts/comparison-events.md](contracts/comparison-events.md).

## Phase 0: Research Outcome

Research decisions are recorded in [research.md](research.md): reuse the existing exact hybrid
retrieval baseline, represent unsupported and contradictory cells explicitly, use deterministic
normalization before any prose synthesis, and keep the comparison quota separate from cited-answer
quota.

## Phase 1: Design Outcome

The data model, API/SSE contract and runnable validation guide are recorded in [data-model.md](data-model.md),
[contracts/](contracts/) and [quickstart.md](quickstart.md).

## Implementation Phases

1. **Foundation**: schemas, database tables, quota extension, and failing contract tests.
2. **P1 comparison**: two-technology request, fan-out retrieval, normalization, matrix, citations,
   progress and cancellation.
3. **Evidence safety**: unsupported/partial/contradictory cells, injection boundary and temporal
   filters.
4. **Bilingual and four-technology polish**: locale parity, accessibility, four-row journey and
   deterministic evaluation dataset.
5. **Convergence**: Spec Kit analyze/converge, quickstart, offline eval and Playwright gate.

## Complexity Tracking

| Decision | Why it is needed | Simpler alternative rejected |
|---|---|---|
| Dedicated matrix and cell contracts | A prose answer cannot express missing values, units and contradictions reliably. | Reusing `/v1/answers` would lose per-cell evidence and make comparison indistinguishable from chat. |
| Separate comparison quota | A four-branch comparison costs more than one cited question. | Sharing the ten-question quota would hide cost and abuse differences. |
| Fan-out retrieval per technology | Each row needs independent filters and evidence provenance. | One blended query would allow evidence from one technology to leak into another row. |
