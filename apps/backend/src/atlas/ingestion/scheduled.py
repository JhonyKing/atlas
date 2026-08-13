"""Collection-scoped scheduled ingestion for serverless runtimes.

The durable queue and the normal ``IngestionWorker`` remain the source of truth.  This
adapter only adds the small amount of orchestration needed when a Vercel Cron invocation
must enqueue and drain one collection before the function exits.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Protocol

import httpx
import psycopg
from openai import AsyncOpenAI

from atlas.config import Settings
from atlas.domain import CollectionSlug
from atlas.ingestion.fetcher import FetchPolicy, SafeFetcher
from atlas.ingestion.manifest import ManifestDiscoverer, load_manifest
from atlas.ingestion.service import IngestionService, PostgresIngestionRepository
from atlas.ingestion.worker import IngestionWorker
from atlas.providers.openai_embeddings import OpenAIEmbeddingsAdapter


class ScheduledIngestionRunner(Protocol):
    """The route-facing seam, replaceable by a deterministic test fake."""

    async def run_collection(
        self,
        collection: CollectionSlug,
        *,
        requested_at: datetime,
    ) -> dict[str, object]: ...


def build_scheduled_idempotency_key(
    manifest_version: str,
    requested_at: datetime,
    collection: CollectionSlug,
) -> str:
    """Return the stable key used by a daily collection Cron invocation."""

    day = requested_at.astimezone(UTC).date().isoformat()
    return f"cron:{manifest_version}:{day}:{collection.value}"


def _resolve_manifest(path: Path) -> Path:
    """Resolve repository-relative manifests from local, Docker, and Vercel roots."""

    if path.is_absolute() and path.exists():
        return path
    if path.exists():
        return path
    repository_root = Path(__file__).resolve().parents[5]
    candidate = repository_root / path
    if candidate.exists():
        return candidate
    raise FileNotFoundError(f"approved corpus manifest is unavailable: {path.name}")


class ScheduledIngestionService:
    """Enqueue and drain exactly one collection-scoped run per invocation."""

    def __init__(
        self,
        settings: Settings,
    ) -> None:
        self._settings = settings

    async def run_collection(
        self,
        collection: CollectionSlug,
        *,
        requested_at: datetime,
    ) -> dict[str, object]:
        settings = self._settings
        if (
            settings.openai_api_key is None
            or not settings.openai_api_key.get_secret_value().strip()
        ):
            raise RuntimeError("scheduled ingestion requires an embedding provider")

        manifest = load_manifest(_resolve_manifest(settings.atlas_corpus_manifest))
        if manifest.review_status != "approved":
            raise RuntimeError("scheduled ingestion requires an approved corpus manifest")
        if not any(candidate.collection is collection for candidate in manifest.candidates):
            raise ValueError("collection is not present in the approved corpus manifest")

        idempotency_key = build_scheduled_idempotency_key(
            manifest.version,
            requested_at,
            collection,
        )
        dsn = settings.database_url.get_secret_value().replace(
            "postgresql+psycopg://", "postgresql://", 1
        )
        connection = psycopg.connect(dsn)
        provider = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
        http_client = httpx.AsyncClient()
        manifest_hosts = frozenset(
            candidate.canonical_url.split("/", 3)[2]
            for candidate in manifest.candidates
            if candidate.collection is collection
        )
        fetcher = SafeFetcher(
            client=http_client,
            policy=FetchPolicy(
                allowed_hosts=manifest_hosts,
                max_bytes=settings.atlas_ingestion_max_bytes,
            ),
        )
        repository = PostgresIngestionRepository(connection)
        service = IngestionService(repository)
        try:
            run_id = service.request_refresh(
                collection,
                trigger="scheduled",
                idempotency_key=idempotency_key,
                requested_by="vercel-cron",
            )
            worker = IngestionWorker(
                repository=repository,
                discoverer=ManifestDiscoverer(manifest),
                fetcher=fetcher,
                embedder=OpenAIEmbeddingsAdapter(client=provider),
                max_attempts=settings.atlas_ingestion_max_retries,
            )
            processed_runs = await worker.run_until_empty(max_runs=1, collection=collection)
            status = service.get_status(run_id)
            if status is None:
                raise RuntimeError("scheduled ingestion status is unavailable")
            return {
                "run_id": run_id,
                "collection": collection,
                "manifest_version": manifest.version,
                "idempotency_key": idempotency_key,
                "processed_runs": processed_runs,
                "status": status["status"],
                "attempt_count": status["attempt_count"],
                "discovered_count": status["discovered_count"],
                "promoted_count": status["promoted_count"],
            }
        finally:
            await fetcher.aclose()
            await provider.close()
            connection.close()


__all__ = [
    "ScheduledIngestionRunner",
    "ScheduledIngestionService",
    "build_scheduled_idempotency_key",
]
