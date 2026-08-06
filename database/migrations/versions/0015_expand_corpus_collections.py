"""Register Anthropic and Gemini as governed corpus collections."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0015_expand_corpus_collections"
down_revision = "0014_comparison_cell_context"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            ALTER TABLE atlas.collections
              DROP CONSTRAINT IF EXISTS collections_slug_check;
            ALTER TABLE atlas.collections
              ADD CONSTRAINT collections_slug_check
              CHECK (slug IN ('langgraph', 'langchain', 'openai', 'anthropic', 'gemini'));

            ALTER TABLE atlas.scheduled_jobs
              DROP CONSTRAINT IF EXISTS scheduled_jobs_collection_slug_check;
            ALTER TABLE atlas.scheduled_jobs
              ADD CONSTRAINT scheduled_jobs_collection_slug_check
              CHECK (collection_slug IN ('langgraph', 'langchain', 'openai', 'anthropic', 'gemini'));

            INSERT INTO atlas.collections(
              slug, display_name, publisher, base_url, allowed_hosts
            ) VALUES
              (
                'anthropic', 'Anthropic Claude', 'Anthropic',
                'https://docs.anthropic.com/en/docs/',
                ARRAY['docs.anthropic.com']::text[]
              ),
              (
                'gemini', 'Google Gemini', 'Google',
                'https://ai.google.dev/gemini-api/docs/',
                ARRAY['ai.google.dev']::text[]
              )
            ON CONFLICT (slug) DO UPDATE SET
              display_name = EXCLUDED.display_name,
              publisher = EXCLUDED.publisher,
              base_url = EXCLUDED.base_url,
              allowed_hosts = EXCLUDED.allowed_hosts;
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM atlas.collections AS c
            WHERE c.slug IN ('anthropic', 'gemini')
              AND NOT EXISTS (
                SELECT 1 FROM atlas.ingestion_runs AS r
                WHERE r.collection_id = c.id
              );

            ALTER TABLE atlas.collections
              DROP CONSTRAINT IF EXISTS collections_slug_check;
            ALTER TABLE atlas.collections
              ADD CONSTRAINT collections_slug_check
              CHECK (slug IN ('langgraph', 'langchain', 'openai'));

            ALTER TABLE atlas.scheduled_jobs
              DROP CONSTRAINT IF EXISTS scheduled_jobs_collection_slug_check;
            ALTER TABLE atlas.scheduled_jobs
              ADD CONSTRAINT scheduled_jobs_collection_slug_check
              CHECK (collection_slug IN ('langgraph', 'langchain', 'openai'));
            """
        )
    )
