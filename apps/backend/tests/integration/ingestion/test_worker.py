import asyncio

import pytest

from atlas.domain import CollectionSlug, SourceType
from atlas.ingestion.connectors import SourceCandidate
from atlas.ingestion.service import IngestionService
from atlas.ingestion.worker import IngestionWorker
from atlas.providers.openai_embeddings import EMBEDDING_DIMENSIONS
from tests.fakes import DeterministicEmbeddingProvider
from tests.fakes.ingestion import FakeDiscoverer, FakeFetcher, FakeIngestionRepository


def candidate() -> SourceCandidate:
    return SourceCandidate(
        collection=CollectionSlug.LANGGRAPH,
        canonical_url="https://docs.langchain.com/oss/python/langgraph/fixture.md",
        title="Fixture",
        source_type=SourceType.DOCUMENTATION,
    )


def make_worker(repository: FakeIngestionRepository, discoverer: FakeDiscoverer) -> IngestionWorker:
    return IngestionWorker(
        repository=repository,
        discoverer=discoverer,
        fetcher=FakeFetcher(b"# Fixture\n\nOfficial content."),
        embedder=DeterministicEmbeddingProvider(dimensions=EMBEDDING_DIMENSIONS),
        max_attempts=2,
    )


def test_manual_and_scheduled_requests_are_idempotent() -> None:
    repository = FakeIngestionRepository()
    service = IngestionService(repository)

    first = service.request_refresh(CollectionSlug.LANGGRAPH, "operator", "same-key")
    repeated = service.request_refresh(CollectionSlug.LANGGRAPH, "scheduled", "same-key")

    assert first == repeated
    assert len(repository.runs) == 1


@pytest.mark.asyncio
async def test_worker_embeds_and_promotes_only_after_successful_pipeline() -> None:
    repository = FakeIngestionRepository()
    service = IngestionService(repository)
    service.request_refresh(CollectionSlug.LANGGRAPH, "operator", "pipeline-key")
    discoverer = FakeDiscoverer([candidate()])
    worker = make_worker(repository, discoverer)

    assert await worker.run_once() is True
    assert len(repository.staged) == 1
    assert len(repository.promoted) == 1
    assert len(repository.completed) == 1


@pytest.mark.asyncio
async def test_collection_lock_allows_only_one_worker_to_claim_a_run() -> None:
    repository = FakeIngestionRepository()
    service = IngestionService(repository)
    service.request_refresh(CollectionSlug.LANGGRAPH, "scheduled", "lock-key")
    discoverer = FakeDiscoverer([candidate()])
    worker = make_worker(repository, discoverer)

    results = await asyncio.gather(worker.run_once(), worker.run_once())

    assert sorted(results) == [False, True]
    assert len(repository.completed) == 1


@pytest.mark.asyncio
async def test_worker_requeues_transient_failures_and_dead_letters_after_budget() -> None:
    repository = FakeIngestionRepository()
    service = IngestionService(repository)
    run_id = service.request_refresh(CollectionSlug.LANGGRAPH, "operator", "retry-key")
    discoverer = FakeDiscoverer([candidate()])
    discoverer.fail = True
    worker = make_worker(repository, discoverer)

    assert await worker.run_once() is True
    assert repository.runs[run_id].status == "queued"
    assert await worker.run_once() is True
    assert repository.runs[run_id].status == "dead_letter"
    assert repository.promoted == []
