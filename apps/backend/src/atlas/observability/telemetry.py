"""OpenTelemetry helpers that deliberately exclude user and source content."""

from __future__ import annotations

from collections.abc import Iterator, Mapping
from contextlib import contextmanager
from typing import Any
from uuid import UUID

from opentelemetry.trace import Span, Tracer

_SENSITIVE_FIELD_PARTS = (
    "question",
    "prompt",
    "evidence",
    "excerpt",
    "content",
    "cookie",
    "authorization",
    "secret",
    "raw",
)
_SAFE_METADATA_FIELDS = frozenset({"prompt_version"})


def span_attributes(
    *,
    request_id: UUID,
    operation: str,
    fields: Mapping[str, Any] | None = None,
) -> dict[str, str | int | float | bool]:
    """Return bounded scalar attributes with sensitive content omitted."""

    attributes: dict[str, str | int | float | bool] = {
        "atlas.request_id": str(request_id),
        "atlas.operation": operation,
    }
    for key, value in (fields or {}).items():
        normalized = key.lower()
        if normalized not in _SAFE_METADATA_FIELDS and any(
            part in normalized for part in _SENSITIVE_FIELD_PARTS
        ):
            continue
        if isinstance(value, (str, int, float, bool)):
            attributes[f"atlas.{normalized}"] = value
    return attributes


@contextmanager
def observed_span(
    tracer: Tracer,
    operation: str,
    *,
    request_id: UUID,
    fields: Mapping[str, Any] | None = None,
) -> Iterator[Span]:
    """Create a span containing only request correlation and safe scalar metrics."""

    with tracer.start_as_current_span(operation) as span:
        for key, value in span_attributes(
            request_id=request_id,
            operation=operation,
            fields=fields,
        ).items():
            span.set_attribute(key, value)
        yield span
