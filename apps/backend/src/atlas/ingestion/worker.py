"""Ingestion worker orchestration with atomic stage/promote boundaries."""

from __future__ import annotations

from collections.abc import Sequence

from atlas.domain import CollectionSlug
from atlas.ingestion.chunker import chunk_markdown
from atlas.ingestion.connectors import SourceCandidate
from atlas.ingestion.normalizer import normalize_document
from atlas.ingestion.service import IngestionRepository, SourceDiscoverer
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


def run() -> None:
    """Console entrypoint placeholder until deployment wiring supplies dependencies."""

    raise RuntimeError(
        "Configure the PostgreSQL repository, connector registry, fetcher, and embedder before "
        "starting the worker entrypoint."
    )
