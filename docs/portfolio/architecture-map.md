# ATLAS portfolio architecture map

ATLAS is an evidence-first agentic research system. The request enters a typed agent graph, selects
retrieval constraints, obtains versioned evidence, generates a cited draft through provider ports,
verifies citations, and pauses for human review before reports or consequential publication.

Cross-cutting controls include multilingual UI, optional auth/private ownership, ingestion governance,
LangSmith/OpenTelemetry-safe traces, model routing with GPT-5.6 Luna default, SLO gates and a
deterministic evaluation loop. Each feature has its own SpecKit branch, tasks, evidence and ADRs.
