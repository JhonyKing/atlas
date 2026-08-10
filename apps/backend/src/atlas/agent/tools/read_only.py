"""Allowlisted read-only adapter boundaries for existing ATLAS domain services."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, Mapping, Sequence
from typing import Final, Literal

ReadOnlyToolId = Literal["cited_answer", "comparison", "report", "daily_news", "corpus_status"]
READ_ONLY_TOOL_IDS: Final[frozenset[str]] = frozenset(
    {"cited_answer", "comparison", "report", "daily_news", "corpus_status"}
)
MAX_REFERENCES: Final[int] = 64
MAX_REFERENCE_LENGTH: Final[int] = 256
MAX_METADATA_ITEMS: Final[int] = 64
MAX_EXCERPT_LENGTH: Final[int] = 1200
SAFE_SCALAR_KEYS: Final[frozenset[str]] = frozenset(
    {
        "claim_count",
        "source_count",
        "verification_status",
        "relation",
        "latency_ms",
        "cost_usd",
        "model_label",
        "corpus_snapshot",
        "mode",
    }
)

ReadOnlyHandler = Callable[[dict[str, object]], Awaitable[Mapping[str, object]]]


def is_read_only_tool(tool_id: str) -> bool:
    """Keep domain delegation constrained to the versioned read-only allowlist."""

    return tool_id in READ_ONLY_TOOL_IDS


def _bounded_ids(value: object) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple, set)):
        return ()
    return tuple(str(item)[:MAX_REFERENCE_LENGTH] for item in tuple(value)[:MAX_REFERENCES])


def _bounded_text(value: object, *, limit: int = MAX_REFERENCE_LENGTH) -> str | None:
    if value is None:
        return None
    return str(value)[:limit]


def _bounded_provenance(value: object) -> dict[str, str]:
    if not isinstance(value, Mapping):
        return {}
    return {
        str(key)[:MAX_REFERENCE_LENGTH]: str(item)[:MAX_REFERENCE_LENGTH]
        for key, item in list(value.items())[:MAX_METADATA_ITEMS]
        if item is not None
    }


def _bounded_excerpts(value: object) -> tuple[dict[str, str], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    allowed = {"evidence_id", "excerpt", "canonical_url", "source_version", "captured_at"}
    records: list[dict[str, str]] = []
    for item in list(value)[:MAX_REFERENCES]:
        if not isinstance(item, Mapping):
            continue
        record = {
            str(key): str(raw)[:MAX_EXCERPT_LENGTH if key == "excerpt" else MAX_REFERENCE_LENGTH]
            for key, raw in item.items()
            if key in allowed and raw is not None
        }
        if record:
            records.append(record)
    return tuple(records)


def _bounded_relations(value: object) -> tuple[dict[str, str], ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return ()
    allowed = {"from_evidence_id", "to_evidence_id", "relation"}
    records: list[dict[str, str]] = []
    for item in list(value)[:MAX_REFERENCES]:
        if not isinstance(item, Mapping):
            continue
        record = {
            str(key): str(raw)[:MAX_REFERENCE_LENGTH]
            for key, raw in item.items()
            if key in allowed and raw is not None
        }
        if record:
            records.append(record)
    return tuple(records)


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
    """Preserve known typed result fields while bounding provenance and references."""

    status = str(raw.get("status", "abstained"))[:64]
    result = bounded_result(
        status=status,
        evidence_ids=_bounded_ids(raw.get("evidence_ids", ())),
        artifact_ids=_bounded_ids(raw.get("artifact_ids", ())),
        reason=str(raw["reason"])[:256] if raw.get("reason") is not None else None,
    )
    provenance = _bounded_provenance(raw.get("provenance"))
    excerpts = _bounded_excerpts(raw.get("excerpts"))
    relations = _bounded_relations(raw.get("evidence_relations"))
    if provenance:
        result["provenance"] = provenance
    if excerpts:
        result["excerpts"] = excerpts
    if relations:
        result["evidence_relations"] = relations
    source_versions = _bounded_ids(raw.get("source_versions", ()))
    if source_versions:
        result["source_versions"] = source_versions
    for key in SAFE_SCALAR_KEYS:
        if key in raw and raw[key] is not None:
            value = raw[key]
            if isinstance(value, (str, int, float, bool)):
                result[key] = _bounded_text(value) if isinstance(value, str) else value
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
