"""Governed source catalog kept separate from public answer collections."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from atlas.ingestion.governance import PolicyState

CollectionKind = Literal["framework", "model_provider"]


@dataclass(frozen=True, slots=True)
class GovernedCollection:
    slug: str
    display_name: str
    publisher: str
    kind: CollectionKind
    allowed_hosts: frozenset[str]
    allowed_paths: tuple[str, ...]
    refresh_interval_hours: int = 24
    ttl_hours: int = 168
    policy_state: PolicyState = PolicyState.APPROVED
    robots_status: str = "approved"
    terms_status: str = "approved"
    license_status: str = "approved"
    reviewer: str = "ATLAS maintainers"
    reviewed_at: str = "2026-08-06"


def build_default_catalog() -> list[GovernedCollection]:
    framework_rows = [
        (
            "framework-langgraph",
            "LangGraph",
            "LangChain",
            "docs.langchain.com",
            "/oss/python/langgraph/",
        ),
        (
            "framework-langchain",
            "LangChain",
            "LangChain",
            "docs.langchain.com",
            "/oss/python/langchain/",
        ),
        ("framework-llamaindex", "LlamaIndex", "LlamaIndex", "docs.llamaindex.ai", "/"),
        ("framework-crewai", "CrewAI", "CrewAI", "docs.crewai.com", "/"),
        ("framework-autogen", "AutoGen", "Microsoft", "microsoft.github.io", "/autogen/"),
        ("framework-pydanticai", "PydanticAI", "Pydantic", "ai.pydantic.dev", "/"),
        ("framework-dspy", "DSPy", "Stanford NLP", "dspy.ai", "/"),
        ("framework-haystack", "Haystack", "deepset", "docs.haystack.deepset.ai", "/"),
        (
            "framework-semantic-kernel",
            "Semantic Kernel",
            "Microsoft",
            "learn.microsoft.com",
            "/semantic-kernel/",
        ),
        ("framework-mastra", "Mastra", "Mastra", "mastra.ai", "/docs/"),
    ]
    provider_rows = [
        ("provider-openai", "OpenAI", "OpenAI", "developers.openai.com", "/api/"),
        ("provider-anthropic", "Anthropic", "Anthropic", "docs.anthropic.com", "/en/docs/"),
        ("provider-google-gemini", "Google Gemini", "Google", "ai.google.dev", "/gemini-api/docs/"),
        ("provider-mistral", "Mistral", "Mistral AI", "docs.mistral.ai", "/"),
        ("provider-cohere", "Cohere", "Cohere", "docs.cohere.com", "/"),
        ("provider-meta-llama", "Meta Llama", "Meta", "llama.meta.com", "/docs/"),
    ]
    definitions: list[GovernedCollection] = []
    for slug, name, publisher, host, path in framework_rows:
        definitions.append(
            GovernedCollection(
                slug=slug,
                display_name=name,
                publisher=publisher,
                kind="framework",
                allowed_hosts=frozenset({host}),
                allowed_paths=(path,),
                refresh_interval_hours=12,
            )
        )
    for slug, name, publisher, host, path in provider_rows:
        definitions.append(
            GovernedCollection(
                slug=slug,
                display_name=name,
                publisher=publisher,
                kind="model_provider",
                allowed_hosts=frozenset({host}),
                allowed_paths=(path,),
                refresh_interval_hours=12,
            )
        )
    return definitions
