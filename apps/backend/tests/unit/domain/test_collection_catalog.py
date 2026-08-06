from atlas.domain import CollectionSlug
from atlas.ingestion.connectors import ConnectorRegistry


def test_catalog_prioritizes_anthropic_then_gemini_after_the_initial_three() -> None:
    assert list(CollectionSlug) == [
        CollectionSlug.LANGGRAPH,
        CollectionSlug.LANGCHAIN,
        CollectionSlug.OPENAI,
        CollectionSlug.ANTHROPIC,
        CollectionSlug.GEMINI,
    ]


def test_new_connectors_are_registered_but_disabled_until_source_review() -> None:
    registry = ConnectorRegistry()
    assert registry.is_enabled(CollectionSlug.ANTHROPIC) is False
    assert registry.is_enabled(CollectionSlug.GEMINI) is False
