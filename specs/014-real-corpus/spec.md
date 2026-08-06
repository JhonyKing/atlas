# Feature Specification: Real Multi-Document Corpus

**Feature Branch**: `codex/014-real-corpus`
**Created**: 2026-08-05
**Status**: Draft
**Input**: PRD v1.1 corpus governance + Plan Maestro RAG/Evals corpus/harness requirements.

**Expansion decision (2026-08-05)**: add Anthropic first as the fourth governed collection and
Google Gemini second as the fifth collection. Anthropic is the first candidate for a four-row
comparison; Gemini is registered for the next corpus expansion. Neither candidate is active until
its source review records current terms, robots and licensing evidence.

## User Scenarios & Testing

### User Story 1 - Inspect a real corpus (Priority: P1)

As a reader, I can see that ATLAS answers against a verified, multi-page snapshot of official
technical sources rather than a three-record fixture.

**Independent Test**: Promote a manifest with at least 12 authorized documents, inspect its source,
page and chunk counts, and verify every answer citation resolves to a captured source version.

### User Story 2 - Refresh without data loss (Priority: P1)

As an operator, I can refresh one collection and retain the last good version if fetch, OCR,
embedding or validation fails.

**Independent Test**: Force a failed refresh and verify the active snapshot and public status remain
the previous successful version.

### User Story 3 - Evaluate retrieval quality (Priority: P2)

As an evaluator, I can run a versioned bilingual/multi-hop/OCR/no-answer dataset against HTTP and
compare retrieval and answer metrics across configurations.

**Independent Test**: Run the offline harness twice from the same commit and obtain identical
inputs, configuration metadata and deterministic evaluator outputs.

## Requirements

- **FR-COR-001**: The corpus MUST use a versioned, allowlisted manifest of authoritative sources.
- **FR-COR-002**: A promoted snapshot MUST include source URL, publisher, license/robots decision,
  capture date, content hash, page/section provenance and chunk count.
- **FR-COR-003**: The launch validation MUST include more than three pages and at least 12 source
  documents across the supported collections.
- **FR-COR-004**: Failed or duplicate ingestion MUST NOT replace or duplicate active content.
- **FR-COR-005**: The runtime MUST distinguish demo fixtures from verified real snapshots.
- **FR-COR-006**: The harness MUST support factual, multi-hop, OCR, bilingual and no-answer cases
  with ground-truth chunk IDs.
- **FR-COR-007**: Retrieval results MUST include Hit@k, MRR, context precision/recall, citation
  precision and freshness measurements.
- **FR-COR-008**: Source content MUST be bounded, licensed/allowed and protected from SSRF and
  embedded prompt instructions.
- **FR-COR-009**: The corpus catalog MUST represent the approved expansion order (`anthropic`, then
  `gemini`) without enabling either connector before its source review is complete.

## Success Criteria

- **SC-COR-001**: A verified snapshot contains at least 12 source documents and more than three
  pages, with reproducible hash/count evidence.
- **SC-COR-002**: 100% of active sources have canonical URL, publisher, capture time and content
  hash.
- **SC-COR-003**: A failed seven-day refresh validation preserves the last successful snapshot.
- **SC-COR-004**: The harness produces repeatable metrics and records corpus/config versions.
