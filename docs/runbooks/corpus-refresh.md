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

## Provider expansion order

The combined expansion manifest preserves the initial three collections and adds Anthropic first
and Gemini second:

```powershell
atlas-corpus-bootstrap --manifest corpus/manifests/expansion-v1.yaml
```

The manifest is approved after the source-review records were completed. Its promoted snapshot
contains 20 official sources across five collections. Future host/path changes require a new review.

## Production Vercel Cron (owner-approved beta)

The approved low-cost production path is one Vercel Cron invocation per collection, backed by the
Supabase durable queue. The five routes are:

```text
/v1/operator/ingestion-cron/langgraph
/v1/operator/ingestion-cron/langchain
/v1/operator/ingestion-cron/openai
/v1/operator/ingestion-cron/anthropic
/v1/operator/ingestion-cron/gemini
```

Each request must include `Authorization: Bearer $CRON_SECRET` and must process only the named
collection. The idempotency key is deterministic: `cron:{manifest_version}:{UTC date}:{collection}`.
Do not invoke production manually until the secret and Cron schedule are configured in Vercel.
For an approved smoke, call one route and retain the redacted status, queue/run identifier,
collection, and captured evidence in the release bundle. A `401` means the secret boundary rejected
the request; a `503` means the dependency/readiness boundary rejected it. Neither should be hidden by
retries that remove the original evidence.
