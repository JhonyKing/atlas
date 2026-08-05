"""Create immutable corpus, ingestion, queue, and snapshot persistence."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0002_corpus_ingestion"
down_revision = "0001_foundation"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("CREATE SEQUENCE IF NOT EXISTS atlas.corpus_snapshot_revision_seq"))
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.collections (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              slug text NOT NULL UNIQUE CHECK (slug IN ('langgraph', 'langchain', 'openai')),
              display_name text NOT NULL,
              publisher text NOT NULL,
              base_url text NOT NULL CHECK (base_url LIKE 'https://%'),
              allowed_hosts text[] NOT NULL CHECK (cardinality(allowed_hosts) > 0),
              refresh_interval interval NOT NULL DEFAULT interval '24 hours',
              enabled boolean NOT NULL DEFAULT false,
              last_success_at timestamptz,
              created_at timestamptz NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS atlas.ingestion_runs (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              collection_id uuid NOT NULL REFERENCES atlas.collections(id) ON DELETE RESTRICT,
              trigger text NOT NULL CHECK (trigger IN ('scheduled', 'operator')),
              idempotency_key text NOT NULL UNIQUE,
              status text NOT NULL CHECK (
                status IN ('queued', 'running', 'succeeded', 'partial', 'failed', 'dead_letter')
              ),
              requested_by text,
              requested_at timestamptz NOT NULL DEFAULT now(),
              started_at timestamptz,
              completed_at timestamptz,
              attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
              discovered_count integer NOT NULL DEFAULT 0 CHECK (discovered_count >= 0),
              changed_count integer NOT NULL DEFAULT 0 CHECK (changed_count >= 0),
              promoted_count integer NOT NULL DEFAULT 0 CHECK (promoted_count >= 0),
              failed_count integer NOT NULL DEFAULT 0 CHECK (failed_count >= 0),
              error_code text,
              error_summary text CHECK (error_summary IS NULL OR length(error_summary) <= 500)
            );

            CREATE TABLE IF NOT EXISTS atlas.sources (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              collection_id uuid NOT NULL REFERENCES atlas.collections(id) ON DELETE RESTRICT,
              canonical_url text NOT NULL CHECK (canonical_url LIKE 'https://%'),
              source_type text NOT NULL CHECK (
                source_type IN ('documentation', 'changelog', 'release_note')
              ),
              title text NOT NULL,
              publisher text NOT NULL,
              product_area text,
              language text NOT NULL DEFAULT 'en',
              trust_tier text NOT NULL CHECK (trust_tier IN ('official_docs', 'official_repository')),
              current_version_id uuid,
              created_at timestamptz NOT NULL DEFAULT now(),
              updated_at timestamptz NOT NULL DEFAULT now(),
              UNIQUE (collection_id, canonical_url)
            );

            CREATE TABLE IF NOT EXISTS atlas.source_versions (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              source_id uuid NOT NULL REFERENCES atlas.sources(id) ON DELETE CASCADE,
              ingestion_run_id uuid NOT NULL REFERENCES atlas.ingestion_runs(id) ON DELETE RESTRICT,
              content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
              source_revision_url text CHECK (
                source_revision_url IS NULL OR source_revision_url LIKE 'https://%'
              ),
              repository text,
              repository_path text,
              commit_sha text,
              release_tag text,
              version_label text,
              published_at timestamptz,
              source_updated_at timestamptz,
              fetched_at timestamptz NOT NULL,
              valid_from timestamptz,
              valid_to timestamptz,
              etag text,
              last_modified text,
              normalized_markdown text NOT NULL,
              byte_size integer NOT NULL CHECK (byte_size > 0),
              status text NOT NULL CHECK (status IN ('staged', 'active', 'superseded', 'rejected')),
              created_at timestamptz NOT NULL DEFAULT now(),
              UNIQUE (source_id, content_sha256)
            );

            ALTER TABLE atlas.sources
              DROP CONSTRAINT IF EXISTS sources_current_version_fk;
            ALTER TABLE atlas.sources
              ADD CONSTRAINT sources_current_version_fk
              FOREIGN KEY (current_version_id) REFERENCES atlas.source_versions(id)
              ON DELETE RESTRICT;

            CREATE TABLE IF NOT EXISTS atlas.chunks (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              source_version_id uuid NOT NULL REFERENCES atlas.source_versions(id) ON DELETE CASCADE,
              parent_chunk_id uuid REFERENCES atlas.chunks(id) ON DELETE SET NULL,
              ordinal integer NOT NULL CHECK (ordinal >= 0),
              heading_path text[] NOT NULL DEFAULT '{}',
              anchor text,
              text text NOT NULL,
              text_sha256 char(64) NOT NULL CHECK (text_sha256 ~ '^[0-9a-f]{64}$'),
              token_count integer NOT NULL CHECK (token_count > 0),
              start_offset integer NOT NULL CHECK (start_offset >= 0),
              end_offset integer NOT NULL CHECK (end_offset > start_offset),
              metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
              UNIQUE (source_version_id, ordinal),
              UNIQUE (source_version_id, text_sha256, ordinal)
            );

            CREATE TABLE IF NOT EXISTS atlas.embedding_profiles (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              provider text NOT NULL,
              model text NOT NULL,
              dimensions integer NOT NULL CHECK (dimensions > 0),
              distance_metric text NOT NULL CHECK (distance_metric IN ('cosine')),
              normalization_version text NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now(),
              retired_at timestamptz,
              UNIQUE (provider, model, dimensions, normalization_version)
            );

            CREATE TABLE IF NOT EXISTS atlas.chunk_embeddings (
              chunk_id uuid NOT NULL REFERENCES atlas.chunks(id) ON DELETE CASCADE,
              embedding_profile_id uuid NOT NULL REFERENCES atlas.embedding_profiles(id) ON DELETE RESTRICT,
              embedding vector(1536) NOT NULL,
              created_at timestamptz NOT NULL DEFAULT now(),
              PRIMARY KEY (chunk_id, embedding_profile_id)
            );

            CREATE TABLE IF NOT EXISTS atlas.corpus_snapshots (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              revision bigint NOT NULL UNIQUE DEFAULT nextval('atlas.corpus_snapshot_revision_seq'),
              manifest jsonb NOT NULL,
              manifest_sha256 char(64) NOT NULL UNIQUE CHECK (manifest_sha256 ~ '^[0-9a-f]{64}$'),
              created_at timestamptz NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS atlas.ingestion_items (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              ingestion_run_id uuid NOT NULL REFERENCES atlas.ingestion_runs(id) ON DELETE CASCADE,
              canonical_url text NOT NULL CHECK (canonical_url LIKE 'https://%'),
              status text NOT NULL CHECK (status IN ('unchanged', 'promoted', 'skipped', 'failed')),
              source_version_id uuid REFERENCES atlas.source_versions(id) ON DELETE SET NULL,
              http_status integer,
              error_code text,
              created_at timestamptz NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS atlas.ingestion_queue (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              ingestion_run_id uuid NOT NULL UNIQUE REFERENCES atlas.ingestion_runs(id) ON DELETE CASCADE,
              payload jsonb NOT NULL,
              status text NOT NULL DEFAULT 'queued' CHECK (status IN ('queued', 'leased', 'done')),
              visible_at timestamptz NOT NULL DEFAULT now(),
              attempt_count integer NOT NULL DEFAULT 0 CHECK (attempt_count >= 0),
              created_at timestamptz NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS atlas.scheduled_jobs (
              name text PRIMARY KEY,
              cron_expression text NOT NULL,
              collection_slug text NOT NULL CHECK (collection_slug IN ('langgraph', 'langchain', 'openai')),
              status text NOT NULL DEFAULT 'disabled' CHECK (status IN ('enabled', 'disabled')),
              last_scheduled_at timestamptz,
              created_at timestamptz NOT NULL DEFAULT now()
            );

            CREATE INDEX IF NOT EXISTS sources_collection_idx
              ON atlas.sources(collection_id, source_type);
            CREATE INDEX IF NOT EXISTS source_versions_source_status_idx
              ON atlas.source_versions(source_id, status, fetched_at DESC);
            CREATE INDEX IF NOT EXISTS chunks_source_version_idx
              ON atlas.chunks(source_version_id, ordinal);
            CREATE INDEX IF NOT EXISTS ingestion_runs_collection_status_idx
              ON atlas.ingestion_runs(collection_id, status, requested_at DESC);
            CREATE INDEX IF NOT EXISTS ingestion_queue_visible_idx
              ON atlas.ingestion_queue(status, visible_at);
            """
        )
    )

    op.execute(
        sa.text(
            """
            DROP TRIGGER IF EXISTS sources_touch_updated_at ON atlas.sources;
            CREATE TRIGGER sources_touch_updated_at
            BEFORE UPDATE ON atlas.sources
            FOR EACH ROW EXECUTE FUNCTION atlas.touch_updated_at();

            CREATE OR REPLACE FUNCTION atlas.promote_source_version(
              p_source_id uuid,
              p_version_id uuid
            ) RETURNS void
            LANGUAGE plpgsql
            AS $$
            DECLARE old_version_id uuid;
            BEGIN
              SELECT current_version_id INTO old_version_id
              FROM atlas.sources WHERE id = p_source_id FOR UPDATE;
              IF NOT FOUND THEN
                RAISE EXCEPTION 'source does not exist';
              END IF;
              PERFORM 1 FROM atlas.source_versions
              WHERE id = p_version_id AND source_id = p_source_id AND status = 'staged'
              FOR UPDATE;
              IF NOT FOUND THEN
                RAISE EXCEPTION 'version is not a staged version of source';
              END IF;
              IF old_version_id IS NOT NULL AND old_version_id <> p_version_id THEN
                UPDATE atlas.source_versions
                SET status = 'superseded', valid_to = now()
                WHERE id = old_version_id;
              END IF;
              UPDATE atlas.source_versions
              SET status = 'active', valid_from = COALESCE(valid_from, now()), valid_to = NULL
              WHERE id = p_version_id;
              UPDATE atlas.sources SET current_version_id = p_version_id WHERE id = p_source_id;
            END
            $$;

            CREATE OR REPLACE FUNCTION atlas.enqueue_ingestion(
              p_collection_id uuid,
              p_trigger text,
              p_idempotency_key text,
              p_requested_by text DEFAULT NULL
            ) RETURNS uuid
            LANGUAGE plpgsql
            AS $$
            DECLARE run_id uuid;
            BEGIN
              INSERT INTO atlas.ingestion_runs(
                collection_id, trigger, idempotency_key, status, requested_by
              ) VALUES (
                p_collection_id, p_trigger, p_idempotency_key, 'queued', p_requested_by
              )
              ON CONFLICT (idempotency_key) DO UPDATE
              SET idempotency_key = EXCLUDED.idempotency_key
              RETURNING id INTO run_id;
              INSERT INTO atlas.ingestion_queue(ingestion_run_id, payload)
              VALUES (
                run_id,
                jsonb_build_object('collection_id', p_collection_id, 'run_id', run_id)
              )
              ON CONFLICT (ingestion_run_id) DO NOTHING;
              RETURN run_id;
            END
            $$;

            CREATE OR REPLACE FUNCTION atlas.fail_ingestion_run(
              p_run_id uuid,
              p_error_code text,
              p_max_attempts integer DEFAULT 3
            ) RETURNS void
            LANGUAGE plpgsql
            AS $$
            BEGIN
              IF p_max_attempts < 1 THEN
                RAISE EXCEPTION 'p_max_attempts must be positive';
              END IF;
              UPDATE atlas.ingestion_runs
              SET attempt_count = attempt_count + 1,
                  status = CASE
                    WHEN attempt_count + 1 >= p_max_attempts THEN 'dead_letter'
                    ELSE 'failed'
                  END,
                  error_code = left(p_error_code, 100),
                  completed_at = CASE
                    WHEN attempt_count + 1 >= p_max_attempts THEN now()
                    ELSE NULL
                  END
              WHERE id = p_run_id AND status NOT IN ('succeeded', 'dead_letter');
              IF NOT FOUND THEN
                RAISE EXCEPTION 'ingestion run is missing or terminal';
              END IF;
            END
            $$;

            INSERT INTO atlas.scheduled_jobs(name, cron_expression, collection_slug)
            VALUES
              ('langgraph_refresh', '0 * * * *', 'langgraph'),
              ('langchain_refresh', '5 * * * *', 'langchain'),
              ('openai_refresh', '10 * * * *', 'openai')
            ON CONFLICT (name) DO NOTHING;
            """
        )
    )

    op.execute(
        sa.text(
            """
            REVOKE ALL ON ALL TABLES IN SCHEMA atlas FROM PUBLIC;
            GRANT SELECT ON atlas.collections, atlas.sources, atlas.source_versions,
              atlas.chunks, atlas.embedding_profiles, atlas.corpus_snapshots,
              atlas.scheduled_jobs TO atlas_readonly;
            GRANT SELECT, INSERT, UPDATE ON atlas.ingestion_runs, atlas.ingestion_items,
              atlas.ingestion_queue TO atlas_worker;
            GRANT SELECT ON atlas.collections, atlas.sources, atlas.source_versions,
              atlas.chunks, atlas.embedding_profiles, atlas.corpus_snapshots TO atlas_api;
            GRANT USAGE, SELECT ON SEQUENCE atlas.corpus_snapshot_revision_seq TO atlas_migrator;
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP FUNCTION IF EXISTS atlas.fail_ingestion_run(uuid, text, integer)"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS atlas.enqueue_ingestion(uuid, text, text, text)"))
    op.execute(sa.text("DROP FUNCTION IF EXISTS atlas.promote_source_version(uuid, uuid)"))
    op.execute(sa.text("DROP SCHEMA IF EXISTS atlas CASCADE"))
