"""Safe, review-gated RSS/Atom fetching for previous-day news."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from datetime import UTC, datetime
from urllib.parse import urljoin, urlparse

import httpx

from atlas.news.feeds import FeedError, parse_feed
from atlas.news.schemas import NewsCandidate


@dataclass(frozen=True, slots=True)
class FeedPolicy:
    allowed_hosts: frozenset[str]
    review_status: str = "pending_operator_approval"
    max_bytes: int = 2_000_000
    timeout_seconds: float = 8.0
    max_redirects: int = 2


class NewsFeedFetcher:
    def __init__(self, client: httpx.AsyncClient, *, policy: FeedPolicy) -> None:
        self._client = client
        self._policy = policy

    async def fetch(
        self,
        url: str,
        *,
        publisher: str,
        authority_score: float = 0.7,
        topic_score: float = 0.7,
    ) -> list[NewsCandidate]:
        if self._policy.review_status != "approved":
            raise FeedError("news feed review is not approved")
        current = _safe_url(url, self._policy.allowed_hosts)
        for redirect_count in range(self._policy.max_redirects + 1):
            try:
                async with self._client.stream(
                    "GET",
                    current,
                    timeout=self._policy.timeout_seconds,
                    follow_redirects=False,
                    headers={
                        "Accept": "application/rss+xml, application/atom+xml, application/xml"
                    },
                ) as response:
                    if response.status_code in {301, 302, 303, 307, 308}:
                        if redirect_count >= self._policy.max_redirects:
                            raise FeedError("feed redirect limit exceeded")
                        location = response.headers.get("location")
                        if not location:
                            raise FeedError("feed redirect has no location")
                        current = _safe_url(urljoin(current, location), self._policy.allowed_hosts)
                        continue
                    if response.status_code != 200:
                        raise FeedError(f"feed returned HTTP {response.status_code}")
                    body = bytearray()
                    async for chunk in response.aiter_bytes():
                        body.extend(chunk)
                        if len(body) > self._policy.max_bytes:
                            raise FeedError("feed exceeds size limit")
                    return _deduplicate(
                        parse_feed(
                            bytes(body),
                            publisher=publisher,
                            captured_at=datetime.now(UTC),
                            authority_score=authority_score,
                            topic_score=topic_score,
                        )
                    )
            except httpx.HTTPError as exc:
                raise FeedError("feed request failed") from exc
        raise FeedError("feed redirect handling failed")


def _safe_url(url: str, allowed_hosts: frozenset[str]) -> str:
    parsed = urlparse(url)
    host = (parsed.hostname or "").casefold().rstrip(".")
    try:
        port = parsed.port
    except ValueError as exc:
        raise FeedError("feed URL has an invalid port") from exc
    if (
        parsed.scheme != "https"
        or not host
        or host not in {item.casefold().rstrip(".") for item in allowed_hosts}
        or parsed.username
        or parsed.password
        or port not in {None, 443}
    ):
        raise FeedError("feed URL is outside the HTTPS allowlist")
    return parsed.geturl()


def _deduplicate(candidates: Iterable[NewsCandidate]) -> list[NewsCandidate]:
    unique: dict[tuple[str, str], NewsCandidate] = {}
    for candidate in candidates:
        unique[(str(candidate.canonical_url), candidate.content_sha256)] = candidate
    return list(unique.values())


__all__ = ["FeedError", "FeedPolicy", "NewsFeedFetcher"]
