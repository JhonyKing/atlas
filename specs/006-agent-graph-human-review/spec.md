# Feature Specification: Agent Graph, Planning, Checkpoints, and Human Review

**Feature Branch**: `codex/006-agent-graph-human-review`  
**Created**: 2026-08-06  
**Status**: Draft  
**Input**: PRD items AGT-001 through AGT-010

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Route a question through an explicit evidence workflow (Priority: P1)

As a researcher, I want ATLAS to classify my question and route it through explicit planning,
retrieval, verification, answer, and optional report steps so that every result has a visible,
repeatable reason for its path.

**Independent Test**: Submit representative factual, comparison, report, ambiguous, and out-of-scope
questions and inspect the recorded node order, route decision, language, freshness, and final state.

**Acceptance Scenarios**:

1. **Given** a supported factual question, **When** the workflow starts, **Then** it classifies intent,
   depth, language, risk, and freshness before planning retrieval.
2. **Given** a comparison request, **When** planning completes, **Then** the plan contains explicit
   subquestions, source/date criteria, and an evidence budget before retrieval begins.
3. **Given** an unsupported or unsafe request, **When** classification detects the boundary,
   **Then** the workflow abstains without invoking retrieval or sensitive tools.
4. **Given** any completed run, **When** an operator inspects it, **Then** each node has a deterministic
   name, input/output state boundary, duration, and outcome.

### User Story 2 - Resume long-running work safely (Priority: P1)

As an operator, I want long-running answer, report, ingestion, and evaluation work to checkpoint
by thread so that a worker failure can resume without duplicating side effects or losing evidence.

**Independent Test**: Interrupt a deterministic run after each checkpoint, restart the worker, and
verify that it resumes from the last durable state and produces the same final result once.

**Acceptance Scenarios**:

1. **Given** a run with a stable thread identifier, **When** a checkpoint is written, **Then** it
   contains the versioned state, completed node, timestamp, and idempotency information.
2. **Given** a worker failure after a completed node, **When** the same thread resumes, **Then** it
   skips completed side effects and continues from the next node.
3. **Given** two concurrent resume requests for one thread, **When** they execute, **Then** only one
   performs each side effect and both receive the same terminal state.
4. **Given** an expired or corrupted checkpoint, **When** resume is requested, **Then** the workflow
   fails closed with a safe error and does not publish a partial answer.

### User Story 3 - Pause for human review before consequential publication (Priority: P1)

As a reviewer, I want to approve, edit, or reject a proposed answer/report before publication so
that ATLAS keeps human judgment at the boundary of consequential or low-confidence actions.

**Independent Test**: Produce a review-required result and exercise approve, edit, reject, timeout,
and duplicate-decision paths while checking that publication occurs only after a valid decision.

**Acceptance Scenarios**:

1. **Given** a low-confidence answer or report with sensitive actions, **When** verification completes,
   **Then** the workflow pauses and exposes a review record with evidence and reason.
2. **Given** an authorized reviewer edits a proposal, **When** they submit the decision, **Then** the
   edited content is validated, versioned, and published with reviewer identity and timestamp.
3. **Given** a reviewer rejects a proposal, **When** the decision is accepted, **Then** no answer or
   report is published and the run ends with a safe rejection state.
4. **Given** an expired, duplicate, or unauthorized decision, **When** it is submitted, **Then** the
   original run remains unchanged and the API returns a safe, repeatable error.

## Edge Cases

- A classification provider times out before a route is chosen; the run must abstain safely.
- A plan contains duplicate subquestions or conflicting freshness constraints; normalize or reject it
  before retrieval.
- A checkpoint references a corpus, prompt, model, or policy version no longer available; resume must
  fail closed with an actionable operator error.
- A node emits an oversized or secret-bearing state field; persistence must redact or reject it.
- A reviewer edits citations or removes supporting evidence; validation must reject publication.
- Cancellation arrives while a node is running; the node must reach a controlled terminal state and
  replay must remain idempotent.

## Requirements

### Functional Requirements

- **FR-AGT-001**: The workflow MUST represent messages, user, request, intent, language, freshness,
  plan, evidence, citations, answer, report, quality, errors, thread ID, and version metadata in a
  typed state contract.
- **FR-AGT-002**: The workflow MUST classify intent, depth, language, risk, and freshness before
  selecting a route, with a deterministic fallback when classification is unavailable.
- **FR-AGT-003**: Planning MUST decompose supported questions into bounded subquestions and explicit
  source/date criteria, preserving the user's requested language and freshness.
- **FR-AGT-004**: Conditional routes MUST be explicit, inspectable, deterministic for the same state,
  and limited to approved nodes and provider adapters.
- **FR-AGT-005**: Every node MUST enforce state isolation, timeout, cancellation, and safe error
  handling; external content MUST NOT redefine instructions or authorize tools.
- **FR-AGT-006**: Report generation MUST accept only a validated report specification and MUST pause
  before publication or other consequential action when review is required.
- **FR-AGT-007**: Checkpoints MUST be durable, versioned, keyed by `thread_id`, content-safe, and
  sufficient to resume answer, report, ingestion, and evaluation workflows.
- **FR-AGT-008**: Resume and replay MUST be idempotent, concurrency-safe, and must not duplicate
  external side effects or publish partial results.
- **FR-AGT-009**: Human review MUST support approve, edit, reject, authorization, expiry, and
  idempotent duplicate-decision handling with an auditable record.
- **FR-AGT-010**: Each run MUST expose node order, route decision, checkpoint, review, latency,
  outcome, and safe error telemetry without secrets or private content.

### Key Entities

- **AtlasState**: Versioned workflow state carried across nodes.
- **RoutePlan**: Intent, subquestions, criteria, freshness, evidence budget, and selected path.
- **Checkpoint**: Durable thread snapshot with completed node and replay key.
- **ReviewRequest**: Proposed publication, evidence references, required decision, expiry, and status.
- **NodeEvent**: Content-safe node start/finish/error telemetry.

## Success Criteria

- **SC-AGT-001**: 100% of deterministic route fixtures record the expected node order and terminal
  state, including abstention paths.
- **SC-AGT-002**: 100% of crash-and-resume fixtures produce one terminal result with no duplicated
  side effect and the same evidence identifiers as uninterrupted execution.
- **SC-AGT-003**: 100% of review-required fixtures remain unpublished until an authorized decision;
  rejection produces zero publication artifacts.
- **SC-AGT-004**: At least 99% of valid checkpoint writes and reads complete within 250 ms in the
  deterministic local harness.
- **SC-AGT-005**: 100% of persisted state and telemetry fixtures contain no API keys, private content,
  or unredacted sensitive fields.
- **SC-AGT-006**: A reviewer can understand why a route paused or abstained using only the run's
  visible plan, evidence references, and safe error message.

## Assumptions

- Feature 001 answer/evidence contracts, Feature 003 report contracts, Feature 004 ownership guards,
  and Feature 005 ingestion governance remain the authoritative downstream boundaries.
- The first slice uses deterministic local providers and fixtures; production provider selection and
  advanced model routing remain in Feature 008.
- Reviewers are authenticated operators or resource owners according to the existing authorization
  model.
- Checkpoint retention follows the existing content-retention policy and excludes raw private data.
