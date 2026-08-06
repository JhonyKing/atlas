# Data Model: Evidence-backed Research Reports

## ReportSpec

| Field | Rule |
|---|---|
| `source_run_id` | Required UUID of a completed comparison run owned by the visitor |
| `report_type` | `comparison`, `architecture_brief`, `adr`, `release_intelligence`, or `research` |
| `locale` | `en-US` or `es-MX` |
| `audience` | Non-empty bounded text |
| `scope` | Non-empty bounded text describing the requested report scope |
| `criteria` | Ordered list of selected comparison criteria |
| `required_sections` | Ordered unique section keys |
| `format` | `docx` or `pdf` |
| `idempotency_key` | Visitor-scoped repeat-safe key |

## ReportJob

States: `accepted → planning → rendering → completed`; failure paths are `failed`, `cancelled`,
`expired`, and `deleted`. A terminal state cannot be changed except an idempotent repeated delete.

Required metadata: `id`, `source_run_id`, `visitor_key_hash`, `request_id`, `status`, timestamps,
`corpus_snapshot_id`, `model_id`, `prompt_version`, `report_spec_hash`, `error_code`, and
`expires_at`.

## ReportSection

Fields: `key`, `title`, `ordinal`, `narrative`, `claims`, `limitations`, and `citation_ids`.
Every factual claim must reference one or more evidence IDs from the source run. Unsupported
material is represented as a limitation, not as an uncited assertion.

## ReportDocument

Fields: `job_id`, `format`, `storage_key`, `content_sha256`, `byte_size`, `media_type`, `created_at`,
`expires_at`, and `citation_manifest`. Storage keys are internal and never returned to visitors.

## Invariants

- A report job cannot complete without at least one validated section and one citation manifest.
- A document cannot be downloaded unless its job is `completed`, not expired, and owned by the
  requesting visitor.
- Reusing an idempotency key with a different normalized `ReportSpec` is a conflict.
- English and Spanish jobs derived from one source run preserve identical evidence IDs, canonical
  URLs, and original excerpts.
