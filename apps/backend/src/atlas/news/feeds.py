"""Bounded RSS/Atom parsing without storing full articles."""

from __future__ import annotations

import hashlib
import re
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from xml.etree import ElementTree

from pydantic import HttpUrl

from atlas.news.schemas import NewsCandidate


class FeedError(ValueError):
    """A feed is malformed, unsafe or missing required attribution metadata."""


def parse_feed(
    payload: bytes,
    *,
    publisher: str,
    captured_at: datetime | None = None,
    authority_score: float = 0.7,
    topic_score: float = 0.7,
) -> list[NewsCandidate]:
    if len(payload) > 2_000_000:
        raise FeedError("feed exceeds size limit")
    try:
        root = ElementTree.fromstring(payload)
    except ElementTree.ParseError as exc:
        raise FeedError("feed XML is invalid") from exc
    captured = (captured_at or datetime.now(UTC)).astimezone(UTC)
    candidates: list[NewsCandidate] = []
    for item in root.iter():
        if _local(item.tag) not in {"item", "entry"}:
            continue
        values = {_local(child.tag): child for child in item}
        title = _text(values.get("title"))
        link = _link(values.get("link"))
        published = _parse_date(
            _text(values.get("pubdate"))
            or _text(values.get("published"))
            or _text(values.get("updated"))
        )
        if not title or not link or published is None:
            continue
        if not link.startswith("https://"):
            continue
        summary = _bounded_summary(
            _text(values.get("description"))
            or _text(values.get("summary"))
            or _text(values.get("content"))
        )
        digest = hashlib.sha256(f"{publisher}|{link}|{published.isoformat()}".encode()).hexdigest()
        candidates.append(
            NewsCandidate(
                title=title,
                summary=summary,
                publisher=publisher,
                canonical_url=HttpUrl(link),
                published_at=published,
                captured_at=captured,
                authority_score=authority_score,
                topic_score=_topic_score(title, summary, topic_score),
                content_sha256=digest,
            )
        )
    return candidates


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].casefold()


def _text(node: ElementTree.Element | None) -> str:
    if node is None:
        return ""
    return " ".join(unescape("".join(node.itertext())).split())


def _link(node: ElementTree.Element | None) -> str:
    if node is None:
        return ""
    return node.attrib.get("href", "") or _text(node)


def _parse_date(value: str) -> datetime | None:
    if not value:
        return None
    try:
        result = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            result = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None
    if result.tzinfo is None:
        return None
    return result.astimezone(UTC)


def _bounded_summary(value: str) -> str:
    value = re.sub(r"<[^>]+>", " ", value)
    return " ".join(value.split())[:4000]


_TECHNOLOGY_TERMS = {
    "ai",
    "artificial intelligence",
    "cloud",
    "cyber",
    "cybersecurity",
    "data",
    "internet",
    "model",
    "online",
    "openai",
    "privacy",
    "software",
    "tech",
    "technology",
    "web",
}


def _topic_score(title: str, summary: str, configured_score: float) -> float:
    """Bound the editorial hint by explicit technology terms in feed metadata."""

    haystack = f"{title} {summary}".casefold()
    matches = sum(term in haystack for term in _TECHNOLOGY_TERMS)
    evidence_score = 0.2 if matches == 0 else min(1.0, 0.4 + 0.15 * matches)
    return round(min(configured_score, evidence_score), 6)


__all__ = ["FeedError", "parse_feed"]
