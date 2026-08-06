# Research: Evidence-backed Research Reports

## Decision 1: Source boundary

**Decision**: The first report type consumes a completed technology-comparison run and its
claim-level evidence. It does not re-run retrieval or permit the report model to select new sources.

**Rationale**: The comparator already owns a reproducible corpus snapshot and per-cell evidence. A
second retrieval path would weaken provenance and make report citations difficult to audit.

**Alternatives considered**: Free-form question-to-report generation was rejected because it could
produce a report without a persisted research run; a fresh report-specific retriever was rejected
until measured need exists.

## Decision 2: Artifact formats

**Decision**: Build one structured report representation and render DOCX and PDF from it. A report
cannot enter `completed` until structural checks, citation checks, and visual QA pass.

**Rationale**: Shared intermediate content prevents format and locale divergence. Rendering checks
are required because parsers alone cannot detect clipping or overflow.

**Alternatives considered**: HTML-only output was rejected because the PRD explicitly requires DOCX
and PDF; format-specific narrative generation was rejected because it duplicates evidence logic.

## Decision 3: Lifecycle and ownership

**Decision**: Report metadata stores source run, owner digest, idempotency key, state, expiration,
format hashes, and citation manifest; binary content stays behind a storage adapter.

**Rationale**: This supports repeat-safe requests, deletion, expiry, and future object storage
without exposing paths or raw visitor identifiers.

**Alternatives considered**: Browser-only downloads were rejected because they cannot enforce expiry
or ownership; a permanent artifact store was rejected because the product has a retention policy.

## Decision 4: Evaluation boundary

**Decision**: Add deterministic report cases and artifact integrity checks now. Live model/RAG and
LangSmith experiments remain opt-in until the report planner and renderer have stable contracts.

**Rationale**: CI must be secret-free and deterministic; report quality still needs an explicit
human review boundary.

**Alternatives considered**: Calling the live model on every PR was rejected for cost, nondeterminism,
and secret exposure.
