# Data Model: Production Deployment

## DeploymentEnvironment

Represents one isolated deploy target.

| Field | Type | Rules |
|---|---|---|
| `name` | enum | `preview`, `staging`, or `production` |
| `web_origin` | URL | HTTPS outside local development; exact origin, no path |
| `api_origin` | URL | HTTPS outside local development; exact origin, no path |
| `database_target` | identifier | Must not be shared with another environment |
| `migration_head` | revision | Must equal the release evidence revision after migration |
| `corpus_snapshot` | version | Must be recorded for research behavior |
| `model_router_version` | version | Must be recorded for model/cost attribution |
| `locale_catalog_version` | version | Must be recorded for bilingual UI attribution |
| `observability_namespace` | identifier | Separate LangSmith project/tags and log fields |
| `status` | enum | `candidate`, `healthy`, `degraded`, `rolled_back` |

## ReleaseEvidenceBundle

Immutable evidence produced for one release candidate or deployed revision.

| Field | Type | Rules |
|---|---|---|
| `release_id` | identifier | Unique and stable for the release |
| `source_revision` | commit | Required; must match the built source |
| `web_build_id` | identifier | Required for Vercel deployment |
| `api_image_digest` | digest | Required for managed container deployment |
| `migration_revision` | revision | Required and verified by readiness |
| `checks` | list | Each required check has name, status, URL/log reference, timestamp |
| `smoke_results` | list | Must include locale, answer, comparison, report, news, auth/privacy paths |
| `health` | object | `healthz`, readiness, database, and provider results |
| `redaction_version` | version | Identifies sensitive-data filtering rules |
| `created_at` | timestamp | UTC |

## SecretBoundary

Defines where sensitive values may exist.

- Browser-visible: only public API origin, public Supabase client settings if used by the auth flow, and non-sensitive feature flags.
- Server-only: model-provider keys, LangSmith keys, database URLs/passwords, Supabase service-role key, storage signing secrets, and worker credentials.
- Forbidden: source control, client bundles, user-visible errors, structured logs, traces, evaluation artifacts, and release summaries.

## MigrationRelease

Tracks a forward migration execution.

- `from_revision`
- `to_revision`
- `environment`
- `started_at`
- `completed_at`
- `status`
- `compatibility_note`
- `operator_or_workflow_id`

The state transition is `candidate -> applying -> applied -> verified`; failure transitions to
`failed` and blocks traffic promotion.
