"""Ingestion worker orchestration with atomic stage/promote boundaries."""

from __future__ import annotations

import argparse
import asyncio
import json
import signal
from collections.abc import Sequence
from pathlib import Path
from typing import Protocol
from urllib.parse import urlparse

import httpx
import psycopg
from openai import AsyncOpenAI

from atlas.config import Settings
from atlas.domain import CollectionSlug
from atlas.ingestion.chunker import chunk_markdown
from atlas.ingestion.connectors import SourceCandidate
from atlas.ingestion.fetcher import FetchPolicy, SafeFetcher
from atlas.ingestion.manifest import ManifestDiscoverer, load_manifest
from atlas.ingestion.normalizer import normalize_document
from atlas.ingestion.service import (
    IngestionRepository,
    PostgresIngestionRepository,
    SourceDiscoverer,
)
from atlas.providers.openai_embeddings import OpenAIEmbeddingsAdapter
from atlas.providers.ports import EmbeddingProvider, SourceFetcher


class IngestionWorker:
    def __init__(
        self,
        *,
        repository: IngestionRepository,
        discoverer: SourceDiscoverer,
        fetcher: SourceFetcher,
        embedder: EmbeddingProvider,
        max_attempts: int = 3,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive")
        self._repository = repository
        self._discoverer = discoverer
        self._fetcher = fetcher
        self._embedder = embedder
        self._max_attempts = max_attempts

    async def run_once(self) -> bool:
        run = self._repository.claim_next()
        if run is None:
            return False
        try:
            candidates = await self._discover(run.collection)
            promoted = 0
            for candidate in candidates:
                fetched = await self._fetcher.fetch(candidate.canonical_url)
                document = normalize_document(
                    fetched.content,
                    content_type=fetched.content_type,
                )
                chunks = chunk_markdown(
                    document.markdown,
                    source_language=document.language,
                    ocr_used=document.ocr_used,
                    ocr_confidence=document.ocr_confidence,
                )
                vectors = await self._embedder.embed([chunk.text for chunk in chunks])
                if len(vectors) != len(chunks):
                    raise RuntimeError("embedding count does not match chunk count")
                self._repository.stage_source(run, candidate, document, chunks, vectors)
                self._repository.promote_source(run, candidate)
                promoted += 1
            self._repository.complete(
                run,
                discovered=len(candidates),
                promoted=promoted,
            )
        except Exception:
            # Persist only a controlled code; source bodies and provider details never enter logs.
            self._repository.fail(
                run,
                error_code="pipeline_failed",
                max_attempts=self._max_attempts,
            )
        return True

    async def run_until_empty(self, *, max_runs: int | None = None) -> int:
        processed = 0
        while max_runs is None or processed < max_runs:
            if not await self.run_once():
                break
            processed += 1
        return processed

    async def _discover(self, collection: CollectionSlug) -> Sequence[SourceCandidate]:
        return await self._discoverer.discover(collection)


class WorkerBatch(Protocol):
    """Small polling-loop seam used by deterministic tests and the managed runtime."""

    async def run_until_empty(self, *, max_runs: int | None = None) -> int: ...


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="atlas-worker")
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--poll-seconds", type=float)
    parser.add_argument("--max-runs-per-cycle", type=int)
    parser.add_argument(
        "--once",
        action="store_true",
        help="Drain one bounded batch and exit; managed workers poll continuously by default.",
    )
    return parser


async def run_polling_loop(
    worker: WorkerBatch,
    *,
    poll_seconds: float,
    max_runs_per_cycle: int,
    once: bool = False,
    stop_event: asyncio.Event | None = None,
) -> int:
    """Drain bounded batches and wait interruptibly when the durable queue is empty."""

    if poll_seconds <= 0:
        raise ValueError("poll_seconds must be positive")
    if max_runs_per_cycle < 1:
        raise ValueError("max_runs_per_cycle must be positive")
    stop = stop_event or asyncio.Event()
    total = 0
    while not stop.is_set():
        processed = await worker.run_until_empty(max_runs=max_runs_per_cycle)
        total += processed
        if once:
            return total
        try:
            await asyncio.wait_for(stop.wait(), timeout=poll_seconds)
        except TimeoutError:
            continue
    return total


def _install_stop_signals(stop_event: asyncio.Event) -> None:
    loop = asyncio.get_running_loop()
    for stop_signal in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(stop_signal, stop_event.set)
        except (NotImplementedError, RuntimeError):
            # Windows and embedded event loops may not expose POSIX signal handlers.
            continue


async def _run_managed_worker(args: argparse.Namespace) -> int:
    settings = Settings()
    manifest_path = args.manifest or settings.atlas_corpus_manifest
    manifest = load_manifest(manifest_path)
    if manifest.review_status != "approved":
        raise RuntimeError("atlas-worker requires an approved corpus manifest")
    if settings.openai_api_key is None or not settings.openai_api_key.get_secret_value().strip():
        raise RuntimeError("atlas-worker requires OPENAI_API_KEY in secret configuration")

    poll_seconds = (
        args.poll_seconds
        if args.poll_seconds is not None
        else settings.atlas_worker_poll_seconds
    )
    max_runs = (
        args.max_runs_per_cycle
        if args.max_runs_per_cycle is not None
        else settings.atlas_worker_max_runs_per_cycle
    )
    dsn = settings.database_url.get_secret_value().replace(
        "postgresql+psycopg://", "postgresql://", 1
    )
    connection = psycopg.connect(dsn)
    provider = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
    http_client = httpx.AsyncClient()
    hosts = frozenset(
        hostname
        for candidate in manifest.candidates
        if (hostname := urlparse(candidate.canonical_url).hostname) is not None
    )
    fetcher = SafeFetcher(
        client=http_client,
        policy=FetchPolicy(
            allowed_hosts=hosts,
            max_bytes=settings.atlas_ingestion_max_bytes,
        ),
    )
    worker = IngestionWorker(
        repository=PostgresIngestionRepository(connection),
        discoverer=ManifestDiscoverer(manifest),
        fetcher=fetcher,
        embedder=OpenAIEmbeddingsAdapter(client=provider),
        max_attempts=settings.atlas_ingestion_max_retries,
    )
    stop_event = asyncio.Event()
    _install_stop_signals(stop_event)
    try:
        processed = await run_polling_loop(
            worker,
            poll_seconds=poll_seconds,
            max_runs_per_cycle=max_runs,
            once=args.once,
            stop_event=stop_event,
        )
        print(
            json.dumps(
                {
                    "event": "worker_stopped",
                    "manifest_version": manifest.version,
                    "processed_runs": processed,
                },
                sort_keys=True,
            )
        )
        return processed
    finally:
        await fetcher.aclose()
        await provider.close()
        connection.close()


def run(argv: Sequence[str] | None = None) -> None:
    """Start the production ingestion worker with explicit, fail-closed dependencies."""

    args = build_parser().parse_args(argv)
    asyncio.run(_run_managed_worker(args))
