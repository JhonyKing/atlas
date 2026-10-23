# Feature 002 owner review: pricing evidence

Use this checklist after the production pricing migration, ingestion, and live comparison. It is
intentionally separate from the specification-quality checklist: the implementation can pass all
local tests while the live evidence is still missing.

## Required evidence

- [ ] `comparison_pricing_contract` is applied in the target Supabase environment and the live
  migration head is recorded.
- [ ] `corpus/manifests/expansion-v3-pricing.yaml` is validated and stored as an immutable manifest
  version; the previous active snapshot remains addressable.
- [ ] A new pricing snapshot ID is recorded without replacing the previous snapshot.
- [ ] A new live comparison run ID and application commit are recorded.
- [ ] The run was executed in both `en-US` and `es-MX`, or the artifact explicitly explains why one
  locale was not run.
- [ ] Every populated price cell has an evidence ID present in the catalog with title, publisher,
  canonical URL, bounded excerpt, capture date, and version/date context.
- [ ] Every `unsupported` cell explains that reviewed pricing evidence was unavailable; no value was
  inferred from technical documentation.
- [ ] Framework-only cells are `not_applicable`, not `unsupported` and not a fabricated price.
- [ ] The conclusion is useful and bounded: it states what can be compared and what remains
  unknown, without declaring a universal winner from incomplete evidence.

## Artifact fields

Record these fields in `evals/results/comparator-pricing-live-<run-id>.json`:

| Field | Required value |
|---|---|
| `run_id` | Live comparison run identifier |
| `snapshot_id` | Immutable pricing snapshot identifier |
| `manifest_version` | Exact manifest version/hash |
| `application_commit` | Commit deployed for the run |
| `locale` | `en-US` or `es-MX` |
| `retrieval_version` | Retrieval/prompt version |
| `cells` | States, values, units, periods, and evidence IDs |
| `evidence_catalog` | Metadata for every cited evidence ID |
| `reviewed_at` | UTC timestamp |

Do not mark T047 or T048 complete until this checklist has no unchecked required item and the
artifact is retained in the repository evidence location.
