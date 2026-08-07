from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from fastapi.testclient import TestClient
from pydantic import HttpUrl

from atlas.api.main import create_app
from atlas.domain import (
    CollectionSlug,
    CollectionState,
    CollectionStatus,
    CorpusStatus,
    SourceType,
)

SNAPSHOT_ID = UUID("00000000-0000-0000-0000-000000000701")


class FakeCorpusService:
    def __init__(self, payload: CorpusStatus | None) -> None:
        self.payload = payload

    def get_status(self) -> CorpusStatus | None:
        return self.payload


def corpus_payload() -> CorpusStatus:
    return CorpusStatus(
        snapshot_id=SNAPSHOT_ID,
        generated_at=datetime(2026, 8, 4, 12, 0, tzinfo=UTC),
        collections=[
            CollectionStatus(
                slug=CollectionSlug.LANGGRAPH,
                name="LangGraph",
                publisher="LangChain",
                source_types=[SourceType.DOCUMENTATION, SourceType.RELEASE_NOTE],
                status=CollectionState.READY,
                last_success_at=datetime(2026, 8, 4, 10, 0, tzinfo=UTC),
                last_attempt_at=datetime(2026, 8, 4, 10, 0, tzinfo=UTC),
                canonical_root=HttpUrl("https://langchain-ai.github.io/langgraph/"),
            ),
            CollectionStatus(
                slug=CollectionSlug.LANGCHAIN,
                name="LangChain",
                publisher="LangChain",
                source_types=[SourceType.DOCUMENTATION, SourceType.CHANGELOG],
                status=CollectionState.STALE,
                last_success_at=datetime(2026, 8, 1, 10, 0, tzinfo=UTC),
                last_attempt_at=datetime(2026, 8, 4, 10, 0, tzinfo=UTC),
                canonical_root=HttpUrl("https://python.langchain.com/"),
            ),
            CollectionStatus(
                slug=CollectionSlug.OPENAI,
                name="OpenAI API",
                publisher="OpenAI",
                source_types=[SourceType.DOCUMENTATION],
                status=CollectionState.UNAVAILABLE,
                canonical_root=HttpUrl("https://platform.openai.com/docs/"),
            ),
        ],
    )


def test_corpus_status_publishes_snapshot_and_all_supported_collections() -> None:
    async def database_probe() -> bool:
        return True

    client = TestClient(
        create_app(
            database_probe=database_probe,
            corpus_service=FakeCorpusService(corpus_payload()),
        )
    )

    response = client.get("/v1/corpus")

    assert response.status_code == 200
    assert response.json() == corpus_payload().model_dump(mode="json")
    assert response.headers["cache-control"] == "no-store"


def test_corpus_status_returns_controlled_unavailable_when_service_is_missing() -> None:
    async def database_probe() -> bool:
        return True

    client = TestClient(create_app(database_probe=database_probe))

    response = client.get("/v1/corpus")

    assert response.status_code == 503
    assert response.json()["error_code"] == "corpus_unavailable"
