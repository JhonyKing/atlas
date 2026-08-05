"""Deterministic previous-day ranking with an explicit insufficient-signal state."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime, timedelta
from typing import Protocol

from atlas.news.schemas import NewsCandidate, NewsSelection


class DailyNewsProvider(Protocol):
    def get_daily(self, *, now: datetime | None = None) -> NewsSelection: ...


def select_previous_day(
    candidates: Sequence[NewsCandidate],
    *,
    now: datetime | None = None,
    minimum_score: float = 0.55,
) -> NewsSelection:
    observed = (now or datetime.now(UTC)).astimezone(UTC)
    target_day = observed.date() - timedelta(days=1)
    eligible = [
        candidate for candidate in candidates if candidate.published_at.date() == target_day
    ]
    ranked = sorted(eligible, key=_sort_key, reverse=True)
    if not ranked:
        return NewsSelection(status="unavailable", day=target_day, reason_code="no_evidence")
    winner = ranked[0]
    score = _score(winner)
    if score < minimum_score:
        return NewsSelection(
            status="unavailable",
            day=target_day,
            candidate_count=len(ranked),
            score=score,
            reason_code="insufficient_signal",
        )
    return NewsSelection(
        status="ready",
        day=target_day,
        candidate=winner,
        candidate_count=len(ranked),
        score=score,
    )


class InMemoryDailyNewsService:
    """Fixture-friendly service; production will replace it with a persisted feed job."""

    def __init__(self, candidates: Sequence[NewsCandidate] = ()) -> None:
        self._candidates = tuple(candidates)

    def get_daily(self, *, now: datetime | None = None) -> NewsSelection:
        return select_previous_day(self._candidates, now=now)


def unavailable_news(
    *, now: datetime | None = None, reason_code: str = "not_configured"
) -> NewsSelection:
    observed = (now or datetime.now(UTC)).astimezone(UTC)
    target_day = observed.date() - timedelta(days=1)
    return NewsSelection(status="unavailable", day=target_day, reason_code=reason_code)  # type: ignore[arg-type]


def _score(candidate: NewsCandidate) -> float:
    corroboration = min(candidate.corroboration_count, 3) / 3
    return round(
        0.45 * candidate.authority_score
        + 0.35 * candidate.topic_score
        + 0.20 * corroboration,
        6,
    )


def _sort_key(candidate: NewsCandidate) -> tuple[float, datetime, str, str]:
    return (
        _score(candidate),
        candidate.published_at,
        candidate.publisher,
        str(candidate.canonical_url),
    )


__all__ = [
    "DailyNewsProvider",
    "InMemoryDailyNewsService",
    "select_previous_day",
    "unavailable_news",
]
