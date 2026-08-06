# Feature Specification: Evidence-backed Research Reports

**Feature Branch**: `003-reports`

**Created**: 2026-08-06

**Status**: Draft

**Input**: Product backlog requirements RPT-001 through RPT-012 for generating cited research
reports from completed ATLAS research runs.

## User Scenarios & Testing

### User Story 1 - Generate a cited report from a completed research run (Priority: P1)

As a researcher, I want to turn a completed cited-answer or comparison run into a structured
report, so I can share an auditable research artifact instead of copying unverified text.

**Why this priority**: A report generated from existing verified evidence is the smallest useful
portfolio vertical slice and reuses the product's evidence-first boundary.

**Independent Test**: Given a completed research run with claim-level citations, request a report,
wait for the terminal status, and verify that the report contains the requested sections and only
references evidence present in the source run.

**Acceptance Scenarios**:

1. **Given** a completed source run, **When** a valid report request is submitted, **Then** ATLAS
   accepts it with a repeat-safe request identifier and reports progress through terminal completion.
2. **Given** a report request with an unsupported type or missing source run, **When** it is
   submitted, **Then** ATLAS rejects it with a controlled error and creates no downloadable artifact.
3. **Given** a completed report, **When** its sections and references are inspected, **Then** every
   factual section has citations linked to evidence from the source run.

### User Story 2 - Download and manage report artifacts (Priority: P2)

As a researcher, I want to download a report as DOCX or PDF and delete it before expiration, so I
can control the lifecycle of generated work products.

**Why this priority**: A report is not useful for a portfolio demonstration unless its artifact can
be inspected, downloaded, and safely retired.

**Independent Test**: Generate a report, download both supported formats, verify their content and
links, delete the report, and confirm subsequent download attempts fail safely.

**Acceptance Scenarios**:

1. **Given** a completed report, **When** the user requests DOCX or PDF, **Then** the returned file
   has the correct media type, non-empty content, readable sections, and human-readable references.
2. **Given** an expired or deleted report, **When** a download is requested, **Then** ATLAS returns
   a not-available response without revealing artifact storage details.
3. **Given** a report owned by another anonymous visitor, **When** it is requested or deleted,
   **Then** ATLAS returns not-found semantics and does not disclose its existence.

### User Story 3 - Produce bilingual reports with citation parity (Priority: P3)

As a Spanish-speaking researcher, I want the report narrative and headings in Spanish while source
excerpts remain clearly marked in their original language, so translation does not change evidence
identity or meaning.

**Why this priority**: The public ATLAS journey is bilingual, and reports must preserve the same
evidence graph across locales.

**Independent Test**: Generate equivalent English and Spanish reports from one source run and
compare their citation IDs, URLs, and source excerpts.

**Acceptance Scenarios**:

1. **Given** one source run and two locales, **When** equivalent reports are generated, **Then**
   their citation identity and source URLs are identical while presentation text is localized.
2. **Given** a source excerpt in English, **When** a Spanish report is rendered, **Then** the excerpt
   is labelled as original evidence and is not silently replaced by an unsupported translation.

### Edge Cases

- A source run contains an abstention or unsupported comparison cells.
- A report has no citations for a requested section.
- A report generator times out or is interrupted after planning but before rendering.
- A retry arrives with the same idempotency key and an identical request.
- A retry arrives with the same idempotency key but different report parameters.
- A DOCX or PDF renderer produces an empty, malformed, clipped, or citation-less artifact.
- A report reaches its retention deadline while a download is in progress.
- A user requests deletion twice.

## Requirements

### Functional Requirements

- **FR-001**: The system MUST accept report requests only for completed source runs visible to the
  requesting visitor.
- **FR-002**: The system MUST support report types for technology comparison, architecture brief,
  ADR, release intelligence, and research report; the first implementation MUST deliver the
  technology-comparison vertical slice.
- **FR-003**: The system MUST validate a report specification containing audience, locale, scope,
  selected criteria, required sections, and source-run identity before generation.
- **FR-004**: The system MUST persist report job state with accepted, planning, rendering,
  completed, failed, cancelled, expired, and deleted terminal semantics.
- **FR-005**: The system MUST make report creation repeat-safe by idempotency key and reject a key
  reused with different parameters.
- **FR-006**: The system MUST create an intermediate structured report representation before DOCX
  or PDF rendering.
- **FR-007**: The system MUST preserve claim-level citation links from the source run into every
  factual report section and references list.
- **FR-008**: The system MUST provide DOCX and PDF downloads for completed reports and validate that
  each artifact is non-empty, parseable, and contains its required references.
- **FR-009**: The system MUST perform visual QA on every generated DOCX and PDF before marking the
  artifact complete; clipping, overflow, missing citations, or invalid links MUST fail generation.
- **FR-010**: The system MUST support English and Mexican Spanish presentation with identical
  citation IDs, URLs, and original evidence excerpts.
- **FR-011**: The system MUST enforce a report quota separate from the anonymous cited-answer quota.
- **FR-012**: The system MUST support repeat-safe download and deletion, and MUST return safe
  not-found semantics after expiration or deletion.
- **FR-013**: The system MUST NOT expose provider keys, raw visitor identifiers, or untrusted source
  instructions in reports or logs.
- **FR-014**: The system MUST record report metadata sufficient to reproduce the artifact: source
  run, report type, locale, model/prompt versions, corpus snapshot, creation time, and content hash.
- **FR-015**: At feature close, the implementation MUST include a documentation task that reads
  the final spec, plan, tasks, and commits, then updates README, relevant ADRs, and architecture
  documentation only where the delivered behavior changed them.

### Key Entities

- **ReportSpec**: Validated request parameters for audience, type, locale, scope, criteria, and
  required sections.
- **ReportJob**: Durable or in-process lifecycle record for planning, rendering, retry, quota, and
  ownership state.
- **ReportDocument**: Completed artifact metadata including format, content hash, size, expiration,
  source run, and citation manifest.
- **ReportSection**: Structured intermediate section with title, narrative, claims, limitations,
  and evidence links.

## Success Criteria

### Measurable Outcomes

- **SC-001**: At least 95% of valid report requests reach a terminal result within 60 seconds in
  the supported portfolio workload; failures are explicit and retryable where safe.
- **SC-002**: 100% of factual report sections in accepted artifacts have at least one valid citation
  to evidence from the source run.
- **SC-003**: 100% of generated DOCX and PDF artifacts pass parseability, non-empty, link, citation,
  and visual-layout checks before completion.
- **SC-004**: English and Spanish reports from the same source run preserve 100% of citation IDs,
  canonical URLs, and original evidence excerpts.
- **SC-005**: Duplicate requests with the same parameters create one report job and duplicate
  deletion/download requests remain safe and repeatable.
- **SC-006**: A report from a deleted or expired job is never downloadable and reveals no storage
  path or private metadata.

## Assumptions

- The first vertical slice uses completed technology-comparison runs already supported by ATLAS.
- Report generation is asynchronous even if the first local implementation uses an in-process job
  coordinator.
- Report artifacts use the existing local artifact storage seam until a managed object store is
  specified.
- Human review of the generated report remains a portfolio acceptance step; automated validation
  cannot replace judgment about recommendation quality.
- Live model calls, if used for narrative planning, remain behind existing provider adapters and
  can fail closed to an explicit report failure.
