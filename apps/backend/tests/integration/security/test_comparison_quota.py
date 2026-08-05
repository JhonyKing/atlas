from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from atlas.persistence.comparison_quota import (
    ComparisonQuotaExceeded,
    ComparisonQuotaService,
    InMemoryComparisonQuotaRepository,
)


def test_comparison_quota_accepts_five_runs_and_rejects_the_sixth() -> None:
    repository = InMemoryComparisonQuotaRepository(limit=5, window=timedelta(hours=24))
    quota = ComparisonQuotaService(repository)
    now = datetime(2026, 8, 5, 12, tzinfo=UTC)

    reservations = [
        quota.reserve("a" * 64, f"comparison-key-{index:02d}", uuid4(), now=now)
        for index in range(5)
    ]

    assert reservations[-1].remaining == 0
    with pytest.raises(ComparisonQuotaExceeded) as error:
        quota.reserve("a" * 64, "comparison-key-06", uuid4(), now=now)
    assert error.value.retry_at == now + timedelta(hours=24)


def test_comparison_quota_is_idempotent_and_isolated_by_visitor() -> None:
    repository = InMemoryComparisonQuotaRepository(limit=5, window=timedelta(hours=24))
    quota = ComparisonQuotaService(repository)
    now = datetime(2026, 8, 5, 12, tzinfo=UTC)
    first_run = uuid4()

    first = quota.reserve("a" * 64, "comparison-idempotent-01", first_run, now=now)
    repeated = quota.reserve("a" * 64, "comparison-idempotent-01", uuid4(), now=now)
    other_visitor = quota.reserve("b" * 64, "comparison-idempotent-01", uuid4(), now=now)

    assert first.run_id == first_run
    assert repeated.run_id == first_run
    assert repeated.is_new is False
    assert other_visitor.is_new is True


def test_comparison_quota_expires_after_rolling_window() -> None:
    repository = InMemoryComparisonQuotaRepository(limit=5, window=timedelta(hours=24))
    quota = ComparisonQuotaService(repository)
    start = datetime(2026, 8, 5, 12, tzinfo=UTC)

    for index in range(5):
        quota.reserve("c" * 64, f"comparison-expiry-{index:02d}", uuid4(), now=start)

    reservation = quota.reserve(
        "c" * 64,
        "comparison-expiry-after-window",
        uuid4(),
        now=start + timedelta(hours=24, seconds=1),
    )
    assert reservation.is_new is True
