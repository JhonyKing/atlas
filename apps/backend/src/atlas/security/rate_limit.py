"""Simple provider-independent sliding-window abuse boundary."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from time import monotonic


@dataclass(frozen=True, slots=True)
class RateLimitDecision:
    allowed: bool
    remaining: int
    challenge: bool = False


@dataclass(slots=True)
class SlidingWindowLimiter:
    limit: int
    window_seconds: float = 60.0
    challenge_after: int | None = None
    _events: dict[str, deque[float]] = field(default_factory=dict)

    def check(self, identity: str, *, now: float | None = None) -> RateLimitDecision:
        if self.limit < 1 or self.window_seconds <= 0:
            raise ValueError("invalid rate-limit policy")
        timestamp = monotonic() if now is None else now
        events = self._events.setdefault(identity, deque())
        while events and timestamp - events[0] >= self.window_seconds:
            events.popleft()
        challenge = self.challenge_after is not None and len(events) >= self.challenge_after
        if len(events) >= self.limit:
            return RateLimitDecision(False, 0, challenge)
        events.append(timestamp)
        return RateLimitDecision(True, self.limit - len(events), challenge)
