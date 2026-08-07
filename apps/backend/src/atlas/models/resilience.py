"""Bounded provider resilience without provider SDK dependencies."""

from __future__ import annotations

import asyncio
import random
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from time import monotonic
from typing import TypeVar

T = TypeVar("T")


class ProviderUnavailable(RuntimeError):
    """A provider cannot serve the request within the configured policy."""


@dataclass(slots=True)
class CircuitBreaker:
    failure_limit: int = 3
    reset_after_seconds: float = 30.0
    failures: int = 0
    opened_at: float | None = None

    @property
    def is_open(self) -> bool:
        return (
            self.opened_at is not None
            and monotonic() - self.opened_at < self.reset_after_seconds
        )

    def record_success(self) -> None:
        self.failures = 0
        self.opened_at = None

    def record_failure(self) -> None:
        self.failures += 1
        if self.failures >= self.failure_limit:
            self.opened_at = monotonic()


async def retry_async[T](
    operation: Callable[[], Awaitable[T]],
    *,
    attempts: int = 3,
    timeout_seconds: float = 15.0,
    breaker: CircuitBreaker | None = None,
) -> T:
    if attempts < 1 or timeout_seconds <= 0:
        raise ValueError("attempts and timeout_seconds must be positive")
    if breaker and breaker.is_open:
        raise ProviderUnavailable("provider circuit is open")
    for attempt in range(attempts):
        try:
            result = await asyncio.wait_for(operation(), timeout=timeout_seconds)
        except (TimeoutError, OSError) as exc:
            if breaker:
                breaker.record_failure()
            if attempt == attempts - 1:
                raise ProviderUnavailable("provider attempts exhausted") from exc
            await asyncio.sleep(random.uniform(0.0, min(1.0, 0.1 * (2**attempt))))
        else:
            if breaker:
                breaker.record_success()
            return result
    raise ProviderUnavailable("provider attempts exhausted")
