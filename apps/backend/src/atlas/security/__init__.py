"""Provider-independent security guardrails for untrusted content and actions."""

from atlas.security.guards import SecurityViolation, assert_safe_action, sanitize_source_text
from atlas.security.rate_limit import RateLimitDecision, SlidingWindowLimiter

__all__ = [
    "RateLimitDecision",
    "SecurityViolation",
    "SlidingWindowLimiter",
    "assert_safe_action",
    "sanitize_source_text",
]
