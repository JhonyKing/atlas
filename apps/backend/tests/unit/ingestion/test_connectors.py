import json
from pathlib import Path

import pytest

from atlas.domain import CollectionSlug, SourceType
from atlas.ingestion.connectors import (
    ConnectorDisabled,
    ConnectorRegistry,
    SourceReview,
    parse_llms_index,
    parse_release_payload,
)

FIXTURES = Path(__file__).parents[2] / "fixtures" / "sources"


def approved_review(collection: CollectionSlug) -> SourceReview:
    return SourceReview(
        collection=collection,
        status="approved",
        allowed_hosts=frozenset({"docs.langchain.com", "developers.openai.com"}),
        allowed_paths=("/oss/python/", "/api/docs/"),
        reviewer="test-reviewer",
        reviewed_on="2026-08-04",
    )


def test_llms_index_discovery_is_allowlisted_and_deduplicated() -> None:
    index = (FIXTURES / "langchain_llms.txt").read_text(encoding="utf-8")

    candidates = parse_llms_index(
        index,
        collection=CollectionSlug.LANGCHAIN,
        allowed_hosts=frozenset({"docs.langchain.com"}),
        allowed_paths=("/oss/python/",),
    )

    assert [candidate.title for candidate in candidates] == ["Overview", "Retrieval"]
    assert all(candidate.source_type is SourceType.DOCUMENTATION for candidate in candidates)
    assert all(
        candidate.canonical_url.startswith("https://docs.langchain.com/")
        for candidate in candidates
    )


def test_release_discovery_preserves_tag_revision_and_published_date() -> None:
    payload = json.loads((FIXTURES / "langgraph_releases.json").read_text(encoding="utf-8"))

    candidates = parse_release_payload(payload, collection=CollectionSlug.LANGGRAPH)

    assert len(candidates) == 1
    assert candidates[0].source_type is SourceType.RELEASE_NOTE
    assert candidates[0].version_label == "langgraph==1.2.9"
    assert candidates[0].source_revision_url == candidates[0].canonical_url
    assert candidates[0].published_at is not None


def test_registry_keeps_every_collection_disabled_without_explicit_review() -> None:
    registry = ConnectorRegistry()

    with pytest.raises(ConnectorDisabled, match="review"):
        registry.get(CollectionSlug.LANGGRAPH)


def test_registry_enables_only_a_collection_with_approved_review() -> None:
    registry = ConnectorRegistry(
        reviews={CollectionSlug.LANGCHAIN: approved_review(CollectionSlug.LANGCHAIN)}
    )

    connector = registry.get(CollectionSlug.LANGCHAIN)
    assert connector.collection is CollectionSlug.LANGCHAIN
    assert registry.is_enabled(CollectionSlug.LANGCHAIN) is True
    assert registry.is_enabled(CollectionSlug.OPENAI) is False
