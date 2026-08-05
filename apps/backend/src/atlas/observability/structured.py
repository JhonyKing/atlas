"""Structured logs with a content-free field allowlist."""

from __future__ import annotations

import json
import logging
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from atlas.observability.telemetry import span_attributes


def log_event(
    logger: logging.Logger,
    event: str,
    *,
    request_id: UUID,
    fields: Mapping[str, Any] | None = None,
    level: int = logging.INFO,
) -> None:
    """Write one JSON event containing request ID and safe scalar diagnostics only."""

    payload = span_attributes(request_id=request_id, operation=event, fields=fields)
    logger.log(level, json.dumps(payload, sort_keys=True, separators=(",", ":")))
