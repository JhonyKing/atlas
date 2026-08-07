"""Add governed collection, version, policy, run, and coverage persistence."""

from alembic import op
import sqlalchemy as sa


revision = "0022_ingestion_governance"
down_revision = "0021_private_upload_provenance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.governed_collections (
              slug text PRIMARY KEY,
              display_name text NOT NULL,
              publisher text NOT NULL,
              kind text NOT NULL CHECK (kind IN ('framework','model_provider')),
              allowed_hosts text[] NOT NULL CHECK (cardinality(allowed_hosts) > 0),
              allowed_paths text[] NOT NULL CHECK (cardinality(allowed_paths) > 0),
              refresh_interval_hours integer NOT NULL CHECK (refresh_interval_hours BETWEEN 6 AND 24),
              ttl_hours integer NOT NULL CHECK (ttl_hours > 0),
              policy_state text NOT NULL CHECK (policy_state IN ('pending','approved','disabled','takedown')),
              reviewer text,
              reviewed_at timestamptz,
              created_at timestamptz NOT NULL DEFAULT now()
            );
            CREATE TABLE IF NOT EXISTS atlas.governed_sources (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              collection_slug text NOT NULL REFERENCES atlas.governed_collections(slug),
              canonical_url text NOT NULL CHECK (canonical_url LIKE 'https://%'),
              title text NOT NULL,
              author_or_org text,
              license text,
              published_at timestamptz,
              captured_at timestamptz NOT NULL,
              content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
              current_version_id uuid,
              state text NOT NULL CHECK (state IN ('current','stale','disabled')),
              last_update_outcome text NOT NULL,
              private_owner_id uuid REFERENCES atlas.users(id),
              UNIQUE (collection_slug, canonical_url)
            );
            CREATE TABLE IF NOT EXISTS atlas.governed_source_versions (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              source_id uuid NOT NULL REFERENCES atlas.governed_sources(id) ON DELETE CASCADE,
              parent_version_id uuid REFERENCES atlas.governed_source_versions(id),
              normalized_markdown text NOT NULL,
              content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
              version_label text,
              captured_at timestamptz NOT NULL,
              status text NOT NULL CHECK (status IN ('staged','active','superseded','rejected')),
              UNIQUE (source_id, content_sha256)
            );
            ALTER TABLE atlas.governed_sources
              ADD CONSTRAINT governed_sources_current_version_fk
              FOREIGN KEY (current_version_id) REFERENCES atlas.governed_source_versions(id)
              ON DELETE RESTRICT;
            CREATE TABLE IF NOT EXISTS atlas.governance_policy_reviews (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              source_id uuid REFERENCES atlas.governed_sources(id) ON DELETE CASCADE,
              collection_slug text REFERENCES atlas.governed_collections(slug),
              robots_status text NOT NULL,
              terms_status text NOT NULL,
              license_status text NOT NULL,
              approval_status text NOT NULL,
              reviewer text,
              reviewed_at timestamptz NOT NULL DEFAULT now(),
              decision_reason text NOT NULL
            );
            CREATE TABLE IF NOT EXISTS atlas.governance_connector_runs (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              collection_slug text NOT NULL REFERENCES atlas.governed_collections(slug),
              trigger text NOT NULL CHECK (trigger IN ('scheduled','operator')),
              status text NOT NULL CHECK (status IN ('running','succeeded','retrying','dead_letter','failed')),
              attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
              latency_ms integer CHECK (latency_ms IS NULL OR latency_ms >= 0),
              error_code text,
              started_at timestamptz NOT NULL DEFAULT now(),
              completed_at timestamptz
            );
            CREATE TABLE IF NOT EXISTS atlas.governance_coverage_snapshots (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              captured_at timestamptz NOT NULL DEFAULT now(),
              seven_day_window_start timestamptz NOT NULL,
              metrics jsonb NOT NULL,
              manifest_sha256 char(64) NOT NULL CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$')
            );
            CREATE INDEX IF NOT EXISTS governed_sources_collection_state_idx
              ON atlas.governed_sources(collection_slug, state, captured_at DESC);
            CREATE INDEX IF NOT EXISTS governed_versions_source_status_idx
              ON atlas.governed_source_versions(source_id, status, captured_at DESC);
            REVOKE ALL ON atlas.governed_collections, atlas.governed_sources,
              atlas.governed_source_versions, atlas.governance_policy_reviews,
              atlas.governance_connector_runs, atlas.governance_coverage_snapshots FROM PUBLIC;
            GRANT SELECT ON atlas.governed_collections, atlas.governed_sources,
              atlas.governed_source_versions, atlas.governance_policy_reviews,
              atlas.governance_connector_runs, atlas.governance_coverage_snapshots TO atlas_readonly;
            GRANT SELECT, INSERT, UPDATE ON atlas.governed_collections, atlas.governed_sources,
              atlas.governed_source_versions, atlas.governance_policy_reviews,
              atlas.governance_connector_runs, atlas.governance_coverage_snapshots TO atlas_worker;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DROP TABLE IF EXISTS atlas.governance_coverage_snapshots;
            DROP TABLE IF EXISTS atlas.governance_connector_runs;
            DROP TABLE IF EXISTS atlas.governance_policy_reviews;
            ALTER TABLE IF EXISTS atlas.governed_sources DROP CONSTRAINT IF EXISTS governed_sources_current_version_fk;
            DROP TABLE IF EXISTS atlas.governed_source_versions;
            DROP TABLE IF EXISTS atlas.governed_sources;
            DROP TABLE IF EXISTS atlas.governed_collections;
            """
        )
    )
