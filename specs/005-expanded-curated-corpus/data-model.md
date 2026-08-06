# Data Model: Expanded Curated Corpus

## GovernedCollection

- `slug`: stable governed identifier
- `display_name`, `publisher`, `kind`: framework or model provider
- `allowed_hosts`, `allowed_paths`: approved destination boundary
- `refresh_interval_hours`, `ttl_hours`: operational freshness policy
- `policy_state`: pending, approved, disabled, takedown
- `reviewer`, `reviewed_at`: human review metadata

## GovernedSource

- `source_id`, `collection_slug`, `canonical_url`, `title`
- `author_or_org`, `license`, `published_at`, `captured_at`
- `content_sha256`, `current_version_id`, `state`, `last_update_outcome`
- `private_owner_id` when the source is authorized private content

## SourceVersion

- Immutable `version_id`, `source_id`, `parent_version_id`
- `normalized_markdown`, `content_sha256`, `version_label`
- `captured_at`, `source_updated_at`, `valid_from`, `valid_to`
- `status`: staged, active, superseded, rejected

## ConnectorRun

- `run_id`, `collection_slug`, `trigger`, `status`, `attempt_count`
- `requested_at`, `started_at`, `completed_at`, `latency_ms`, `error_code`
- `discovered_count`, `changed_count`, `failed_count`, `dead_letter_count`

## PolicyReview

- `source_id`, `robots_status`, `terms_status`, `license_status`, `approval_status`
- `reviewer`, `reviewed_at`, `decision_reason`, `correction_or_takedown_id`

## CoverageSnapshot

- `captured_at`, `seven_day_window_start`
- Per collection: source count, fresh/stale count, disabled count, retry count, dead-letter count
- `coverage_percent`, `freshness_percent`, `manifest_sha256`
