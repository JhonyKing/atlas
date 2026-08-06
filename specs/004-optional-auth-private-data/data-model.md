# Data Model: Optional Authentication and Private Data

## User

- `id`: UUID primary key
- `auth_subject`: provider-neutral subject identifier, unique
- `locale`: `en-US` or `es-MX`
- `created_at`, `updated_at`, `deleted_at`

## Session

- `id`: opaque server-side session identifier
- `user_id`: owner
- `issued_at`, `expires_at`, `revoked_at`, `last_seen_at`
- `created_from`: bounded device description, never a raw token

States: `active -> expired | revoked`; revoked/expired sessions cannot authorize resources.

## OwnershipGrant

- `user_id`, `resource_type`, `resource_id`
- `created_at`, `deleted_at`

The pair `(user_id, resource_type, resource_id)` is unique. Database policies require the current
authenticated subject to match `user_id` and exclude soft-deleted records.

## PrivateUpload

- `id`, `user_id`, `storage_key`
- `declared_type`, `detected_type`, `size_bytes`, `content_hash`
- `scan_status`: `pending | clean | rejected | error`
- `parse_status`: `pending | parsed | rejected | error`
- `retained_until`, `created_at`, `deleted_at`

Only `clean + parsed` files may produce private chunks/embeddings. No upload row may be promoted to
the public corpus in this feature.

## DeletionJob

- `id`, `requested_by`, `subject_user_id`
- `scope`: `upload | resource | account`
- `status`: `accepted | deleting | completed | failed`
- `idempotency_key`, `requested_at`, `completed_at`, `error_code`

Deletion is repeat-safe. A completed job never restores access, and audit metadata excludes raw
tokens, private excerpts, and storage credentials.

