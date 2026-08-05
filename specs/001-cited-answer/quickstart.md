# Quickstart Validation: Verifiable Cited Answer

This guide is the runnable acceptance path for `001-cited-answer`. Commands describe the planned
repository interface and become executable during `$speckit-implement`.

## Prerequisites

- Git
- Python 3.13.x
- `uv`
- Node.js 24 LTS
- `pnpm`
- Docker with Compose
- An OpenAI API key with access to `gpt-5.6-luna` and `text-embedding-3-small`

The real API key stays in an untracked local environment file or deployment secret manager. Tests
use fakes by default and MUST NOT require a paid model call.

## 1. Configure the local environment

```powershell
Copy-Item .env.example .env.local
```

Set the documented local-only variables:

```text
OPENAI_API_KEY=<secret>
ATLAS_VISITOR_HMAC_SECRET=<random local secret>
ATLAS_OPERATOR_TOKEN=<random local secret>
DATABASE_URL=postgresql+psycopg://atlas:atlas@localhost:5432/atlas
WEB_ORIGIN=http://localhost:3000
API_ORIGIN=http://localhost:8000
```

Never commit `.env.local`.

## 2. Install locked dependencies

```powershell
uv sync --project apps/backend --frozen
pnpm install --frozen-lockfile
```

## 3. Start local infrastructure and migrate

```powershell
docker compose up -d postgres
uv run --project apps/backend alembic upgrade head
```

Expected result: PostgreSQL is healthy; required extensions, tables, functions, roles, and indexes
exist; migrations are at the repository head.

## 4. Seed the three allowlisted collections

Before enabling a collection, confirm that its review in `docs/governance/source-reviews/` records
the exact terms, robots policy, licensing basis, allowed fetch paths, required attribution, reviewer,
review date, and re-review trigger. A missing, failed, or expired review keeps that collection
disabled.

```powershell
uv run --project apps/backend atlas-ingest seed-collections
uv run --project apps/backend atlas-ingest enqueue --collection langgraph
uv run --project apps/backend atlas-ingest enqueue --collection langchain
uv run --project apps/backend atlas-ingest enqueue --collection openai
uv run --project apps/backend atlas-worker --until-empty
```

Expected result:

- all three ingestion runs reach `succeeded` or an explicitly diagnosed `partial` state;
- a corpus snapshot is created;
- the previous active version remains current if any source item fails;
- no URL outside the connector allowlists is fetched.

## 5. Run the API and web app

In terminal 1:

```powershell
uv run --project apps/backend uvicorn atlas.api.main:app --reload --host 127.0.0.1 --port 8000
```

In terminal 2:

```powershell
pnpm --filter @atlas/web dev
```

Confirm the API contract and dependency state:

```powershell
Invoke-RestMethod http://localhost:8000/healthz
```

Expected result: the endpoint returns a stable request identifier and a ready status when PostgreSQL
is available. Contract tests also verify a controlled degraded response without credentials, raw
exceptions, or other internal details when a required dependency is unavailable.

Open `http://localhost:3000` and confirm the corpus panel lists LangGraph, LangChain, and OpenAI with
their source types and last successful refresh times.

## 6. Validate the primary cited-answer journey

Ask a supported question, for example:

```text
When does a LangGraph workflow need a checkpointer, and what capabilities does it enable?
```

Expected result:

1. The UI announces search, composition, and citation verification progress.
2. No draft answer text appears before verification completes.
3. The final answer contains principal claims with navigable citations.
4. Opening a citation displays publisher, canonical URL, excerpt, capture date, source type, and any
   known version/date metadata.
5. The source link opens the canonical official page.

## 7. Validate invalid input and explicit cancellation

Submit an empty question, punctuation-only text, an over-limit question, and several unrelated
questions in one request. Verify that every case receives a useful correction, does not consume
answer quota or call the model, and leaves the original text available for editing.

Start a valid answer, use the visible cancel control, and verify that
`DELETE /v1/answers/{run_id}` reaches a terminal cancelled state. Repeating the same cancellation
must be safe, and disconnecting the answer stream must also cancel active processing.

## 8. Validate temporal evidence

Ask a prepared question from the versioned temporal dataset, then verify that changelog or release
evidence includes the relevant chronology or version. The answer MUST expose disagreement when two
official records conflict.

## 9. Validate abstention and prompt-injection resistance

Run the prepared unsupported and malicious-source cases:

```powershell
uv run --project apps/backend pytest -m "abstention or prompt_injection"
```

Expected result: unsupported questions abstain; source text cannot authorize tools, change the
system policy, or create a citation that was not in the retrieved evidence set.

## 10. Validate anonymous quota

Submit 11 valid questions using one anonymous visitor cookie and distinct idempotency keys.

Expected result:

- requests 1-10 are accepted;
- request 11 returns HTTP 429 before retrieval/model execution;
- `Retry-After` and `retry_at` identify the earliest valid retry time;
- retrying an accepted idempotency key does not consume another quota unit;
- reports/documents are absent from this feature and do not interact with this quota.

## 11. Validate refresh atomicity

Force a connector fixture to fail after a prior version is active, then run the worker.

Expected result: the ingestion item/run records the controlled failure, the old source version stays
active, and answers continue to cite the last successful version.

## 12. Validate 30-day retention

Use the test clock/fixture to age selected answer content past 30 days, run retention, and verify:

- question, answer, claims, detailed feedback, selected-evidence links, and diagnostic content are
  deleted within the additional 24-hour window;
- no visitor hash or run ID is copied to aggregate metrics;
- aggregate counts, latency totals, token totals, cost totals, and quality counts remain correct;
- corpus documents and evidence are unaffected.

## 13. Validate external usability

Follow `docs/research/001-cited-answer-usability-protocol.md` with five consenting external
participants who did not build ATLAS. Without guidance, each participant must attempt to ask a
supported question, inspect its evidence, and identify whether the result was verified or an
abstention. Record only non-identifying observations in
`evals/results/001-cited-answer-usability.md`.

Expected result: at least four of five participants complete all three critical actions. Record a
follow-up defect for every critical failure rather than changing the criterion after observing the
results.

## 14. Validate seven days of scheduled refreshes

For seven consecutive launch-validation days, retain ingestion-run metadata for every scheduled
LangGraph, LangChain, and OpenAI collection refresh. Record expected runs, successful runs,
controlled failures, last-success preservation checks, and timestamps in
`evals/results/001-cited-answer-refresh-7d.md`.

Expected result: at least 95% of scheduled refreshes succeed in aggregate and per-collection
failures preserve the last successfully promoted version. The report must distinguish skipped or
missing schedules from attempted failures instead of counting them as successes.

## 15. Run quality gates

```powershell
uv run --project apps/backend ruff check .
uv run --project apps/backend mypy src tests
uv run --project apps/backend pytest
pnpm lint
pnpm typecheck
pnpm test
pnpm exec playwright test
```

Database contract tests:

```powershell
uv run --project apps/backend pytest -m database
```

Offline evaluation:

```powershell
uv run --project apps/backend atlas-eval run --dataset evals/datasets/cited-answer-v1.jsonl
```

The feature cannot be marked complete unless the run records and meets the thresholds in
[spec.md](./spec.md), including citation precision, abstention, temporal correctness, latency, and
prompt-injection cases.

## Contract references

- Public/operator HTTP interface: [contracts/openapi.yaml](./contracts/openapi.yaml)
- Streaming behavior: [contracts/answer-events.md](./contracts/answer-events.md)
- Persistence and retention: [data-model.md](./data-model.md)
