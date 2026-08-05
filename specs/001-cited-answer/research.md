# Research: Verifiable Cited Answer

**Date**: 2026-08-04

**Scope**: Technical decisions required to plan `001-cited-answer`. Primary official documentation
was used for framework, provider, database, and runtime claims.

## 1. Application Topology

**Decision**: Use a modular monolith in one repository with Next.js web, FastAPI API, and a Python
worker that share one backend package and one Supabase PostgreSQL database.

**Rationale**: The API needs long-lived async streaming and connection pooling. Ingestion needs a
durable worker boundary, but retrieval and agent logic do not justify separate network services.
This topology keeps deployment and debugging small while preserving module seams.

**Alternatives considered**:

- Serverless-only backend: rejected because streaming, database pools, and durable ingestion become
  provider-specific and harder to test locally.
- Microservices or Kubernetes: rejected because the launch load and team size do not justify them.
- Browser-to-Supabase writes: rejected because OpenAI, ingestion, and administrative privileges must
  stay server-side.

**Sources**: [Next.js deployment](https://nextjs.org/docs/app/getting-started/deploying),
[FastAPI containers](https://fastapi.tiangolo.com/deployment/docker/),
[Supabase connections](https://supabase.com/docs/guides/database/connecting-to-postgres)

## 2. Runtime and Dependency Policy

**Decision**: Pin Python 3.13.x and Node.js 24 LTS patch versions in containers/tool files. Use the
current Next.js 16.2 line. Declare compatible direct dependency ranges and commit exact `uv` and
`pnpm` lock resolutions.

**Rationale**: Python 3.13 is in bugfix support and Node 24 is LTS at planning time. Lockfiles make
portfolio builds reproducible without copying stale package versions into architecture documents.

**Alternatives considered**:

- Python 3.12: supported by the constitution but now security-fixes-only; retain only if a required
  dependency blocks 3.13.
- Unpinned `latest`: rejected because it breaks reproducibility and evaluation baselines.

**Sources**: [Python support status](https://devguide.python.org/versions/),
[Node releases](https://nodejs.org/en/about/previous-releases),
[Next.js 16 upgrade guide](https://nextjs.org/docs/app/guides/upgrading/version-16)

## 3. LangGraph Use and Shape

**Decision**: Use a small Graph API `StateGraph`, not `create_agent`: validate, retrieve, evidence
gate, compose structured claims, deterministic citation verification, finalize or abstain. Use a
`TypedDict` state and inject clients through runtime context.

**Rationale**: Conditional evidence and verification gates are visible, independently testable, and
valuable in a portfolio. A tool-selecting autonomous loop would add variability without improving
the controlled corpus workflow.

**Alternatives considered**:

- Plain Python pipeline: adequate but provides less explicit topology and future branching support.
- Functional API: concise, but the Graph API better communicates this feature's controlled paths.
- Dynamic agent: rejected because the model must never decide which external sources or tools to use.

**Sources**: [Choosing LangGraph APIs](https://docs.langchain.com/oss/python/langgraph/choosing-apis),
[Workflows and agents](https://docs.langchain.com/oss/python/langgraph/workflows-agents),
[Graph API](https://docs.langchain.com/oss/python/langgraph/graph-api)

## 4. Graph Persistence and Streaming

**Decision**: Execute the first slice asynchronously without a durable LangGraph checkpointer.
Persist the ATLAS run, selected evidence, claims, citations, and metrics in domain tables. Use an
in-memory saver only in graph tests. Emit progress events from `astream`, but withhold answer text
until the citation gate passes.

**Rationale**: Durable checkpoints are designed for memory, HITL, resume, time travel, and failure
recovery. The one-shot anonymous answer has none of those requirements, and checkpoint snapshots
would duplicate content subject to the 30-day deletion policy.

**Alternatives considered**:

- `AsyncPostgresSaver`: deferred to a report/HITL feature; use `run_id` as `thread_id` if activated.
- Token streaming: deferred because provisional claims could be visible before citation validation.

**Sources**: [LangGraph persistence](https://docs.langchain.com/oss/python/langgraph/persistence),
[LangGraph streaming](https://docs.langchain.com/oss/python/langgraph/streaming)

## 5. OpenAI Model and API

**Decision**: Use the official async Python SDK and Responses API through an `AnswerGenerator` port
and `OpenAIResponsesAdapter`. Set the exact model slug `gpt-5.6-luna`, standard mode, and
`reasoning.effort="medium"` as the first baseline. Use `store=false`, no `previous_response_id`, and
`reasoning.context="current_turn"`.

**Rationale**: Luna is documented for cost-sensitive, high-volume workloads. `gpt-5.6` is not an
equivalent shortcut because it routes to Sol. Stateless calls align with anonymous questions,
local 30-day retention, and reproducible evaluations.

**Alternatives considered**:

- `low` effort: mandatory comparison candidate if latency/cost miss the SLO.
- `high` effort or Terra: evaluation candidates when citation semantics miss quality targets.
- Chat Completions: rejected for this new reasoning/structured-output integration.

**Sources**: [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna),
[GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/latest-model),
[Conversation state](https://developers.openai.com/api/docs/guides/conversation-state),
[OpenAI Python SDK](https://github.com/openai/openai-python)

## 6. Structured Model Output and Safety Boundary

**Decision**: Parse the response into a Pydantic `AnswerDraft` containing answer/abstain status,
claims, opaque evidence IDs, and caveats. Reject drafts with unknown evidence IDs, unsupported
principal claims, duplicate/orphan citations, or source metadata supplied by the model. URLs,
titles, dates, versions, and excerpts always come from PostgreSQL.

**Rationale**: Structured Outputs provides schema adherence, not semantic truth. ATLAS retains
ownership of evidence identity and release gates. Retrieved pages are untrusted content and the
model receives no tools during answer generation.

**Alternatives considered**:

- Free-form Markdown: rejected because claims and citations cannot be reliably audited.
- Model-created URLs/citation labels: rejected because it enables fabricated evidence.
- Repair loop: deferred; the safe baseline abstains after a failed gate and measures the failure.

**Source**: [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs)

## 7. Embeddings and Hybrid Retrieval

**Decision**: Use `text-embedding-3-small` at 1,536 dimensions. Build a deterministic PostgreSQL
hybrid function with English full-text search plus exact cosine vector search, then combine ranks
with reciprocal-rank fusion. Retrieve top candidates separately and return at most eight deduplicated
evidence excerpts after product/source/version/date filters.

**Rationale**: Full-text search preserves exact versions and product tokens; embeddings recover
semantic matches. RRF combines rank positions without pretending the raw scores are comparable.
Exact vector search provides a trustworthy recall baseline for the initial small corpus.

**Alternatives considered**:

- `text-embedding-3-large`: only if measured retrieval quality warrants reindexing and extra cost.
- HNSW: only after corpus size or p95 latency demonstrates need; exact search remains ground truth.
- Vector-only search, reranking, and LLM query rewriting: rejected from the baseline so improvements
  can be measured individually.

**Sources**: [OpenAI embeddings](https://developers.openai.com/api/docs/guides/embeddings),
[PostgreSQL text search](https://www.postgresql.org/docs/current/textsearch-tables.html),
[pgvector](https://github.com/pgvector/pgvector),
[Supabase hybrid search](https://supabase.com/docs/guides/ai/hybrid-search)

## 8. Corpus Discovery and Versioning

**Decision**: Allowlist official LangGraph/LangChain documentation paths from
`docs.langchain.com/llms.txt`, official LangGraph/LangChain repository releases, and OpenAI developer
documentation links from `developers.openai.com/llms.txt`. Prefer official Markdown/MDX or APIs;
use bounded HTML parsing only as a fallback. Store immutable document versions and promote a new
version only after normalization, chunking, embedding, and validation succeed atomically.

**Rationale**: Official machine-readable indexes reduce crawler breadth and layout fragility.
Immutable hashes and revision URLs preserve the exact basis of temporal claims.

**Alternatives considered**:

- Broad crawling/search-engine results: rejected because authority, licensing, and freshness become
  difficult to control.
- Overwriting documents in place: rejected because citations would no longer be reproducible.

**Sources**: [LangChain documentation index](https://docs.langchain.com/llms.txt),
[LangChain documentation repository](https://github.com/langchain-ai/docs),
[LangGraph releases](https://github.com/langchain-ai/langgraph/releases),
[LangChain releases](https://github.com/langchain-ai/langchain/releases),
[OpenAI documentation index](https://developers.openai.com/llms.txt)

**Implementation gate**: Each connector remains disabled until a recorded robots/terms/licensing
review in `docs/governance/source-reviews/`
confirms its exact fetch path and storage behavior. Store only the content needed for retrieval and
link every visible citation to the canonical publisher page.

## 9. Durable Daily Ingestion

**Decision**: Supabase Cron enqueues one idempotent job per collection into Supabase Queues/PGMQ.
An authenticated operator endpoint invokes the same enqueue operation. A Python worker claims jobs,
uses a per-source lock, applies bounded retries, and atomically promotes validated versions. Failed
jobs preserve the prior current version and end in a queryable failure/dead-letter state.

**Rationale**: Cron jobs remain short and the database-backed queue survives API restarts without
adding Redis/Celery. Heavy fetching and embedding do not run inside a web request.

**Alternatives considered**:

- FastAPI `BackgroundTasks`: rejected for heavy work that must survive process termination.
- In-process scheduler: rejected because replicas can duplicate jobs.
- Celery/Redis: rejected as a separate service not yet justified.

**Sources**: [Supabase Cron](https://supabase.com/docs/guides/cron),
[Supabase Queues](https://supabase.com/docs/guides/queues),
[FastAPI background tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)

## 10. Anonymous Identity, Quota, and OpenAI Safety Identifier

**Decision**: Issue a random opaque `HttpOnly`, `Secure`, `SameSite=Lax` visitor cookie. Store only
an HMAC of the token. Atomically reserve a question using a PostgreSQL transaction/advisory lock,
count accepted usage events in the previous 24 hours, and reject the 11th with HTTP 429,
`Retry-After`, and the exact retry time. Use an idempotency key so retries do not consume quota twice.
Send a separately derived HMAC as OpenAI `safety_identifier`.

**Rationale**: This implements the clarified product rule without invasive fingerprinting or raw IP
storage. A global daily model-cost circuit breaker limits cookie-reset abuse.

**Alternatives considered**:

- IP/User-Agent fingerprint: rejected on privacy and reliability grounds.
- Redis counter: rejected because PostgreSQL already owns quota events and transactional answer runs.
- Reports consuming the same quota: rejected by clarified scope; future reports get a separate policy.

**Sources**: [PostgreSQL advisory locks](https://www.postgresql.org/docs/current/explicit-locking.html),
[OpenAI safety best practices](https://developers.openai.com/api/docs/guides/safety-best-practices)

## 11. Retention and Observability

**Decision**: Every anonymous-content row has `expires_at`. A daily job first upserts non-reversible
daily counters, then cascades deletion of questions, answers, claims, detailed feedback, evidence
selection, and trace content at 30 days. Corpus content is not user content and follows source
version policy. Propagate one request ID and collect content-free OpenTelemetry spans plus structured
logs. Optional LangSmith production tracing must hide inputs/outputs and satisfy the TTL.

**Rationale**: Explicit expiry makes deletion testable while aggregate latency, error, cost, and
quality metrics remain useful. Content-free telemetry reduces accidental leakage.

**Alternatives considered**:

- Indefinite run storage: violates the clarification.
- Sending raw production prompts/evidence to every tracing backend: rejected.

**Sources**: [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/),
[LangSmith masking](https://docs.langchain.com/langsmith/mask-inputs-outputs),
[LangSmith retention](https://docs.langchain.com/langsmith/administration-overview)

## 12. Prompt Caching and Cost Accounting

**Decision**: Start without explicit cache breakpoints. Order stable instructions/schema before
dynamic evidence and question. If the stable prefix exceeds 1,024 tokens and telemetry shows reuse,
benchmark explicit caching keyed by prompt version. Record cached, cache-write, reasoning, input,
and output token classes. Calculate cost from an effective-dated local price table.

**Rationale**: GPT-5.6 cache writes are billable; enabling caching without measured reusable prefixes
can increase cost. A dated price table avoids rewriting historical run costs when prices change.

**Alternatives considered**:

- Hardcoded current price: rejected because it corrupts historical calculations.
- Always-on explicit caching: rejected until prefix reuse and net savings are measured.

**Sources**: [OpenAI prompt caching](https://developers.openai.com/api/docs/guides/prompt-caching),
[GPT-5.6 Luna pricing](https://developers.openai.com/api/docs/models/gpt-5.6-luna)

## 13. Verification and Evaluation Strategy

**Decision**: Use unit tests for nodes, provider ports, validators, chunk/version rollover, quota, and
purge logic; contract tests for Pydantic/OpenAPI/SSE; integration tests for PostgreSQL functions,
PGMQ, migrations, and adapter fixtures; opt-in real-provider smoke tests; Playwright for the three
user journeys. Keep a versioned dataset with 30 in-scope questions, at least 10 temporal cases,
unsupported/contradictory cases, and prompt-injection fixtures.

Measure Hit@k, MRR/nDCG, citation coverage, citation correctness, temporal correctness, abstention
precision/recall, latency, tokens, and cost. Tests with a real model verify schema and invariants,
not exact prose.

**Rationale**: Separating deterministic tests from probabilistic evals makes failures attributable
and lets every future retrieval/model change compare against the same baseline.

**Alternatives considered**:

- LLM-only evaluation: rejected because schemas, evidence IDs, and SQL ranking have deterministic
  invariants.
- Snapshotting full generated prose: rejected as brittle and semantically weak.

**Sources**: [Testing LangGraph](https://docs.langchain.com/oss/python/langgraph/test),
[LangSmith RAG evaluation](https://docs.langchain.com/langsmith/evaluate-rag-tutorial),
[Supabase database testing](https://supabase.com/docs/guides/local-development/testing/overview)
