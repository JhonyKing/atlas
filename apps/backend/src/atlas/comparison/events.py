"""Safe SSE events for comparison progress and verified terminal matrices."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any
from uuid import UUID

_EVENT_ORDER = (
    "comparison.accepted",
    "comparison.retrieval.started",
    "comparison.retrieval.completed",
    "comparison.normalization.completed",
    "comparison.verification.completed",
    "comparison.completed",
)
_TERMINAL_EVENTS = frozenset(
    {"comparison.completed", "comparison.abstained", "comparison.cancelled", "comparison.failed"}
)
_FORBIDDEN_PROGRESS_KEYS = frozenset({"matrix", "cells", "evidence", "evidence_ids"})


class ComparisonEventOrderError(ValueError):
    """An event was emitted after the run had advanced or terminated."""


@dataclass(slots=True)
class ComparisonEventWriter:
    run_id: UUID
    sequence: int = 0
    _last_index: int = -1
    _terminal: bool = False

    def emit(self, event: str, data: dict[str, Any]) -> str:
        if event not in _EVENT_ORDER and event not in _TERMINAL_EVENTS:
            raise ValueError(f"unsupported comparison event: {event}")
        if self._terminal:
            raise ComparisonEventOrderError("comparison events cannot be emitted after termination")
        event_index = _EVENT_ORDER.index(event) if event in _EVENT_ORDER else len(_EVENT_ORDER)
        if event_index <= self._last_index:
            raise ComparisonEventOrderError("comparison events must advance monotonically")
        if event in _TERMINAL_EVENTS:
            _validate_terminal(event, data)
            self._terminal = True
        else:
            if _FORBIDDEN_PROGRESS_KEYS.intersection(data):
                raise ValueError("progress comparison events cannot contain matrix or evidence")
        self._last_index = event_index
        self.sequence += 1
        payload = {"run_id": str(self.run_id), **data}
        encoded = json.dumps(payload, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        return f"id: {self.sequence}\nevent: {event}\ndata: {encoded}\n\n"


def _validate_terminal(event: str, data: dict[str, Any]) -> None:
    if event != "comparison.completed":
        return
    matrix = data.get("matrix")
    if not isinstance(matrix, dict):
        raise ValueError("completed comparison requires a matrix")
    cells = matrix.get("cells")
    if not isinstance(cells, list):
        raise ValueError("completed comparison matrix requires cells")
    for cell in cells:
        if not isinstance(cell, dict):
            raise ValueError("comparison cells must be objects")
        if cell.get("state") == "supported" and not cell.get("evidence_ids"):
            raise ValueError("supported comparison cells require evidence")
