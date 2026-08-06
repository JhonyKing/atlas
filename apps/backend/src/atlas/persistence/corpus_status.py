"""Public corpus freshness status backed by immutable snapshots and ingestion history."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Protocol
from uuid import UUID

from psycopg import Connection

from atlas.domain import (
    CollectionSlug,
    CollectionState,
    CollectionStatus,
    CorpusStatus,
    SourceType,
)


class CorpusUnavailableError(RuntimeError):
    """Raised when no immutable corpus snapshot exists to publish."""


class CorpusStatusProvider(Protocol):
    def get_status(self) -> CorpusStatus | None: ...


_DEFAULT_SOURCE_TYPES: dict[CollectionSlug, list[SourceType]] = {
    CollectionSlug.LANGGRAPH: [SourceType.DOCUMENTATION, SourceType.RELEASE_NOTE],
    CollectionSlug.LANGCHAIN: [SourceType.DOCUMENTATION, SourceType.CHANGELOG],
    CollectionSlug.OPENAI: [SourceType.DOCUMENTATION],
    CollectionSlug.ANTHROPIC: [SourceType.DOCUMENTATION, SourceType.RELEASE_NOTE],
    CollectionSlug.GEMINI: [SourceType.DOCUMENTATION, SourceType.RELEASE_NOTE],
}


class PostgresCorpusStatusRepository:
    """Derive public collection status without exposing source content or diagnostics."""

    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def get_status(self, *, now: datetime | None = None) -> CorpusStatus:
        observed_at = (now or datetime.now(UTC)).astimezone(UTC)
        snapshot = self._connection.execute(
            """
            SELECT id, created_at
            FROM atlas.corpus_snapshots
            ORDER BY revision DESC
            LIMIT 1
            """
        ).fetchone()
        if snapshot is None:
            raise CorpusUnavailableError("no corpus snapshot is available")

        rows = self._connection.execute(
            """
            SELECT
              c.slug,
              c.display_name,
              c.publisher,
              c.base_url,
              c.refresh_interval,
              c.last_success_at,
              max(r.requested_at) AS last_attempt_at,
              coalesce(
                array_agg(DISTINCT s.source_type) FILTER (WHERE s.source_type IS NOT NULL),
                ARRAY[]::text[]
              ) AS source_types,
              coalesce(
                bool_or(r.status IN ('queued', 'running')),
                false
              ) AS refresh_active,
              (
                SELECT count(*) FROM atlas.sources AS count_sources
                WHERE count_sources.collection_id = c.id
                  AND count_sources.current_version_id IS NOT NULL
              ) AS source_count,
              (
                SELECT coalesce(sum(count_versions.page_count), 0)
                FROM atlas.sources AS count_sources
                JOIN atlas.source_versions AS count_versions
                  ON count_versions.id = count_sources.current_version_id
                WHERE count_sources.collection_id = c.id
              ) AS page_count,
              (
                SELECT count(count_chunks.id)
                FROM atlas.sources AS count_sources
                JOIN atlas.source_versions AS count_versions
                  ON count_versions.id = count_sources.current_version_id
                LEFT JOIN atlas.chunks AS count_chunks
                  ON count_chunks.source_version_id = count_versions.id
                WHERE count_sources.collection_id = c.id
              ) AS chunk_count,
              (
                SELECT coalesce(sum(count_versions.byte_size), 0)
                FROM atlas.sources AS count_sources
                JOIN atlas.source_versions AS count_versions
                  ON count_versions.id = count_sources.current_version_id
                WHERE count_sources.collection_id = c.id
              ) AS byte_count
            FROM atlas.collections AS c
            LEFT JOIN atlas.ingestion_runs AS r ON r.collection_id = c.id
            LEFT JOIN atlas.sources AS s ON s.collection_id = c.id
            GROUP BY c.id, c.slug, c.display_name, c.publisher, c.base_url,
                     c.refresh_interval, c.last_success_at
            ORDER BY c.slug
            """
        ).fetchall()
        by_slug = {CollectionSlug(row[0]): row for row in rows}
        collections: list[CollectionStatus] = []
        for slug in CollectionSlug:
            row = by_slug.get(slug)
            if row is None:
                continue
            last_success = _as_utc(row[5])
            last_attempt = _as_utc(row[6])
            refresh_interval = _as_interval(row[4])
            if bool(row[8]):
                state = CollectionState.REFRESHING
            elif last_success is None:
                state = CollectionState.UNAVAILABLE
            elif observed_at - last_success > refresh_interval:
                state = CollectionState.STALE
            else:
                state = CollectionState.READY
            source_types = [SourceType(value) for value in row[7]] or _DEFAULT_SOURCE_TYPES[slug]
            collections.append(
                CollectionStatus(
                    slug=slug,
                    name=row[1],
                    publisher=row[2],
                    source_types=source_types,
                    status=state,
                    last_success_at=last_success,
                    last_attempt_at=last_attempt,
                    canonical_root=row[3],
                    source_count=int(row[9]),
                    page_count=int(row[10]),
                    chunk_count=int(row[11]),
                    byte_count=int(row[12]),
                )
            )

        if len(collections) != len(CollectionSlug):
            raise CorpusUnavailableError("supported collection metadata is incomplete")
        return CorpusStatus(
            snapshot_id=UUID(str(snapshot[0])),
            generated_at=observed_at,
            collections=collections,
        )


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    return value.astimezone(UTC)


def _as_interval(value: timedelta | object) -> timedelta:
    if isinstance(value, timedelta):
        return value
    raise TypeError("collection refresh interval must be a timedelta")
