"""Content-minimized observability fields for the daily-news lifecycle."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from atlas.news.schemas import NewsSelection


def news_observation(
    selection: NewsSelection,
    *,
    latency_ms: float,
    feed_count: int | None = None,
    feeds_succeeded: int | None = None,
) -> Mapping[str, Any]:
    """Return safe scalar metadata; never include title, summary or article URL."""

    fields: dict[str, Any] = {
        "stage": "daily_news",
        "status": selection.status,
        "day": selection.day.isoformat(),
        "timezone": selection.timezone,
        "candidate_count": selection.candidate_count,
        "latency_ms": round(max(latency_ms, 0.0), 2),
    }
    if selection.score is not None:
        fields["selection_score"] = selection.score
    if selection.reason_code != "none":
        fields["reason_code"] = selection.reason_code
    if feed_count is not None:
        fields["feed_count"] = feed_count
    if feeds_succeeded is not None:
        fields["feeds_succeeded"] = feeds_succeeded
    return fields


__all__ = ["news_observation"]
