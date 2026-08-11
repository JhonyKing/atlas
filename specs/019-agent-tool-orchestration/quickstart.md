# Agent Tool Orchestration Quickstart

This validates the local agent workspace and contracts. It does not require a live provider for
deterministic contract tests; live mode must be labelled explicitly.

## Start local dependencies

```powershell
docker compose up -d
```

Start the API and web application using the repository's existing commands. Verify:

```powershell
Invoke-WebRequest http://localhost:8000/healthz
Invoke-WebRequest http://localhost:3000/
```

## Contract checks

From the root:

```powershell
pnpm lint
pnpm typecheck
pnpm test
pnpm test:e2e
```

From `apps/backend`:

```powershell
.venv\Scripts\python.exe -m pytest tests/contract tests/unit/agent tests/security/test_agent_orchestration.py
```

## Manual tool journey

1. Open `http://localhost:3000/` and select the agent workspace.
2. Choose `cited_answer`, enter a technical question, and submit.
3. Confirm the plan is shown before execution and the final result contains evidence or an explicit abstention.
4. Choose `comparison`, `report`, `daily_news`, and `corpus_status`; confirm each run uses the same registry/event timeline.
5. Choose a private/delete/publish action; confirm the approval card displays the normalized target and expires; reject it and verify no mutation.
   Confirm the browser sends one operation-level `Idempotency-Key` for plan, approval, and run.
   Reusing another key for the approval or run must fail; an exact replay must not spend another
   side-effect quota unit.
6. Disconnect/reload during a read-only run and resume using the displayed run ID; confirm no duplicate call.
7. Inspect LangSmith/OpenTelemetry metadata if configured; confirm tool ID/version, run ID, locale,
   corpus, latency, cost, and outcome are present and content/secrets are redacted.

## Required evidence

- Tool catalog response and version.
- Plan JSON with plan hash and approval requirements.
- Ordered run-event stream for success, abstention, failure, cancellation, and resume.
- Evidence/artifact mapping for answer, comparison, report, and news.
- Approval/rejection/idempotency evidence for private and mutation tools.
- Quota exhaustion evidence (`429`, `Retry-After`, rejected tool-call record) with zero adapter execution.
- Deterministic evaluation summary with execution mode; live traces kept separate.
