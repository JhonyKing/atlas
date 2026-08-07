import asyncio

import pytest

from atlas.models.resilience import CircuitBreaker, ProviderUnavailable, retry_async


@pytest.mark.asyncio
async def test_retry_is_bounded_and_opens_circuit_after_failures() -> None:
    breaker = CircuitBreaker(failure_limit=2)

    async def failing() -> str:
        raise TimeoutError("simulated")

    with pytest.raises(ProviderUnavailable):
        await retry_async(failing, attempts=2, timeout_seconds=0.01, breaker=breaker)
    assert breaker.is_open
    with pytest.raises(ProviderUnavailable, match="circuit"):
        await retry_async(failing, attempts=1, timeout_seconds=0.01, breaker=breaker)


@pytest.mark.asyncio
async def test_success_resets_circuit() -> None:
    breaker = CircuitBreaker()

    async def successful() -> str:
        await asyncio.sleep(0)
        return "ok"

    assert await retry_async(successful, breaker=breaker) == "ok"
    assert not breaker.is_open
