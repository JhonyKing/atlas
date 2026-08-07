# Feature Specification: LangSmith Evaluation Harness

**Feature Branch**: `codex/016-langsmith-evaluation-harness`
**Status**: Draft
**Input**: PRD EVA-013 through EVA-020

## User Stories

### User Story 1 — Run reproducible offline graders (P1)
As an evaluator, I can run versioned deterministic and structured graders against the 60-case
dataset without network access.

### User Story 2 — Link online experiments safely (P1)
As an operator, I can opt into LangSmith dataset/experiment execution with commit and corpus
metadata while keeping inputs and outputs hidden by default.

### User Story 3 — Block quality regressions (P1)
As a maintainer, I can apply a versioned gate to citation, faithfulness, abstention, cost and
latency metrics before promotion, and export negative cases without PII.

## Functional Requirements

- **FR-EVA-001**: Dataset examples MUST include input, reference, chunk IDs, locale and corpus version.
- **FR-EVA-002**: Deterministic graders MUST validate schema, citations, links, abstention, duplicates and reports.
- **FR-EVA-003**: Model/code/human grader output MUST be structured with score, strengths, weaknesses and rationale.
- **FR-EVA-004**: Online runs MUST link dataset, experiment, trace, commit and corpus snapshot without raw content by default.
- **FR-EVA-005**: Negative cases MUST export as a versioned, secret-free regression dataset.
- **FR-EVA-006**: CI MUST fail closed when versioned quality, cost or latency thresholds regress.

## Success Criteria

- **SC-EVA-001**: Offline execution is repeatable and records dataset/evaluator/application versions.
- **SC-EVA-002**: A failing threshold returns a non-zero CI exit code with actionable reasons.
- **SC-EVA-003**: Exported regression cases contain no secrets, authorization values or raw private content.
