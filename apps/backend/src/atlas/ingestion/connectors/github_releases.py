"""Bounded GitHub release/changelog payload adapter."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ReleaseCandidate:
    collection: str
    canonical_url: str
    title: str
    version_label: str
    published_at: datetime | None


def parse_github_releases(payload: object, *, collection: str) -> list[ReleaseCandidate]:
    if not isinstance(payload, Sequence) or isinstance(payload, (str, bytes)):
        raise ValueError("release payload must be a sequence")
    results: list[ReleaseCandidate] = []
    seen: set[str] = set()
    for item in payload:
        if not isinstance(item, dict):
            continue
        url, tag = item.get("html_url"), item.get("tag_name")
        if not isinstance(url, str) or not url.startswith("https://") or not isinstance(tag, str):
            continue
        if url in seen:
            continue
        seen.add(url)
        published = item.get("published_at")
        date = None
        if isinstance(published, str):
            try:
                date = datetime.fromisoformat(published.replace("Z", "+00:00"))
            except ValueError:
                date = None
        title_value = item.get("name")
        title = title_value if isinstance(title_value, str) else tag
        results.append(ReleaseCandidate(collection, url, title, tag, date))
    return results
