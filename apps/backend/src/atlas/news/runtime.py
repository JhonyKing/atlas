"""Runtime provider for the reviewed, bounded previous-day news feeds."""

from __future__ import annotations

import asyncio
import threading
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from urllib.parse import urlparse

import httpx
import yaml  # type: ignore[import-untyped]

from atlas.news.fetch import FeedPolicy, NewsFeedFetcher
from atlas.news.ranking import DailyNewsProvider, select_previous_day, unavailable_news
from atlas.news.schemas import NewsCandidate, NewsSelection


class LiveDailyNewsService(DailyNewsProvider):
    """Fetch reviewed RSS metadata once per UTC day and cache the selection."""

    def __init__(self, manifest_path: Path) -> None:
        raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict) or raw.get("review_status") != "approved":
            raise ValueError("news manifest must be approved")
        feeds = raw.get("feeds")
        if not isinstance(feeds, list) or not feeds:
            raise ValueError("news manifest must contain feeds")
        self._feeds = tuple(item for item in feeds if isinstance(item, dict))
        self._hosts = frozenset(
            host
            for item in self._feeds
            if item.get("url")
            for host in [urlparse(str(item["url"])).hostname]
            if isinstance(host, str)
        )
        self._manifest_path = manifest_path
        self._cache: dict[date, NewsSelection] = {}
        self._lock = threading.Lock()

    def get_daily(self, *, now: datetime | None = None) -> NewsSelection:
        observed = (now or datetime.now(UTC)).astimezone(UTC)
        target_day = observed.date() - timedelta(days=1)
        with self._lock:
            cached = self._cache.get(target_day)
        if cached is not None:
            return cached
        try:
            candidates = asyncio.run(self._fetch_candidates())
            selection = select_previous_day(candidates, now=observed)
        except Exception:
            selection = unavailable_news(now=observed, reason_code="no_evidence")
        with self._lock:
            return self._cache.setdefault(target_day, selection)

    async def _fetch_candidates(self) -> list[NewsCandidate]:
        candidates: list[NewsCandidate] = []
        async with httpx.AsyncClient() as client:
            fetcher = NewsFeedFetcher(
                client,
                policy=FeedPolicy(allowed_hosts=self._hosts, review_status="approved"),
            )
            for item in self._feeds:
                try:
                    candidates.extend(
                        await fetcher.fetch(
                            str(item["url"]),
                            publisher=str(item["publisher"]),
                            authority_score=float(item.get("authority_score", 0.7)),
                            topic_score=0.7,
                        )
                    )
                except Exception:
                    continue
        return candidates


__all__ = ["LiveDailyNewsService"]
