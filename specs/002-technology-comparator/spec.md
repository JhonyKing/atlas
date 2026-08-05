# Feature Specification: Evidence-Backed Technology Comparator

**Feature Branch**: `codex/002-technology-comparator`

**Created**: 2026-08-05

**Status**: Draft

**Input**: PRD v1.1 comparator requirements and backlog items CMP-001–CMP-009.

## User Scenarios & Testing

### User Story 1 - Compare selected technologies (Priority: P1)

As a technical researcher, I can select two to four supported technologies and compare them using
explicit criteria so that I can make a documented decision instead of reading an unstructured chat
answer.

**Why this priority**: A bounded comparison is the next portfolio-level capability after one cited
answer and demonstrates multi-branch retrieval and evidence synthesis.

**Independent Test**: Select two supported technologies, choose at least three criteria, run the
comparison, and inspect a matrix in which every populated cell links to supporting evidence.

**Acceptance Scenarios**:

1. **Given** two supported technologies and selected criteria, **when** the visitor starts a
   comparison, **then** the system shows progress and returns one row per technology and one column
   per selected criterion.
2. **Given** a populated comparison cell, **when** the visitor opens its evidence, **then** the
   source title, publisher, canonical URL, excerpt, capture date, and version context are shown.
3. **Given** four selected technologies, **when** the comparison completes, **then** all four are
   represented without collapsing the result into a generic prose answer.

### User Story 2 - Understand missing and conflicting evidence (Priority: P1)

As a skeptical reviewer, I can distinguish a supported value, an unsupported value, and a
contradiction so that the matrix does not imply certainty where the corpus does not provide it.

**Why this priority**: A comparison is only trustworthy when empty or conflicting cells are explicit
and traceable.

**Independent Test**: Run prepared cases containing a missing criterion and two conflicting sources;
verify that the corresponding cells explain the evidence state and do not invent a value.

**Acceptance Scenarios**:

1. **Given** no authoritative evidence for a technology and criterion, **when** the comparison is
   rendered, **then** the cell is marked unsupported with a concise explanation and no fabricated
   claim.
2. **Given** credible sources disagree, **when** the comparison is rendered, **then** the cell
   shows the disagreement, source identities, and relevant dates or versions.
3. **Given** a date, version, or provider filter, **when** the comparison runs, **then** every
   populated cell respects that constraint or explains why it cannot be verified.

### User Story 3 - Review and share a bilingual comparison (Priority: P2)

As an English- or Spanish-speaking visitor, I can switch the comparison interface between `en-US`
and `es-MX` without changing the compared claims, evidence IDs, dates, or numeric values.

**Why this priority**: The public product is bilingual and the comparison must preserve the same
evidence while changing only presentation language.

**Independent Test**: Complete one comparison in both locales and compare the terminal matrix,
evidence identifiers, citations, dates, and status values.

**Acceptance Scenarios**:

1. **Given** a completed comparison, **when** the visitor changes locale, **then** labels, status
   messages, validation text, and controls are translated without a page reload.
2. **Given** source excerpts in the original language, **when** the comparison is shown in either
   locale, **then** the excerpt is labelled as original source text when it is not translated.

## Edge Cases

- Fewer than two, more than four, duplicate, or unsupported technologies are rejected before
  retrieval and the visitor's selections remain available for correction.
- No criteria are selected, or all selected criteria are outside the supported criterion list.
- A technology has evidence for only some criteria.
- Sources use different units, price periods, release dates, or version labels.
- Two sources describe the same capability with incompatible terminology.
- A source is stale, disabled, unavailable, or contains instructions that must remain evidence only.
- One retrieval branch times out while the other branches return usable evidence.
- The visitor cancels an in-progress comparison or repeats the same idempotency key.
- The comparison produces too many citations or exceeds the published response-time limit.

## Requirements

### Functional Requirements

- **FR-CMP-001**: The system MUST accept a comparison request containing two to four distinct
  supported technologies.
- **FR-CMP-002**: The system MUST support the criteria capability, tool calling, context,
  latency, price, license, freshness, and operational risk.
- **FR-CMP-003**: The system MUST allow the visitor to select criteria and optional product,
  version, date, language, and source-type constraints before running the comparison.
- **FR-CMP-004**: The system MUST return a structured matrix with one technology row and one
  selected-criterion column for each requested criterion.
- **FR-CMP-005**: Every populated factual cell MUST reference at least one evidence record with
  source title, publisher, canonical URL, bounded excerpt, capture date, and known version/date
  context.
- **FR-CMP-006**: The system MUST label each cell as supported, unsupported, partial, or
  contradictory and MUST explain unsupported or contradictory states.
- **FR-CMP-007**: The system MUST preserve source and version/date constraints independently for
  every technology retrieval branch.
- **FR-CMP-008**: The system MUST normalize comparable values without hiding units, price periods,
  missing values, or incompatible definitions.
- **FR-CMP-009**: The system MUST expose progress, support cancellation, and make repeated
  requests safe through a stable run identifier and idempotency key.
- **FR-CMP-010**: The system MUST reject invalid comparison requests before retrieval and preserve
  the visitor's selections and correction message.
- **FR-CMP-011**: The system MUST provide equivalent `en-US` and `es-MX` presentation while
  preserving claims, evidence IDs, citations, dates, versions, and numeric values.
- **FR-CMP-012**: The system MUST treat source instructions as untrusted evidence and MUST NOT
  allow them to authorize tools or change system policy.
- **FR-CMP-013**: The comparison MUST remain separate from generic chat and MUST expose its
  criteria, matrix structure, cell states, and evidence relationships.

### Key Entities

- **ComparisonRequest**: Selected technologies, criteria, filters, locale, and idempotency key.
- **ComparisonRun**: Stable run identifier, progress, terminal status, cancellation state, and
  retention metadata.
- **ComparisonCell**: One technology/criterion intersection with normalized value, unit,
  evidence state, and explanation.
- **ComparisonMatrix**: Ordered technologies, selected criteria, cells, constraints, and locale-
  independent result metadata.
- **ComparisonEvidence**: Immutable source evidence attached to one or more cells.

## Scope Boundaries

- Version one supports only technologies represented by the approved ATLAS corpus.
- Report generation, DOCX/PDF export, saved user history, private uploads, and authentication are
  separate features.
- The comparator does not claim that one technology is universally best; recommendations must be
  explicitly supported or labelled as an inference.
- Live unrestricted web research is outside this feature.

## Success Criteria

### Measurable Outcomes

- **SC-CMP-001**: At least 90% of 20 prepared comparison requests produce the requested matrix
  structure with the correct technologies and criteria.
- **SC-CMP-002**: At least 95% of audited populated factual cells have a citation that directly
  supports the displayed value.
- **SC-CMP-003**: 100% of prepared missing-evidence and contradiction cases display the correct
  explicit cell state and do not invent a value.
- **SC-CMP-004**: At least 95% of normal comparisons show useful progress within two seconds and
  reach a terminal result within 30 seconds under launch limits.
- **SC-CMP-005**: All public comparison labels and states have both locale catalog entries, with
  100% key parity between `en-US` and `es-MX`.
- **SC-CMP-006**: Paired English/Spanish evaluations preserve 100% of technology IDs, criterion
  IDs, cell states, evidence IDs, dates, versions, and numeric values.
- **SC-CMP-007**: Every prepared source-injection case results in no unauthorized tool or policy
  change.
- **SC-CMP-008**: At least four of five external users can select technologies, choose criteria,
  inspect a cell's evidence, and identify an unsupported cell without guidance.

## Assumptions

- The existing cited-answer corpus and evidence contracts remain the source of truth.
- Initial criteria use the units and definitions available in the corpus; no unsupported numeric
  conversion is inferred.
- The initial release uses the existing anonymous visitor model and its separate comparison quota
  will be specified during planning.
- A comparison may cite multiple sources for one cell and one source may support multiple cells.
- The first implementation is English-canonical engineering with public `en-US`/`es-MX` parity.
