"""Reproducible corpus bootstrap with a safe dry-run default."""

from __future__ import annotations

import argparse
import asyncio
import json
from collections.abc import Sequence
from pathlib import Path

import httpx
import psycopg
from openai import AsyncOpenAI

from atlas.config import Settings
from atlas.domain import CollectionSlug
from atlas.ingestion.fetcher import FetchPolicy, SafeFetcher
from atlas.ingestion.manifest import CorpusManifest, load_manifest
from atlas.ingestion.service import IngestionService, PostgresIngestionRepository
from atlas.ingestion.worker import IngestionWorker
from atlas.providers.openai_embeddings import OpenAIEmbeddingsAdapter


class ManifestDiscoverer:
    def __init__(self, manifest: CorpusManifest) -> None:
        self._manifest = manifest

    async def discover(self, collection: CollectionSlug):
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
    settings = Settings()
    if settings.openai_api_key is None or not settings.openai_api_key.get_secret_value().strip():
        raise RuntimeError("--execute requires OPENAI_API_KEY in secret configuration")
    return asyncio.run(_execute(settings, manifest, args.collection, args.max_runs))


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
    hosts = frozenset(
        candidate.canonical_url.split("/", 3)[2]
        for candidate in manifest.candidates
    )
    fetcher = SafeFetcher(client=http_client, policy=FetchPolicy(allowed_hosts=hosts))
    repository = PostgresIngestionRepository(connection)
    worker = IngestionWorker(
        repository=repository,
        discoverer=ManifestDiscoverer(manifest),
        fetcher=fetcher,
        embedder=OpenAIEmbeddingsAdapter(client=client),
    )
    service = IngestionService(repository)
    try:
        for collection in collections:
            service.request_refresh(
                collection,
                trigger="operator",
                idempotency_key=f"bootstrap:{manifest.version}:{collection.value}",
                requested_by="atlas-corpus-bootstrap",
            )
        processed = await worker.run_until_empty(max_runs=max_runs)
        print(json.dumps({"processed_runs": processed}, sort_keys=True))
        return 0
    finally:
        await fetcher.aclose()
        await client.close()
        connection.close()


if __name__ == "__main__":
    raise SystemExit(main())
