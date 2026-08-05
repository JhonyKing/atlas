# Implementation Plan: LangSmith Quality Observability

**Branch**: `codex/013-observability` | **Date**: 2026-08-05 | **Spec**: [spec.md](spec.md)

## Summary

Add an optional LangSmith adapter around the existing OpenTelemetry/request-context primitives.
The adapter will create safe, correlated run metadata for answer stages, preserve a no-op path for
offline tests, and expose versioned evaluation/feedback links without sending content by default.

## Technical Context

**Language/Version**: Python 3.13; TypeScript/Next.js current repository versions  
**Primary Dependencies**: `langsmith` Python SDK (optional at runtime), OpenTelemetry, FastAPI,
LangGraph, pytest  
**Storage**: Existing PostgreSQL aggregate/feedback records; LangSmith for optional traces/datasets  
**Testing**: pytest contract/unit tests; deterministic fake client; opt-in network smoke test  
**Target Platform**: Local Docker and Linux deployment  
**Project Type**: Monorepo web service and worker  
**Performance Goals**: Tracing must not add more than 100 ms p95 to a normal answer when enabled  
**Constraints**: No secrets or raw content in default trace payloads; no network dependency in CI  
**Scale/Scope**: One answer graph, ingestion worker and evaluation harness in the first increment

## Constitution Check

- Privacy and evidence-first principles pass: external traces are content-minimized.
- Provider portability passes: graph nodes depend on an internal tracing port, not SDK details.
- Testability passes: no-op/fake clients cover offline paths.

## Project Structure

```text
apps/backend/src/atlas/observability/
├── langsmith.py             # optional client and safe run context
├── context.py               # existing request correlation
├── telemetry.py             # existing OpenTelemetry helpers
└── structured.py            # existing redacted logs
apps/backend/tests/unit/observability/
├── test_langsmith.py
└── test_trace_redaction.py
evals/
├── datasets/                # versioned examples and metadata
└── run_langsmith.py         # opt-in online evaluation entrypoint
docs/operations/
└── langsmith-runbook.md
```

**Structure Decision**: Extend existing backend observability; keep evaluation execution in a
separate `evals/` environment and never make the web request depend on it.

