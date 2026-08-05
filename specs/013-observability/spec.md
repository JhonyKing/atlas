# Feature Specification: LangSmith Quality Observability

**Feature Branch**: `codex/013-observability`
**Created**: 2026-08-05
**Status**: Draft
**Input**: Plan Maestro RAG/Evals + PRD v1.1, observabilidad, evaluación y privacidad.

## User Scenarios & Testing

### User Story 1 - Trace one answer end to end (Priority: P1)

As the project owner, I can locate one answer request and inspect its retrieval, generation,
verification and streaming stages using a correlation ID, without exposing the user's question or
source excerpts by default.

**Independent Test**: Run one deterministic answer and verify a trace tree contains the request,
retrieval, model and verifier stages, safe metadata, duration and terminal outcome.

### User Story 2 - Diagnose quality regressions (Priority: P1)

As an evaluator, I can filter traces by corpus snapshot, locale, model, prompt/retrieval versions,
feedback and outcome, then link a difficult trace to a versioned evaluation example.

**Independent Test**: Mark a response as incorrect citation and verify it is discoverable in the
review workflow and can become a regression example without copying secrets or PII.

### User Story 3 - Operate safely (Priority: P2)

As an operator, I can run ATLAS when LangSmith is unavailable or unconfigured, preserving the API
behavior while keeping local OpenTelemetry and structured diagnostics available.

**Independent Test**: Remove LangSmith configuration, run the contract suite, and verify no request
fails and no secret/content appears in logs.

## Requirements

- **FR-OBS-001**: The system MUST correlate every answer lifecycle with one request/run identifier.
- **FR-OBS-002**: Traces MUST expose stage, status, latency, token/cost class, model, locale,
  prompt/retrieval/index/corpus versions and error code as safe metadata.
- **FR-OBS-003**: Raw questions, generated answers, evidence text, authorization values and API
  keys MUST be excluded from external traces by default.
- **FR-OBS-004**: LangSmith tracing MUST be optional and disabled safely when configuration is absent.
- **FR-OBS-005**: The system MUST support versioned datasets, experiments, human feedback and
  regression-case links.
- **FR-OBS-006**: Observability data MUST respect the PRD retention and deletion policy.
- **FR-OBS-007**: A deployment MUST provide a documented dashboard/runbook for latency, errors,
  citations, abstention, feedback and cost segmented by locale and corpus snapshot.

## Success Criteria

- **SC-OBS-001**: 100% of completed and failed answer runs in the contract suite have a correlation
  ID and terminal outcome.
- **SC-OBS-002**: A reviewer can locate a trace and its safe metadata in under two minutes.
- **SC-OBS-003**: The API has no availability regression when LangSmith is disabled or unreachable.
- **SC-OBS-004**: A redaction test finds no question, answer, excerpt, secret or authorization value
  in exported trace payloads.
- **SC-OBS-005**: Every promoted evaluation result identifies dataset, experiment, application
  commit and corpus snapshot versions.

## Assumptions

- LangSmith cloud credentials are supplied only by the operator through secret configuration.
- OpenTelemetry remains the local baseline and is not removed.
- The initial feature records metadata and bounded hashes; full content capture requires an explicit
  privacy decision and is out of the default path.

