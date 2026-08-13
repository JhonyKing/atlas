"""In-memory ingestion repository and discoverer for deterministic worker tests."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from dataclasses import dataclass, field, replace
from datetime import UTC, datetime
from uuid import UUID, uuid4

from atlas.domain import CollectionSlug
from atlas.ingestion.chunker import MarkdownChunk
from atlas.ingestion.connectors import SourceCandidate
from atlas.ingestion.normalizer import NormalizedDocument
from atlas.ingestion.service import IngestionRun, RunStatus
from atlas.providers.ports import FetchedSource


@dataclass
class FakeIngestionRepository:
    runs: dict[UUID, IngestionRun] = field(default_factory=dict)
    by_key: dict[str, UUID] = field(default_factory=dict)
    queue: list[UUID] = field(default_factory=list)
    active_collections: set[CollectionSlug] = field(default_factory=set)
    staged: list[tuple[UUID, SourceCandidate, NormalizedDocument, Sequence[MarkdownChunk]]] = field(
        default_factory=list
    )
    promoted: list[UUID] = field(default_factory=list)
    current_versions: dict[str, UUID] = field(default_factory=dict)
    completed: list[UUID] = field(default_factory=list)

    def enqueue(
        self,
        collection: CollectionSlug,
        trigger: str,
        idempotency_key: str,
        requested_by: str | None = None,
    ) -> UUID:
        del requested_by
        if idempotency_key in self.by_key:
            return self.by_key[idempotency_key]
        run_id = uuid4()
        self.by_key[idempotency_key] = run_id
        self.runs[run_id] = IngestionRun(
            id=run_id,
            collection=collection,
            trigger=trigger,
            idempotency_key=idempotency_key,
            attempt_count=0,
        )
        self.queue.append(run_id)
        return run_id

    def claim_next(self, collection: CollectionSlug | None = None) -> IngestionRun | None:
        for run_id in self.queue:
            run = self.runs[run_id]
            if collection is not None and run.collection is not collection:
                continue
            if run.collection in self.active_collections:
                continue
            self.queue.remove(run_id)
            self.active_collections.add(run.collection)
            claimed = replace(run, status="running")
            self.runs[run_id] = claimed
            return claimed
        return None

    def stage_source(
        self,
        run: IngestionRun,
        candidate: SourceCandidate,
        document: NormalizedDocument,
        chunks: Sequence[MarkdownChunk],
        vectors: Sequence[Sequence[float]],
    ) -> None:
        del vectors
        self.staged.append((run.id, candidate, document, chunks))

    def promote_source(self, run: IngestionRun, candidate: SourceCandidate) -> None:
        version_id = uuid4()
        self.current_versions[candidate.canonical_url] = version_id
        self.promoted.append(version_id)

    def complete(self, run: IngestionRun, *, discovered: int, promoted: int) -> None:
        del discovered, promoted
        self.runs[run.id] = replace(self.runs[run.id], status="succeeded")
        self.completed.append(run.id)
        self.active_collections.discard(run.collection)

    def fail(self, run: IngestionRun, *, error_code: str, max_attempts: int) -> None:
        del error_code
        attempt_count = run.attempt_count + 1
        status: RunStatus = "dead_letter" if attempt_count >= max_attempts else "queued"
        self.runs[run.id] = replace(run, status=status, attempt_count=attempt_count)
        self.active_collections.discard(run.collection)
        if status == "queued":
            self.queue.append(run.id)


class FakeDiscoverer:
    def __init__(self, candidates: Sequence[SourceCandidate]) -> None:
        self.candidates = tuple(candidates)
        self.fail = False

    async def discover(self, collection: CollectionSlug) -> Sequence[SourceCandidate]:
        if self.fail:
            raise RuntimeError("fixture discovery failed")
        return [candidate for candidate in self.candidates if candidate.collection is collection]


class FakeFetcher:
    def __init__(self, content: bytes) -> None:
        self.content = content

    async def fetch(self, url: str) -> FetchedSource:
        from atlas.providers.ports import FetchedSource

        return FetchedSource(
            requested_url=url,
            final_url=url,
            content=self.content,
            content_type="text/markdown",
            fetched_at=datetime.now(UTC),
        )


async def yield_once() -> None:
    await asyncio.sleep(0)
