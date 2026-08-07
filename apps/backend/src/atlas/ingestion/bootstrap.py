"""Reproducible corpus bootstrap with a safe dry-run default."""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
from collections.abc import Sequence
from pathlib import Path
from typing import Any

import httpx
import psycopg
from openai import AsyncOpenAI
from psycopg.types.json import Jsonb

from atlas.config import Settings
from atlas.domain import CollectionSlug
from atlas.ingestion.connectors import SourceCandidate
from atlas.ingestion.fetcher import FetchPolicy, SafeFetcher
from atlas.ingestion.manifest import CorpusManifest, load_manifest
from atlas.ingestion.service import IngestionService, PostgresIngestionRepository
from atlas.ingestion.worker import IngestionWorker
from atlas.providers.openai_embeddings import OpenAIEmbeddingsAdapter


class ManifestDiscoverer:
    def __init__(self, manifest: CorpusManifest) -> None:
        self._manifest = manifest

    async def discover(self, collection: CollectionSlug) -> Sequence[SourceCandidate]:
        return tuple(
            candidate
            for candidate in self._manifest.candidates
            if candidate.collection is collection
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlas-corpus-bootstrap")
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("corpus/manifests/launch-v1.yaml"),
    )
    parser.add_argument("--collection", choices=[value.value for value in CollectionSlug])
    parser.add_argument("--max-runs", type=int, default=1)
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Perform network fetches, embeddings and database promotion; dry-run is the default.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    manifest = load_manifest(args.manifest)
    candidates = manifest.candidates
    if args.collection:
        collection = CollectionSlug(args.collection)
        candidates = tuple(
            candidate for candidate in candidates if candidate.collection is collection
        )
    summary = {
        "manifest": str(args.manifest),
        "version": manifest.version,
        "review_status": manifest.review_status,
        "execute": bool(args.execute),
        "source_count": len(candidates),
        "collections": {
            slug.value: sum(candidate.collection is slug for candidate in candidates)
            for slug in CollectionSlug
        },
    }
    if not args.execute:
        print(json.dumps(summary, indent=2, sort_keys=True))
        return 0
    if manifest.review_status != "approved":
        raise RuntimeError(
            "--execute requires a manifest with review_status=approved; "
            "complete source governance first"
        )
    settings = Settings()
    if settings.openai_api_key is None or not settings.openai_api_key.get_secret_value().strip():
        raise RuntimeError("--execute requires OPENAI_API_KEY in secret configuration")
    return asyncio.run(_execute(settings, manifest, args.collection, args.max_runs))


def _manifest_fingerprint(manifest: CorpusManifest) -> str:
    """Return a stable short fingerprint so changed URLs get a fresh idempotency key."""

    material = "\n".join(sorted(candidate.canonical_url for candidate in manifest.candidates))
    return hashlib.sha256(material.encode("utf-8")).hexdigest()[:16]


def _promote_snapshot(connection: psycopg.Connection[Any], manifest: CorpusManifest) -> str | None:
    """Create one immutable snapshot only after every manifest source is active."""

    source_version_ids: list[str] = []
    for candidate in manifest.candidates:
        row = connection.execute(
            """
            SELECT s.current_version_id
            FROM atlas.sources AS s
            JOIN atlas.collections AS c ON c.id = s.collection_id
            WHERE c.slug = %s AND s.canonical_url = %s AND s.current_version_id IS NOT NULL
            """,
            (candidate.collection.value, candidate.canonical_url),
        ).fetchone()
        if row is None:
            return None
        source_version_ids.append(str(row[0]))

    payload = {
        "version": manifest.version,
        "review_status": manifest.review_status,
        "source_version_ids": source_version_ids,
        "sources": [
            {
                "collection": candidate.collection.value,
                "title": candidate.title,
                "url": candidate.canonical_url,
                "type": candidate.source_type.value,
            }
            for candidate in manifest.candidates
        ],
    }
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()
    row = connection.execute(
        """
        INSERT INTO atlas.corpus_snapshots(manifest, manifest_sha256)
        VALUES (%s, %s)
        ON CONFLICT (manifest_sha256) DO NOTHING
        RETURNING id
        """,
        (Jsonb(payload), digest),
    ).fetchone()
    if row is None:
        row = connection.execute(
            "SELECT id FROM atlas.corpus_snapshots WHERE manifest_sha256 = %s",
            (digest,),
        ).fetchone()
    connection.commit()
    return str(row[0]) if row else None


async def _execute(
    settings: Settings,
    manifest: CorpusManifest,
    collection_value: str | None,
    max_runs: int,
) -> int:
    collections = [CollectionSlug(collection_value)] if collection_value else list(CollectionSlug)
    dsn = settings.database_url.get_secret_value().replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )
    connection = psycopg.connect(dsn)
    client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())  # type: ignore[union-attr]
    http_client = httpx.AsyncClient()
    hosts = frozenset(candidate.canonical_url.split("/", 3)[2] for candidate in manifest.candidates)
    fetcher = SafeFetcher(client=http_client, policy=FetchPolicy(allowed_hosts=hosts))
    repository = PostgresIngestionRepository(connection)
    worker = IngestionWorker(
        repository=repository,
        discoverer=ManifestDiscoverer(manifest),
        fetcher=fetcher,
        embedder=OpenAIEmbeddingsAdapter(client=client),
    )
    service = IngestionService(repository)
    manifest_fingerprint = _manifest_fingerprint(manifest)
    try:
        for collection in collections:
            service.request_refresh(
                collection,
                trigger="operator",
                idempotency_key=(
                    f"bootstrap:{manifest.version}:{manifest_fingerprint}:{collection.value}"
                ),
                requested_by="atlas-corpus-bootstrap",
            )
        processed = await worker.run_until_empty(max_runs=max_runs)
        snapshot_id = _promote_snapshot(connection, manifest)
        print(
            json.dumps(
                {
                    "processed_runs": processed,
                    "snapshot_id": snapshot_id,
                    "snapshot_ready": snapshot_id is not None,
                },
                sort_keys=True,
            )
        )
        return 0
    finally:
        await fetcher.aclose()
        await client.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
