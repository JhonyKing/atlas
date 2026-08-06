"""Content-free redaction for logs, traces, and audit metadata."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

REDACTED = "[REDACTED]"
_SENSITIVE_PARTS = (
    "authorization",
    "cookie",
    "password",
    "private",
    "prompt",
    "raw",
    "secret",
    "session",
    "token",
    "visitor",
)


def redact_secret(value: str | None) -> str:
    """Replace a secret entirely; never preserve a prefix that can aid replay."""

    return REDACTED


def redact_mapping(value: Mapping[str, Any]) -> dict[str, Any]:
    """Recursively redact fields whose names indicate credentials or private content."""

    result: dict[str, Any] = {}
    for key, item in value.items():
        normalized = key.casefold()
        if any(part in normalized for part in _SENSITIVE_PARTS):
            result[key] = REDACTED
        elif isinstance(item, Mapping):
            result[key] = redact_mapping(item)
        elif isinstance(item, list):
            result[key] = [
                redact_mapping(entry) if isinstance(entry, Mapping) else entry for entry in item
            ]
        else:
            result[key] = item
    return result
