"""PostgreSQL adapter for immutable corpus retrieval."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from typing import cast
from uuid import UUID

from pgvector.psycopg import register_vector  # type: ignore[import-untyped]
from psycopg import Connection
from pydantic import HttpUrl

from atlas.domain import CollectionSlug, Evidence, SourceType
from atlas.retrieval.service import RetrievalRow

type RetrievalDbRow = tuple[
    UUID,
    UUID,
    UUID,
    UUID,
    str,
    str,
    str,
    str,
    str,
    str,
    datetime,
    str | None,
    int | None,
    int | None,
    int,
]


class CorpusUnavailableError(RuntimeError):
    """Raised when no reproducible corpus snapshot exists for retrieval."""


class PostgresCorpusRepository:
    """Execute the versioned SQL retrieval contract without leaking provider types."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection
        register_vector(connection)

    async def select_snapshot(self, collection: CollectionSlug | None) -> UUID:
        del collection
        row = self._connection.execute(
            "SELECT id FROM atlas.corpus_snapshots ORDER BY revision DESC LIMIT 1"
        ).fetchone()
        if row is None:
            raise CorpusUnavailableError("no corpus snapshot is available")
        return cast(UUID, row[0])

    async def search(
        self,
        *,
        collection: CollectionSlug | None,
        query_text: str,
        embedding: list[float],
        top_k: int,
        snapshot_id: UUID,
        version: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> Sequence[RetrievalRow]:
        collections = [collection] if collection is not None else list(CollectionSlug)
        rows: list[RetrievalRow] = []
        for slug in collections:
            result = cast(
                Sequence[RetrievalDbRow],
                self._connection.execute(
                    """
                    SELECT evidence_id, chunk_id, source_id, source_version_id,
                           collection_slug, source_title, publisher, canonical_url, source_type,
                           excerpt, capture_date, version_label, keyword_rank, vector_rank,
                           fused_rank
                    FROM atlas.search_evidence(
                        %s::text, %s::text, %s::extensions.vector, %s::integer, %s::uuid
                    )
                    """,
                    (slug.value, query_text, embedding, top_k, snapshot_id),
                ).fetchall(),
            )
            rows.extend(
                self._to_row(row, version=version, date_from=date_from, date_to=date_to)
                for row in result
                if self._matches_constraints(
                    row,
                    version=version,
                    date_from=date_from,
                    date_to=date_to,
                )
            )
        return sorted(rows, key=lambda row: (row.fused_rank, str(row.evidence.id)))[:top_k]

    @staticmethod
    def _matches_constraints(
        row: RetrievalDbRow,
        *,
        version: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> bool:
        row_version = row[11]
        captured_at = row[10]
        if version is not None and row_version != version:
            return False
        captured_date = captured_at.date()
        return not (
            (date_from is not None and captured_date < date_from)
            or (date_to is not None and captured_date > date_to)
        )

    @staticmethod
    def _to_row(
        row: RetrievalDbRow,
        *,
        version: str | None,
        date_from: date | None,
        date_to: date | None,
    ) -> RetrievalRow:
        del version, date_from, date_to
        captured_at = row[10]
        evidence = Evidence(
            id=row[0],
            source_title=row[5],
            publisher=row[6],
            canonical_url=HttpUrl(row[7]),
            excerpt=row[9],
            captured_at=captured_at,
            version_label=row[11],
            source_type=SourceType(row[8]),
        )
        return RetrievalRow(
            evidence=evidence,
            keyword_rank=row[12],
            vector_rank=row[13],
            fused_rank=row[14],
        )
