"""Seed the supported corpus collections required by ingestion queueing."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0011_seed_collections"
down_revision = "0010_daily_news"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        sa.text(
            """
            INSERT INTO atlas.collections(
              slug, display_name, publisher, base_url, allowed_hosts
            ) VALUES
              (
                'langgraph', 'LangGraph', 'LangChain',
                'https://docs.langchain.com/oss/python/langgraph/',
                ARRAY['docs.langchain.com']::text[]
              ),
              (
                'langchain', 'LangChain', 'LangChain',
                'https://docs.langchain.com/oss/python/langchain/',
                ARRAY['docs.langchain.com']::text[]
              ),
              (
                'openai', 'OpenAI API', 'OpenAI',
                'https://developers.openai.com/api/docs/',
                ARRAY['developers.openai.com']::text[]
              )
            ON CONFLICT (slug) DO UPDATE SET
              display_name = EXCLUDED.display_name,
              publisher = EXCLUDED.publisher,
              base_url = EXCLUDED.base_url,
              allowed_hosts = EXCLUDED.allowed_hosts
            """
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text(
            """
            DELETE FROM atlas.collections
            WHERE slug IN ('langgraph', 'langchain', 'openai')
              AND NOT EXISTS (
                SELECT 1 FROM atlas.ingestion_runs
                WHERE ingestion_runs.collection_id = collections.id
              )
            """
        )
    )
