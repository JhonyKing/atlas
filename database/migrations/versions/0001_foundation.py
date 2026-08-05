"""Create ATLAS foundation schemas, roles, helpers, and extension status."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_foundation"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS atlas"))
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS atlas_private"))
    op.execute(sa.text("CREATE SCHEMA IF NOT EXISTS atlas_audit"))

    # vector is part of the supported database contract. pgmq and pg_cron are
    # optional image capabilities and are recorded explicitly when unavailable.
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS vector"))
    op.execute(sa.text("CREATE EXTENSION IF NOT EXISTS pgcrypto"))

    op.execute(
        sa.text(
            """
            DO $$
            DECLARE role_name text;
            BEGIN
              FOREACH role_name IN ARRAY ARRAY[
                'atlas_api', 'atlas_worker', 'atlas_migrator', 'atlas_readonly', 'atlas_owner'
              ] LOOP
                IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name) THEN
                  EXECUTE format(
                    'CREATE ROLE %I NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE INHERIT',
                    role_name
                  );
                END IF;
              END LOOP;
            END
            $$;
            """
        )
    )

    op.execute(
        sa.text(
            """
            REVOKE ALL ON SCHEMA atlas FROM PUBLIC;
            REVOKE ALL ON SCHEMA atlas_private FROM PUBLIC;
            REVOKE ALL ON SCHEMA atlas_audit FROM PUBLIC;
            REVOKE CREATE ON SCHEMA public FROM PUBLIC;

            GRANT USAGE ON SCHEMA atlas TO atlas_api, atlas_worker, atlas_readonly;
            GRANT USAGE ON SCHEMA atlas_private TO atlas_worker, atlas_migrator;
            GRANT USAGE ON SCHEMA atlas_audit TO atlas_worker, atlas_readonly;

            GRANT atlas_readonly TO atlas_api;
            GRANT atlas_readonly TO atlas_worker;
            GRANT atlas_owner TO atlas_migrator;
            """
        )
    )

    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.extension_status (
              extension_name text PRIMARY KEY,
              requested boolean NOT NULL DEFAULT true,
              installed boolean NOT NULL,
              detail text,
              checked_at timestamptz NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS atlas.app_metadata (
              key text PRIMARY KEY,
              value jsonb NOT NULL,
              updated_at timestamptz NOT NULL DEFAULT now()
            );

            COMMENT ON TABLE atlas.app_metadata IS
              'Protected runtime metadata; never stores question, answer, credential, or visitor data.';
            COMMENT ON TABLE atlas.extension_status IS
              'Records required and optional extension availability for this database image.';
            """
        )
    )

    op.execute(
        sa.text(
            """
            CREATE OR REPLACE FUNCTION atlas.new_uuid()
            RETURNS uuid
            LANGUAGE plpgsql
            VOLATILE
            AS $$
            DECLARE result uuid;
            BEGIN
              IF to_regprocedure('uuidv7()') IS NOT NULL THEN
                EXECUTE 'SELECT uuidv7()' INTO result;
                RETURN result;
              END IF;
              RETURN gen_random_uuid();
            END
            $$;

            CREATE OR REPLACE FUNCTION atlas.touch_updated_at()
            RETURNS trigger
            LANGUAGE plpgsql
            AS $$
            BEGIN
              NEW.updated_at = timezone('UTC', now());
              RETURN NEW;
            END
            $$;

            DROP TRIGGER IF EXISTS app_metadata_touch_updated_at ON atlas.app_metadata;
            CREATE TRIGGER app_metadata_touch_updated_at
            BEFORE UPDATE ON atlas.app_metadata
            FOR EACH ROW EXECUTE FUNCTION atlas.touch_updated_at();
            """
        )
    )

    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.app_metadata ENABLE ROW LEVEL SECURITY;
            ALTER TABLE atlas.app_metadata FORCE ROW LEVEL SECURITY;
            DROP POLICY IF EXISTS app_metadata_migrator ON atlas.app_metadata;
            CREATE POLICY app_metadata_migrator ON atlas.app_metadata
              FOR ALL TO atlas_migrator
              USING (true)
              WITH CHECK (true);

            REVOKE ALL ON atlas.app_metadata FROM PUBLIC;
            GRANT SELECT ON atlas.extension_status TO atlas_readonly;
            GRANT SELECT ON atlas.extension_status TO atlas_api, atlas_worker;
            GRANT ALL ON atlas.app_metadata TO atlas_migrator;

            ALTER DEFAULT PRIVILEGES IN SCHEMA atlas REVOKE ALL ON TABLES FROM PUBLIC;
            ALTER DEFAULT PRIVILEGES IN SCHEMA atlas
              GRANT SELECT ON TABLES TO atlas_readonly;
            """
        )
    )

    op.execute(
        sa.text(
            """
            DO $$
            DECLARE requested_extension text;
            DECLARE extension_installed boolean;
            DECLARE extension_detail text;
            BEGIN
              FOREACH requested_extension IN ARRAY ARRAY['vector', 'pgmq', 'pg_cron'] LOOP
                extension_installed := false;
                extension_detail := NULL;
                IF EXISTS (
                  SELECT 1 FROM pg_available_extensions WHERE name = requested_extension
                ) THEN
                  BEGIN
                    EXECUTE format('CREATE EXTENSION IF NOT EXISTS %I', requested_extension);
                    extension_installed := EXISTS (
                      SELECT 1 FROM pg_extension WHERE extname = requested_extension
                    );
                    IF NOT extension_installed THEN
                      extension_detail := 'extension did not become installed';
                    END IF;
                  EXCEPTION WHEN OTHERS THEN
                    extension_detail := SQLERRM;
                  END;
                ELSE
                  extension_detail := 'not available in this PostgreSQL image';
                END IF;

                INSERT INTO atlas.extension_status(
                  extension_name, requested, installed, detail, checked_at
                ) VALUES (
                  requested_extension, true, extension_installed, extension_detail, now()
                )
                ON CONFLICT ON CONSTRAINT extension_status_pkey DO UPDATE SET
                  requested = EXCLUDED.requested,
                  installed = EXCLUDED.installed,
                  detail = EXCLUDED.detail,
                  checked_at = EXCLUDED.checked_at;
              END LOOP;
            END
            $$;
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP SCHEMA IF EXISTS atlas_audit CASCADE"))
    op.execute(sa.text("DROP SCHEMA IF EXISTS atlas_private CASCADE"))
    op.execute(sa.text("DROP SCHEMA IF EXISTS atlas CASCADE"))
    op.execute(
        sa.text(
            """
            DO $$
            DECLARE role_name text;
            BEGIN
              FOREACH role_name IN ARRAY ARRAY[
                'atlas_api', 'atlas_worker', 'atlas_migrator', 'atlas_readonly', 'atlas_owner'
              ] LOOP
                IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = role_name) THEN
                  EXECUTE format('DROP ROLE %I', role_name);
                END IF;
              END LOOP;
            END
            $$;
            """
        )
    )
