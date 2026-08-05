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
