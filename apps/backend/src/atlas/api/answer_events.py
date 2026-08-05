"""Safe SSE event serialization for cited-answer runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

_TERMINAL_EVENTS = frozenset(
    {"answer.completed", "answer.abstained", "answer.cancelled", "answer.failed"}
)
_FORBIDDEN_PROGRESS_KEYS = frozenset(
    {"claim", "claims", "citation", "citations", "excerpt", "source_url", "canonical_url", "draft"}
)


@dataclass(slots=True)
class SSEEventWriter:
    """Serialize monotonically sequenced events without logging or exposing content."""

    sequence: int = 0

    def emit(self, event: str, data: dict[str, Any]) -> str:
        self.sequence += 1
        _validate_payload(event, data)
        encoded = json.dumps(data, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        return f"id: {self.sequence}\nevent: {event}\ndata: {encoded}\n\n"


def _validate_payload(event: str, data: dict[str, Any]) -> None:
    if event in _TERMINAL_EVENTS:
        return
    forbidden = _FORBIDDEN_PROGRESS_KEYS.intersection(data)
    if forbidden:
        names = ", ".join(sorted(forbidden))
        raise ValueError(f"progress event contains forbidden content fields: {names}")
