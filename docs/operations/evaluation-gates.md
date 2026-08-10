# Evaluation gates

Deterministic cited-answer and RAG regression evaluations run in CI and are required before a
release is promoted. A live provider or LangSmith evaluation is not substituted by the offline
gate: it is retained as separate evidence with model, corpus, locale, latency, token, and cost
metadata. A live failure blocks the release owner from declaring the environment production-ready.
