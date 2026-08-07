# Deployment Readiness Contract v1

## Health endpoint

`GET /healthz`

The endpoint returns HTTP 200 only when the process is alive. It must never claim database or
provider readiness unless the response body reports those checks truthfully.

## Readiness endpoint

`GET /readyz`

The endpoint returns HTTP 200 only when the configured database, migration head, and required
runtime dependencies are available. A dependency failure returns a non-2xx status and a stable
machine-readable error category without secrets.

## Required response fields

```json
{
  "status": "ready|degraded|unavailable",
  "environment": "preview|staging|production",
  "release_id": "string",
  "source_revision": "string",
  "migration_revision": "string",
  "checks": {
    "database": "ready|failed",
    "migrations": "ready|failed|unknown",
    "model_provider": "ready|degraded|disabled",
    "observability": "ready|degraded"
  }
}
```

## Smoke contract

The deployed smoke runner must verify:

1. `GET /healthz` and `GET /readyz`.
2. Corpus status and provenance metadata.
3. One cited answer that either passes evidence verification or abstains truthfully.
4. One comparator request with evidence IDs mapped to the returned catalog.
5. One report request with a retained artifact reference.
6. Previous-day news behavior with explicit no-evidence handling.
7. Anonymous quota and authenticated ownership paths in an isolated test tenant.
8. Spanish and English web routes, including API CORS and locale selection.

The runner must fail on a network error, an unexpected 2xx/4xx contract, missing evidence IDs,
localhost origins, exposed-secret markers, or a response that claims verification without evidence.
