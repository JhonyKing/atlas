"""Persist bounded news candidates and one deterministic selection per UTC day."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0010_daily_news"
down_revision = "0009_provenance"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            CREATE TABLE IF NOT EXISTS atlas.news_candidates (
              id uuid PRIMARY KEY DEFAULT atlas.new_uuid(),
              candidate_day date NOT NULL,
              title text NOT NULL CHECK (length(title) BETWEEN 1 AND 300),
              summary text NOT NULL DEFAULT '' CHECK (length(summary) <= 4000),
              publisher text NOT NULL CHECK (length(publisher) BETWEEN 1 AND 160),
              canonical_url text NOT NULL CHECK (canonical_url LIKE 'https://%'),
              published_at timestamptz NOT NULL,
              captured_at timestamptz NOT NULL,
              authority_score numeric(4,3) NOT NULL CHECK (authority_score BETWEEN 0 AND 1),
              topic_score numeric(4,3) NOT NULL CHECK (topic_score BETWEEN 0 AND 1),
              corroboration_count integer NOT NULL DEFAULT 1 CHECK (corroboration_count >= 1),
              content_sha256 char(64) NOT NULL CHECK (content_sha256 ~ '^[0-9a-f]{64}$'),
              created_at timestamptz NOT NULL DEFAULT now(),
              UNIQUE (canonical_url, content_sha256)
            );

            CREATE TABLE IF NOT EXISTS atlas.news_selections (
              candidate_day date PRIMARY KEY,
              status text NOT NULL CHECK (status IN ('ready', 'unavailable')),
              candidate_id uuid REFERENCES atlas.news_candidates(id) ON DELETE SET NULL,
              candidate_count integer NOT NULL DEFAULT 0 CHECK (candidate_count >= 0),
              score numeric(4,3) CHECK (score IS NULL OR score BETWEEN 0 AND 1),
              reason_code text NOT NULL CHECK (
                reason_code IN ('none', 'not_configured', 'no_evidence', 'insufficient_signal')
              ),
              generated_at timestamptz NOT NULL DEFAULT now()
            );

            CREATE TABLE IF NOT EXISTS atlas.news_refresh_jobs (
              name text PRIMARY KEY,
              cron_expression text NOT NULL,
              status text NOT NULL DEFAULT 'disabled' CHECK (status IN ('enabled', 'disabled')),
              last_run_at timestamptz,
              created_at timestamptz NOT NULL DEFAULT now()
            );
            INSERT INTO atlas.news_refresh_jobs(name, cron_expression, status)
            VALUES ('previous_day_news', '20 * * * *', 'disabled')
            ON CONFLICT (name) DO NOTHING;

            CREATE INDEX IF NOT EXISTS news_candidates_day_idx
              ON atlas.news_candidates(candidate_day, published_at DESC);
            REVOKE ALL ON atlas.news_candidates, atlas.news_selections, atlas.news_refresh_jobs FROM PUBLIC;
            GRANT SELECT ON atlas.news_candidates, atlas.news_selections TO atlas_api, atlas_readonly;
            GRANT SELECT, INSERT, UPDATE ON atlas.news_candidates, atlas.news_selections,
              atlas.news_refresh_jobs TO atlas_worker;
            """
        )
    )


def downgrade() -> None:
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.news_selections"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.news_candidates"))
    op.execute(sa.text("DROP TABLE IF EXISTS atlas.news_refresh_jobs"))
