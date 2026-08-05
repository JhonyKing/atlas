# Research: LangSmith Quality Observability

## Decisions

- Use the current LangSmith environment names `LANGSMITH_TRACING`, `LANGSMITH_API_KEY`,
  `LANGSMITH_PROJECT`, and optional endpoint/workspace settings. The SDK supports hiding inputs and
  outputs, which matches the ATLAS privacy default.
- Keep OpenTelemetry as the local baseline and put LangSmith behind an internal port/no-op sink.
- Use LangSmith datasets, experiments, feedback and annotation queues only for opt-in quality work;
  CI remains offline and deterministic.

## Sources

- https://docs.langchain.com/langsmith/create-account-api-key
- https://docs.langchain.com/langsmith/trace-without-env-vars
- https://docs.langchain.com/langsmith/evaluation-concepts
- https://docs.langchain.com/langsmith/annotation-queues

