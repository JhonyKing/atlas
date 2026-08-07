# Feature Specification: Retrieval Quality and Multilingual Evidence

**Feature Branch**: `codex/007-retrieval-quality-multilingual`  
**Created**: 2026-08-06  
**Status**: Draft  
**Input**: PRD items RET-001 through RET-009

## User Scenarios & Testing

### User Story 1 - Retrieve the right evidence across languages (Priority: P1)

As a researcher, I want ATLAS to understand aliases, versions, synonyms, and language differences
so that a question finds authoritative evidence even when the source language differs from my UI.

**Independent Test**: Run a fixed set of English and Spanish questions with aliases and version names,
then compare retrieved evidence IDs, language labels, source authority, and freshness.

**Acceptance Scenarios**:

1. **Given** a question containing an alias or version, **When** retrieval prepares the query, **Then**
   it emits bounded rewritten terms without changing the user's intent.
2. **Given** a Spanish question and English source, **When** retrieval runs, **Then** it preserves the
   original evidence language and returns a localized explanation of the match.
3. **Given** provider/framework/date/version/language/source-type filters, **When** search executes,
   **Then** every returned row satisfies all selected filters.

### User Story 2 - Prefer diverse, authoritative, fresh context (Priority: P1)

As an answer verifier, I want retrieval to remove duplicates, diversify parent sources, and prioritize
authoritative fresh evidence within a bounded token budget so that claims are better supported.

**Independent Test**: Use a fixture with duplicate chunks, parent/child documents, conflicting dates,
and mixed authority; verify selected evidence and budget under deterministic scores.

**Acceptance Scenarios**:

1. **Given** near-duplicate chunks from one source, **When ranking runs,** **Then** the result keeps
   the strongest representative and fills remaining slots with diverse sources.
2. **Given** parent and child chunks, **When context is assembled,** **Then** the selected child keeps
   a bounded parent heading/context window without exceeding the budget.
3. **Given** stale and current authoritative evidence, **When ranking runs,** **Then** current
   authoritative evidence wins unless the question explicitly requests history.
4. **Given** a configured evidence budget, **When results exceed it,** **Then** lower-priority items
   are dropped deterministically and no request can bypass the limit.

### User Story 3 - Measure retrieval quality before enabling advanced ranking (Priority: P2)

As an engineer, I want reproducible retrieval metrics and a baseline-versus-reranker comparison so
that an optimization is enabled only when it improves quality without unacceptable latency or cost.

**Independent Test**: Run the versioned evaluation dataset through baseline, diversity, and optional
reranker adapters and compare Hit@5, MRR, context precision/recall, citation precision, freshness,
latency, and estimated cost.

**Acceptance Scenarios**:

1. **Given** a baseline result and a candidate reranker, **When evaluation runs,** **Then** it reports
   paired metrics and does not silently replace the baseline.
2. **Given** no measured improvement or a latency/cost regression, **When a reranker is selected,**
   **Then** the system keeps the baseline and records the reason.
3. **Given** temporal, cross-language, contradiction, and source-version cases, **When evals run,**
   **Then** each case reports a deterministic pass/fail with evidence IDs.

## Edge Cases

- A rewrite expands beyond its term or token limit; truncate deterministically and retain the original.
- A filter names an unknown provider/version/language; return an empty result with a safe reason.
- All candidates are duplicates or over budget; return the best bounded subset or abstain.
- A reranker adapter times out or returns malformed scores; fall back to baseline.
- Two sources contradict each other; preserve both provenance records and expose the contradiction.
- A multilingual embedding profile is unavailable; use the configured baseline and record fallback.

## Requirements

### Functional Requirements

- **FR-RET-001**: Query preparation MUST support bounded rewriting for terms, versions, aliases, and
  synonyms while preserving the original query and language.
- **FR-RET-002**: Retrieval MUST apply provider, framework, date, version, language, and source-type
  filters before ranking and expose the active filter set in run metadata.
- **FR-RET-003**: Ranking MUST provide deterministic deduplication, MMR-style diversity, and bounded
  parent-child context windows behind typed adapters.
- **FR-RET-004**: Optional reranking MUST be behind an adapter and enabled only after a measured
  baseline comparison of quality, latency, and cost.
- **FR-RET-005**: Multilingual retrieval MUST preserve original evidence language and benchmark the
  selected embedding profile against the current baseline.
- **FR-RET-006**: Evidence assembly MUST enforce a configured token/character budget and prioritize
  authority, freshness, and direct query relevance deterministically.
- **FR-RET-007**: Retrieval runs MUST emit Hit@5, MRR, context precision/recall, citation precision,
  freshness accuracy, latency, and estimated cost metrics for versioned evaluation cases.
- **FR-RET-008**: Regression fixtures MUST cover temporal, cross-language, contradiction, and
  source-version behavior without leaking private content or secrets.

### Key Entities

- **QueryRewrite**: Original query, bounded alternatives, language, aliases, and version terms.
- **RetrievalFilters**: Provider/framework/date/version/language/source-type constraints.
- **RankedEvidence**: Evidence row, score components, authority/freshness signals, and diversity key.
- **RerankerDecision**: Baseline/candidate metrics, latency/cost delta, and enablement decision.
- **RetrievalEvaluation**: Dataset version, query case, expected IDs, metrics, and result status.

## Success Criteria

- **SC-RET-001**: At least 95% of alias/version fixture cases retrieve the expected source in top 5.
- **SC-RET-002**: 100% of filtered results satisfy every requested filter and 0 unsafe candidates are
  introduced by rewriting.
- **SC-RET-003**: Duplicate fixture evidence is reduced by at least 90% while retaining at least two
  independent authoritative sources when available.
- **SC-RET-004**: 100% of assembled contexts stay within the configured evidence budget.
- **SC-RET-005**: A candidate reranker is enabled only when Hit@5 or MRR improves without more than
  20% latency or cost regression; otherwise baseline remains active.
- **SC-RET-006**: English/Spanish fixture pairs preserve evidence identity and original-language
  metadata in 100% of cases.
- **SC-RET-007**: Every evaluation run records all required metrics and version identifiers.

## Assumptions

- Existing `Question`, `Evidence`, `RetrievalRow`, corpus snapshot, and cited-answer contracts remain
  authoritative.
- The first slice uses deterministic lexical/vector fixture scores; provider-specific model routing
  remains Feature 008.
- Existing privacy, allowlist, and retention boundaries apply to every candidate and metric.
