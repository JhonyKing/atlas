from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from datetime import UTC, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.testclient import TestClient

from atlas.api.middleware.anonymous_identity import (
    VISITOR_COOKIE_NAME,
    AnonymousIdentityMiddleware,
    visitor_key_hash,
)
from atlas.persistence.quota import (
    BudgetExceeded,
    GlobalDailyBudget,
    InMemoryQuotaRepository,
    QuotaExceeded,
    QuotaService,
)


def test_identity_cookie_is_opaque_secure_and_only_hmac_hash_is_exposed() -> None:
    application = FastAPI()
    application.add_middleware(AnonymousIdentityMiddleware, secret="visitor-secret")

    @application.get("/")
    def identity(request: Request) -> dict[str, str]:
        return {"visitor_key_hash": request.state.visitor_key_hash}

    response = TestClient(application).get("/")
    set_cookie = response.headers["set-cookie"]
    raw_cookie = response.cookies[VISITOR_COOKIE_NAME]

    assert raw_cookie
    assert len(raw_cookie) >= 32
    assert response.json()["visitor_key_hash"] == visitor_key_hash("visitor-secret", raw_cookie)
    assert raw_cookie not in response.json()["visitor_key_hash"]
    assert f"{VISITOR_COOKIE_NAME}={raw_cookie}" in set_cookie
    assert "HttpOnly" in set_cookie
    assert "Secure" in set_cookie
    assert "SameSite=lax" in set_cookie


def test_existing_cookie_keeps_the_same_hmac_identity_without_setting_a_new_cookie() -> None:
    application = FastAPI()
    application.add_middleware(AnonymousIdentityMiddleware, secret="visitor-secret")
    application.get("/")(lambda request: {"visitor_key_hash": request.state.visitor_key_hash})
    client = TestClient(application)
    first = client.get("/")
    raw_cookie = first.cookies[VISITOR_COOKIE_NAME]

    second = client.get("/", cookies={VISITOR_COOKIE_NAME: raw_cookie})

    assert second.json() == first.json()
    assert "set-cookie" not in second.headers


def test_quota_is_idempotent_and_returns_the_earliest_retry_time() -> None:
    now = datetime(2026, 8, 4, 12, tzinfo=UTC)
    repository = InMemoryQuotaRepository(limit=10, window=timedelta(hours=24))
    quota = QuotaService(repository)
    visitor = "a" * 64
    first_run = uuid4()

    first = quota.reserve(visitor, "same-key", first_run, now=now)
    repeated = quota.reserve(visitor, "same-key", first_run, now=now + timedelta(minutes=1))
    for index in range(9):
        quota.reserve(visitor, f"key-{index}", uuid4(), now=now)

    try:
        quota.reserve(visitor, "eleventh", uuid4(), now=now + timedelta(hours=1))
    except QuotaExceeded as exc:
        denied = exc
    else:
        raise AssertionError("the eleventh reservation should be rejected")

    assert first.remaining == 9
    assert repeated.run_id == first.run_id
    assert repeated.remaining == 9
    assert denied.retry_at == now + timedelta(hours=24)
    assert denied.retry_after_seconds(now=now + timedelta(hours=1)) == 23 * 60 * 60
    assert repository.accepted_count(visitor, now + timedelta(hours=1)) == 10


def test_concurrent_reservations_never_exceed_the_rolling_limit() -> None:
    repository = InMemoryQuotaRepository(limit=10, window=timedelta(hours=24))
    quota = QuotaService(repository)
    visitor = "b" * 64
    now = datetime.now(UTC)

    def reserve(index: int):
        try:
            return quota.reserve(visitor, f"concurrent-{index}", uuid4(), now=now)
        except QuotaExceeded:
            return None

    with ThreadPoolExecutor(max_workers=20) as executor:
        results = list(executor.map(reserve, range(20)))

    assert sum(result is not None for result in results) == 10
    assert repository.accepted_count(visitor, now) == 10


def test_global_daily_budget_rejects_costly_work_until_the_next_day() -> None:
    budget = GlobalDailyBudget(limit_usd=Decimal("0.010000"))
    observed_at = datetime(2026, 8, 4, 23, 59, tzinfo=UTC)

    budget.reserve(Decimal("0.006000"), observed_at=observed_at)
    try:
        budget.reserve(Decimal("0.005000"), observed_at=observed_at)
    except BudgetExceeded:
        pass
    else:
        raise AssertionError("the daily budget should reject the second reservation")

    budget.reserve(Decimal("0.005000"), observed_at=observed_at + timedelta(days=1))


def test_budget_rejection_does_not_consume_anonymous_quota() -> None:
    now = datetime(2026, 8, 4, 12, tzinfo=UTC)
    repository = InMemoryQuotaRepository(limit=10, window=timedelta(hours=24))
    budget = GlobalDailyBudget(limit_usd=Decimal("0.010000"))
    quota = QuotaService(repository, global_budget=budget)
    visitor = "c" * 64

    quota.reserve(visitor, "budget-1", uuid4(), now=now, estimated_cost_usd=Decimal("0.006"))
    try:
        quota.reserve(visitor, "budget-2", uuid4(), now=now, estimated_cost_usd=Decimal("0.005"))
    except BudgetExceeded:
        pass
    else:
        raise AssertionError("the global budget should reject the second reservation")

    assert repository.accepted_count(visitor, now) == 1
