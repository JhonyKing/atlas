"""Allowlisted read-only adapter boundaries for existing ATLAS domain services."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping
from typing import Final, Literal

ReadOnlyToolId = Literal["cited_answer", "comparison", "report", "daily_news", "corpus_status"]
READ_ONLY_TOOL_IDS: Final[frozenset[str]] = frozenset(
    {"cited_answer", "comparison", "report", "daily_news", "corpus_status"}
)
MAX_REFERENCES: Final[int] = 64
MAX_REFERENCE_LENGTH: Final[int] = 256

ReadOnlyHandler = Callable[[dict[str, object]], Awaitable[Mapping[str, object]]]


def is_read_only_tool(tool_id: str) -> bool:
    """Keep domain delegation constrained to the versioned read-only allowlist."""

    return tool_id in READ_ONLY_TOOL_IDS


def _bounded_ids(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple, set)):
        return ()
    return tuple(str(item)[:MAX_REFERENCE_LENGTH] for item in tuple(value)[:MAX_REFERENCES])


class ReadOnlyToolAdapters:
    """Async adapter registry that delegates to existing domain service contracts."""

    def __init__(self, handlers: Mapping[str, ReadOnlyHandler]) -> None:
        invalid = set(handlers) - READ_ONLY_TOOL_IDS
        if invalid:
            raise ValueError(
                "read-only adapters may only register catalog tools: "
                + ", ".join(sorted(invalid))
            )
        self._handlers = dict(handlers)

    async def execute(self, tool_id: str, arguments: Mapping[str, object]) -> dict[str, object]:
        if not is_read_only_tool(tool_id):
            raise ValueError(f"tool is not read-only: {tool_id}")
        handler = self._handlers.get(tool_id)
        if handler is None:
            return bounded_result(status="abstained", reason="adapter_unavailable")
        try:
            raw = await handler(dict(arguments))
        except Exception:
            return bounded_result(status="failed", reason="adapter_failed")
        return _normalize_result(raw)


def _normalize_result(raw: Mapping[str, object]) -> dict[str, object]:
    """Preserve typed result fields while bounding evidence and artifact references."""

    status = str(raw.get("status", "abstained"))[:64]
    result = bounded_result(
        status=status,
        evidence_ids=_bounded_ids(raw.get("evidence_ids", ())),
        artifact_ids=_bounded_ids(raw.get("artifact_ids", ())),
        reason=str(raw["reason"])[:256] if raw.get("reason") is not None else None,
    )
    result.update(
        {
            str(key): value
            for key, value in raw.items()
            if key not in {"status", "evidence_ids", "artifact_ids", "reason"}
        }
    )
    return result


def bounded_result(
    *,
    status: str,
    evidence_ids: tuple[str, ...] = (),
    artifact_ids: tuple[str, ...] = (),
    reason: str | None = None,
) -> dict[str, object]:
    """Build the safe result envelope shared by read-only adapters."""

    result: dict[str, object] = {
        "status": status,
        "evidence_ids": evidence_ids,
        "artifact_ids": artifact_ids,
    }
    if reason is not None:
        result["reason"] = reason
    return result
