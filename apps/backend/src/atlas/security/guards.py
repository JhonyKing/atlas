"""Treat retrieved/source content as inert data and reject unsafe actions."""

from __future__ import annotations

import re


class SecurityViolation(ValueError):
    """Untrusted input attempted to cross a security boundary."""


_INJECTION_PATTERNS = (
    re.compile(r"ignore\s+(?:all|previous)\s+instructions", re.IGNORECASE),
    re.compile(r"(?:execute|run)\s+(?:shell|python|javascript|code)", re.IGNORECASE),
    re.compile(r"call\s+(?:the\s+)?[a-z0-9_.-]+\s+tool", re.IGNORECASE),
)


def sanitize_source_text(text: str, *, max_length: int = 12_000) -> str:
    """Return bounded source text; injection-like instructions remain inert markers."""

    if max_length < 1:
        raise ValueError("max_length must be positive")
    bounded = text[:max_length]
    for pattern in _INJECTION_PATTERNS:
        bounded = pattern.sub("[UNTRUSTED_INSTRUCTION_REMOVED]", bounded)
    return bounded


def assert_safe_action(action: str, *, allowed_actions: frozenset[str]) -> None:
    """Allow only server-selected action names; source text cannot invent a tool call."""

    if action not in allowed_actions:
        raise SecurityViolation("action is not allowlisted")
