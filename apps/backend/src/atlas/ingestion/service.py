"""Durable-ingestion interfaces and idempotent refresh requests."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal, Protocol
from uuid import UUID

import psycopg
from pgvector.psycopg import register_vector  # type: ignore[import-untyped]

from atlas.domain import CollectionSlug
from atlas.ingestion.chunker import MarkdownChunk
from atlas.ingestion.connectors import SourceCandidate
from atlas.ingestion.normalizer import NormalizedDocument
from atlas.providers.openai_embeddings import DEFAULT_EMBEDDING_PROFILE

RunStatus = Literal["queued", "running", "succeeded", "failed", "dead_letter"]


class IdempotencyConflict(RuntimeError):
    """An idempotency key was previously bound to a different collection."""


@dataclass(frozen=True, slots=True)
class IngestionRun:
    id: UUID
    collection: CollectionSlug
    trigger: str
    idempotency_key: str
    attempt_count: int = 0
    status: RunStatus = "queued"
    requested_at: datetime | None = None


class IngestionRepository(Protocol):
    def enqueue(
        self,
        collection: CollectionSlug,
        trigger: str,
        idempotency_key: str,
        requested_by: str | None = None,
    ) -> UUID: ...

    def claim_next(self) -> IngestionRun | None: ...

    def stage_source(
        self,
        run: IngestionRun,
        candidate: SourceCandidate,
        document: NormalizedDocument,
        chunks: Sequence[MarkdownChunk],
        vectors: Sequence[Sequence[float]],
    ) -> None: ...

    def promote_source(self, run: IngestionRun, candidate: SourceCandidate) -> None: ...

    def complete(self, run: IngestionRun, *, discovered: int, promoted: int) -> None: ...

    def fail(self, run: IngestionRun, *, error_code: str, max_attempts: int) -> None: ...


class SourceDiscoverer(Protocol):
    async def discover(self, collection: CollectionSlug) -> Sequence[SourceCandidate]: ...


class OperatorIngestionService(Protocol):
    def request_refresh(
        self,
        collection: CollectionSlug,
        trigger: str,
        idempotency_key: str,
        requested_by: str | None = None,
    ) -> UUID: ...

    def get_status(self, run_id: UUID) -> dict[str, object] | None: ...


class IngestionService:
    def __init__(self, repository: IngestionRepository) -> None:
        self._repository = repository

    def request_refresh(
        self,
        collection: CollectionSlug,
        trigger: str,
        idempotency_key: str,
        requested_by: str | None = None,
    ) -> UUID:
        if trigger not in {"scheduled", "operator"}:
            raise ValueError("trigger must be scheduled or operator")
        if not idempotency_key.strip():
            raise ValueError("idempotency_key must not be blank")
        return self._repository.enqueue(collection, trigger, idempotency_key, requested_by)

    def get_status(self, run_id: UUID) -> dict[str, object] | None:
        getter = getattr(self._repository, "get_status", None)
        if getter is None:
            return None
        return getter(run_id)


class PostgresIngestionRepository:
    """Durable repository backed by the corpus tables and transactional SQL functions."""

    def __init__(self, connection: psycopg.Connection[Any]) -> None:
        self._connection = connection
        register_vector(connection)
        self._leases: dict[UUID, str] = {}
        self._pending_versions: dict[tuple[UUID, str], UUID | None] = {}

    def enqueue(
        self,
        collection: CollectionSlug,
        trigger: str,
        idempotency_key: str,
        requested_by: str | None = None,
    ) -> UUID:
        existing = self._connection.execute(
            """
            SELECT r.id, c.slug
            FROM atlas.ingestion_runs AS r
            JOIN atlas.collections AS c ON c.id = r.collection_id
            WHERE r.idempotency_key = %s
            """,
            (idempotency_key,),
        ).fetchone()
        if existing is not None:
            if existing[1] != collection.value:
                raise IdempotencyConflict("idempotency key belongs to another collection")
            self._connection.commit()
            return existing[0]
        row = self._connection.execute(
            "SELECT atlas.enqueue_ingestion(%s, %s, %s, %s)",
            (
                self._collection_id(collection),
                trigger,
                idempotency_key,
                requested_by,
            ),
        ).fetchone()
        self._connection.commit()
        if row is None:
            raise RuntimeError("ingestion enqueue did not return a run id")
        return row[0]

    def get_status(self, run_id: UUID) -> dict[str, object] | None:
        row = self._connection.execute(
            """
            SELECT r.id, c.slug, r.trigger, r.status, r.requested_at, r.started_at,
                   r.completed_at, r.attempt_count, r.discovered_count, r.promoted_count,
                   r.failed_count, r.error_code
            FROM atlas.ingestion_runs AS r
            JOIN atlas.collections AS c ON c.id = r.collection_id
            WHERE r.id = %s
            """,
            (run_id,),
        ).fetchone()
        if row is None:
            return None
        return {
            "id": row[0],
            "collection": row[1],
            "trigger": row[2],
            "status": row[3],
            "requested_at": row[4],
            "started_at": row[5],
            "completed_at": row[6],
            "attempt_count": row[7],
            "discovered_count": row[8],
            "promoted_count": row[9],
            "failed_count": row[10],
            "error_code": row[11],
        }

    def claim_next(self) -> IngestionRun | None:
        row = self._connection.execute(
            """
            SELECT r.id, c.slug, r.trigger, r.idempotency_key, r.attempt_count, r.status,
                   r.requested_at
            FROM atlas.ingestion_runs AS r
            JOIN atlas.collections AS c ON c.id = r.collection_id
            WHERE r.status = 'queued'
              AND pg_try_advisory_lock(hashtextextended(c.slug, 0))
            ORDER BY r.requested_at
            FOR UPDATE SKIP LOCKED
            LIMIT 1
            """
        ).fetchone()
        if row is None:
            self._connection.rollback()
            return None
        run_id, slug, trigger, key, attempts, status, requested_at = row
        collection = CollectionSlug(slug)
        self._connection.execute(
            """
            UPDATE atlas.ingestion_runs
            SET status = 'running', started_at = now()
            WHERE id = %s
            """,
            (run_id,),
        )
        self._connection.commit()
        self._leases[run_id] = collection.value
        return IngestionRun(
            id=run_id,
            collection=collection,
            trigger=trigger,
            idempotency_key=key,
            attempt_count=attempts,
            status=status,
            requested_at=requested_at,
        )

    def stage_source(
        self,
        run: IngestionRun,
        candidate: SourceCandidate,
        document: NormalizedDocument,
        chunks: Sequence[MarkdownChunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        if len(chunks) != len(vectors):
            raise ValueError("embedding count does not match chunk count")
        collection_id = self._collection_id(run.collection)
        source_row = self._connection.execute(
            """
            INSERT INTO atlas.sources(
              collection_id, canonical_url, source_type, title, publisher, language, trust_tier
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (collection_id, canonical_url) DO UPDATE SET
              title = EXCLUDED.title, publisher = EXCLUDED.publisher, updated_at = now()
            RETURNING id
            """,
            (
                collection_id,
                candidate.canonical_url,
                candidate.source_type.value,
                candidate.title,
                "LangChain" if candidate.collection is not CollectionSlug.OPENAI else "OpenAI",
                document.language,
                "official_repository" if candidate.source_revision_url else "official_docs",
            ),
        ).fetchone()
        if source_row is None:
            raise RuntimeError("source upsert did not return an id")
        source_id = source_row[0]
        version_row = self._connection.execute(
            """
            INSERT INTO atlas.source_versions(
              source_id, ingestion_run_id, content_sha256, source_revision_url,
              version_label, published_at, fetched_at, normalized_markdown, byte_size,
              page_count, language, ocr_used, ocr_confidence, status
            ) VALUES (%s, %s, %s, %s, %s, %s, now(), %s, %s, %s, %s, %s, %s, 'staged')
            ON CONFLICT (source_id, content_sha256) DO NOTHING
            RETURNING id
            """,
            (
                source_id,
                run.id,
                document.content_sha256,
                candidate.source_revision_url,
                candidate.version_label,
                candidate.published_at,
                document.markdown,
                document.byte_size,
                document.page_count,
                document.language,
                document.ocr_used,
                document.ocr_confidence,
            ),
        ).fetchone()
        if version_row is None:
            existing = self._connection.execute(
                "SELECT id, status FROM atlas.source_versions "
                "WHERE source_id = %s AND content_sha256 = %s",
                (source_id, document.content_sha256),
            ).fetchone()
            if existing is None:
                raise RuntimeError("source version upsert did not return an id")
            self._pending_versions[(run.id, candidate.canonical_url)] = (
                None if existing[1] == "active" else existing[0]
            )
            self._connection.commit()
            return
        version_id = version_row[0]
        profile_row = self._connection.execute(
            """
            INSERT INTO atlas.embedding_profiles(
              provider, model, dimensions, distance_metric, normalization_version
            ) VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (provider, model, dimensions, normalization_version)
            DO UPDATE SET retired_at = NULL
            RETURNING id
            """,
            (
                DEFAULT_EMBEDDING_PROFILE.provider,
                DEFAULT_EMBEDDING_PROFILE.model,
                DEFAULT_EMBEDDING_PROFILE.dimensions,
                DEFAULT_EMBEDDING_PROFILE.distance_metric,
                DEFAULT_EMBEDDING_PROFILE.normalization_version,
            ),
        ).fetchone()
        if profile_row is None:
            raise RuntimeError("embedding profile upsert did not return an id")
        profile_id = profile_row[0]
        for chunk, vector in zip(chunks, vectors, strict=True):
            chunk_row = self._connection.execute(
                """
                INSERT INTO atlas.chunks(
                  source_version_id, ordinal, heading_path, anchor, text, text_sha256,
                  token_count, start_offset, end_offset, page_start, page_end, language,
                  ocr_used, ocr_confidence
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    version_id,
                    chunk.ordinal,
                    list(chunk.heading_path),
                    chunk.anchor,
                    chunk.text,
                    chunk.text_sha256,
                    chunk.token_count,
                    chunk.start_offset,
                    chunk.end_offset,
                    chunk.page_start,
                    chunk.page_end,
                    chunk.language,
                    chunk.ocr_used,
                    chunk.ocr_confidence,
                ),
            ).fetchone()
            if chunk_row is None:
                raise RuntimeError("chunk insert did not return an id")
            self._connection.execute(
                """
                INSERT INTO atlas.chunk_embeddings(chunk_id, embedding_profile_id, embedding)
                VALUES (%s, %s, %s)
                ON CONFLICT (chunk_id, embedding_profile_id)
                DO UPDATE SET embedding = EXCLUDED.embedding
                """,
                (chunk_row[0], profile_id, list(vector)),
            )
        self._connection.commit()
        self._pending_versions[(run.id, candidate.canonical_url)] = version_id

    def promote_source(self, run: IngestionRun, candidate: SourceCandidate) -> None:
        version_id = self._pending_versions.pop((run.id, candidate.canonical_url), None)
        if version_id is not None:
            self._connection.execute(
                "SELECT atlas.promote_source_version(%s, %s)",
                (self._source_id(candidate), version_id),
            )
            self._connection.commit()

    def complete(self, run: IngestionRun, *, discovered: int, promoted: int) -> None:
        self._connection.execute(
            """
            UPDATE atlas.ingestion_runs
            SET status = 'succeeded', discovered_count = %s, promoted_count = %s,
                completed_at = now()
            WHERE id = %s
            """,
            (discovered, promoted, run.id),
        )
        self._connection.commit()
        self._release_lease(run)

    def fail(self, run: IngestionRun, *, error_code: str, max_attempts: int) -> None:
        self._connection.execute(
            "SELECT atlas.fail_ingestion_run(%s, %s, %s)",
            (run.id, error_code, max_attempts),
        )
        self._connection.execute(
            "UPDATE atlas.ingestion_runs SET status = 'queued' WHERE id = %s AND status = 'failed'",
            (run.id,),
        )
        self._connection.commit()
        self._release_lease(run)

    def _collection_id(self, collection: CollectionSlug) -> UUID:
        row = self._connection.execute(
            "SELECT id FROM atlas.collections WHERE slug = %s",
            (collection.value,),
        ).fetchone()
        if row is None:
            raise KeyError(f"collection {collection.value} is not seeded")
        return row[0]

    def _source_id(self, candidate: SourceCandidate) -> UUID:
        row = self._connection.execute(
            """
            SELECT s.id
            FROM atlas.sources AS s
            JOIN atlas.collections AS c ON c.id = s.collection_id
            WHERE c.slug = %s AND s.canonical_url = %s
            """,
            (candidate.collection.value, candidate.canonical_url),
        ).fetchone()
        if row is None:
            raise KeyError("source is not staged")
        return row[0]

    def _release_lease(self, run: IngestionRun) -> None:
        slug = self._leases.pop(run.id, None)
        if slug is not None:
            self._connection.execute(
                "SELECT pg_advisory_unlock(hashtextextended(%s, 0))",
                (slug,),
            )
            self._connection.commit()
