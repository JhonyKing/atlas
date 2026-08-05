"""Non-blocking, idempotent previous-day news selection service."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from typing import Protocol

from atlas.news.ranking import select_previous_day
from atlas.news.schemas import NewsCandidate, NewsSelection


class DailyNewsSelectionStore(Protocol):
    def get(self, day: date) -> NewsSelection | None: ...

    def put_if_absent(self, day: date, selection: NewsSelection) -> NewsSelection: ...


class InMemoryDailyNewsSelectionStore:
    def __init__(self) -> None:
        self._selections: dict[date, NewsSelection] = {}

    def get(self, day: date) -> NewsSelection | None:
        return self._selections.get(day)

    def put_if_absent(self, day: date, selection: NewsSelection) -> NewsSelection:
        return self._selections.setdefault(day, selection)


class DailyNewsRefreshService:
    """Persist one result per UTC day without coupling to answer execution."""

    def __init__(self, store: DailyNewsSelectionStore | None = None) -> None:
        self._store = store or InMemoryDailyNewsSelectionStore()
        self._lock = asyncio.Lock()

    async def refresh(
        self,
        candidates: Sequence[NewsCandidate],
        *,
        now: datetime | None = None,
    ) -> NewsSelection:
        observed = (now or datetime.now(UTC)).astimezone(UTC)
        target_day = observed.date() - timedelta(days=1)
        async with self._lock:
            existing = self._store.get(target_day)
            if existing is not None:
                return existing
            selection = select_previous_day(candidates, now=observed)
            return self._store.put_if_absent(target_day, selection)

    def get_daily(self, *, now: datetime | None = None) -> NewsSelection:
        observed = (now or datetime.now(UTC)).astimezone(UTC)
        target_day = observed.date() - timedelta(days=1)
        return self._store.get(target_day) or select_previous_day((), now=observed)
