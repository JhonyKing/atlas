"""Official-source discovery behind explicit governance approvals."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from urllib.parse import urlparse

from atlas.domain import CollectionSlug, SourceType


class ConnectorDisabled(RuntimeError):
    """A source connector cannot run until its review explicitly approves it."""


@dataclass(frozen=True, slots=True)
class SourceReview:
    collection: CollectionSlug
    status: Literal["approved", "disabled"]
    allowed_hosts: frozenset[str]
    allowed_paths: tuple[str, ...]
    reviewer: str
    reviewed_on: str


@dataclass(frozen=True, slots=True)
class SourceCandidate:
    collection: CollectionSlug
    canonical_url: str
    title: str
    source_type: SourceType
    source_revision_url: str | None = None
    version_label: str | None = None
    published_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class SourceConnector:
    collection: CollectionSlug
    review: SourceReview

    def discover_llms_index(self, text: str) -> list[SourceCandidate]:
        return parse_llms_index(
            text,
            collection=self.collection,
            allowed_hosts=self.review.allowed_hosts,
            allowed_paths=self.review.allowed_paths,
        )

    def discover_releases(self, payload: object) -> list[SourceCandidate]:
        return parse_release_payload(payload, collection=self.collection)


def parse_llms_index(
    text: str,
    *,
    collection: CollectionSlug,
    allowed_hosts: frozenset[str],
    allowed_paths: tuple[str, ...],
) -> list[SourceCandidate]:
    pattern = re.compile(r"\[([^\]]+)\]\((https://[^)\s]+)\)")
    candidates: list[SourceCandidate] = []
    seen: set[str] = set()
    for match in pattern.finditer(text):
        title = " ".join(match.group(1).split())
        url = match.group(2)
        parsed = urlparse(url)
        host = (parsed.hostname or "").casefold().rstrip(".")
        path = parsed.path or "/"
        if (
            parsed.scheme != "https"
            or host not in {item.casefold().rstrip(".") for item in allowed_hosts}
            or not any(path.startswith(prefix) for prefix in allowed_paths)
            or url in seen
        ):
            continue
        seen.add(url)
        candidates.append(
            SourceCandidate(
                collection=collection,
                canonical_url=url,
                title=title,
                source_type=SourceType.DOCUMENTATION,
            )
        )
    return candidates


def parse_release_payload(payload: object, *, collection: CollectionSlug) -> list[SourceCandidate]:
    if not isinstance(payload, list):
        raise ValueError("release payload must be a list")
    candidates: list[SourceCandidate] = []
    for item in payload:
        if not isinstance(item, dict):
            continue
        url = item.get("html_url")
        tag = item.get("tag_name")
        if not isinstance(url, str) or not isinstance(tag, str) or not url.startswith("https://"):
            continue
        published_at = _parse_datetime(item.get("published_at"))
        title_value = item.get("name") or tag
        title = title_value if isinstance(title_value, str) else tag
        candidates.append(
            SourceCandidate(
                collection=collection,
                canonical_url=url,
                source_revision_url=url,
                title=title,
                source_type=SourceType.RELEASE_NOTE,
                version_label=tag,
                published_at=published_at,
            )
        )
    return candidates


class ConnectorRegistry:
    def __init__(self, *, reviews: dict[CollectionSlug, SourceReview] | None = None) -> None:
        self._reviews = reviews or _default_reviews()

    def get(self, collection: CollectionSlug) -> SourceConnector:
        review = self._reviews.get(collection)
        if review is None or review.status != "approved":
            raise ConnectorDisabled(
                f"{collection.value} connector requires an approved source review"
            )
        return SourceConnector(collection=collection, review=review)

    def is_enabled(self, collection: CollectionSlug) -> bool:
        review = self._reviews.get(collection)
        return review is not None and review.status == "approved"


def _default_reviews() -> dict[CollectionSlug, SourceReview]:
    return {
        CollectionSlug.LANGGRAPH: SourceReview(
            collection=CollectionSlug.LANGGRAPH,
            status="disabled",
            allowed_hosts=frozenset({"docs.langchain.com", "api.github.com"}),
            allowed_paths=("/oss/python/langgraph/", "/repos/langchain-ai/langgraph/releases"),
            reviewer="ATLAS maintainers",
            reviewed_on="2026-08-04",
        ),
        CollectionSlug.LANGCHAIN: SourceReview(
            collection=CollectionSlug.LANGCHAIN,
            status="disabled",
            allowed_hosts=frozenset({"docs.langchain.com", "api.github.com"}),
            allowed_paths=("/oss/python/langchain/", "/repos/langchain-ai/langchain/releases"),
            reviewer="ATLAS maintainers",
            reviewed_on="2026-08-04",
        ),
        CollectionSlug.OPENAI: SourceReview(
            collection=CollectionSlug.OPENAI,
            status="disabled",
            allowed_hosts=frozenset({"developers.openai.com"}),
            allowed_paths=("/api/",),
            reviewer="ATLAS maintainers",
            reviewed_on="2026-08-04",
        ),
        CollectionSlug.ANTHROPIC: SourceReview(
            collection=CollectionSlug.ANTHROPIC,
            status="approved",
            allowed_hosts=frozenset({"docs.anthropic.com", "platform.claude.com"}),
            allowed_paths=("/en/docs/", "/en/api/", "/docs/en/"),
            reviewer="ATLAS maintainers",
            reviewed_on="2026-08-05",
        ),
        CollectionSlug.GEMINI: SourceReview(
            collection=CollectionSlug.GEMINI,
            status="approved",
            allowed_hosts=frozenset({"ai.google.dev"}),
            allowed_paths=("/gemini-api/docs/", "/api/"),
            reviewer="ATLAS maintainers",
            reviewed_on="2026-08-05",
        ),
    }


def _parse_datetime(value: object) -> datetime | None:
    if not isinstance(value, str):
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


__all__ = [
    "ConnectorDisabled",
    "ConnectorRegistry",
    "SourceCandidate",
    "SourceConnector",
    "SourceReview",
    "parse_llms_index",
    "parse_release_payload",
]
