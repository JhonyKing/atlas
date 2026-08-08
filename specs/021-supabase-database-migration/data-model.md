# Data Model: Supabase Migration Evidence

## MigrationEvidence

Represents one migration verification/apply run without private row content.

| Field | Type | Rules |
|---|---|---|
| `run_id` | UUID/string | Required, unique per run |
| `project_ref` | string | Must equal `fcbclsaytbjpywlaplbh` |
| `environment` | enum | `development`, `staging`, or `production`; production gates writes |
| `mode` | enum | `inspect`, `apply`, or `verify` |
| `started_at` / `finished_at` | datetime | UTC timestamps |
| `repository_head` | string | Commit identifier used for the run |
| `repository_revisions` | string[] | Ordered revision IDs expected by the repository |
| `remote_revisions` | string[] | Ordered revision IDs reported by Supabase |
| `applied_revisions` | string[] | Revisions applied in this run |
| `schema_inventory` | object | Counts/names of tables, functions, indexes, policies, and extensions |
| `checks` | object[] | Named check, status, elapsed time, and bounded detail |
| `drift` | object[] | Exact non-secret differences, if any |
| `status` | enum | `passed`, `failed`, `blocked`, or `drift_detected` |

## DriftFinding

Describes one difference between the repository contract and the remote project.

- `kind`: `revision`, `table`, `function`, `index`, `policy`, `extension`, or `seed`
- `object_name`: bounded identifier, never row content
- `expected`: expected version/name/state
- `actual`: observed version/name/state
- `severity`: `blocking`, `warning`, or `informational`
- `resolution`: review note or migration identifier

## Relationships

- One `MigrationEvidence` contains zero or more `DriftFinding` records.
- One `MigrationEvidence` references many ordered repository revisions.
- One check may reference one schema object or a bounded aggregate count.
- Evidence artifacts never contain credentials, access tokens, passwords, or private row payloads.
