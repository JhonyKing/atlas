# Runbook: corpus freshness and refresh

## Observe public status

```powershell
Invoke-WebRequest http://127.0.0.1:8000/v1/corpus | Select-Object -ExpandProperty Content
```

Each supported collection must be present. `ready` means the last successful ingestion is within
its refresh interval, `stale` means it is older, `refreshing` means a queued/running attempt exists,
and `unavailable` means there is no successful version to cite.

## Trigger an operator refresh

Use the bearer token configured in `ATLAS_OPERATOR_TOKEN` and a unique idempotency key:

```powershell
Invoke-WebRequest -Method Post `
  -Uri http://127.0.0.1:8000/v1/operator/ingestion-runs `
  -Headers @{ Authorization = "Bearer $env:ATLAS_OPERATOR_TOKEN"; "Idempotency-Key" = "local-refresh-langgraph-001" } `
  -ContentType "application/json" -Body '{"collection":"langgraph"}'
```

A failed run preserves the previously active source version. Review the ingestion status and source
review decision before enabling a connector; a connector must never become active by accident.

## Scheduled production refresh

Vercel invokes one daily route per approved collection. Configure the platform secret `CRON_SECRET`
and let Vercel provide the `Authorization: Bearer <CRON_SECRET>` header; do not put the value in
`vercel.json` or the repository. The routes are:

```text
GET /v1/operator/ingestion-cron/langgraph
GET /v1/operator/ingestion-cron/langchain
GET /v1/operator/ingestion-cron/openai
GET /v1/operator/ingestion-cron/anthropic
GET /v1/operator/ingestion-cron/gemini
```

Each route uses one UTC-date idempotency key and drains at most one collection run. A repeated
delivery returns the existing run rather than creating a duplicate. Inspect the returned `status`,
`attempt_count`, `discovered_count`, and `promoted_count`; then use the normal status endpoint for
operator diagnostics. The endpoint is intentionally not a manual replacement for the operator
route and never returns document contents.

## Provider expansion order

The combined expansion manifest preserves the initial three collections and adds Anthropic first
and Gemini second:

```powershell
atlas-corpus-bootstrap --manifest corpus/manifests/expansion-v1.yaml
```

The manifest is approved after the source-review records were completed. Its promoted snapshot
contains 20 official sources across five collections. Future host/path changes require a new review.
