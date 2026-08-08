"""Allowlisted read-only adapter boundaries for existing ATLAS domain services."""

from __future__ import annotations

from typing import Final, Literal

ReadOnlyToolId = Literal["cited_answer", "comparison", "report", "daily_news", "corpus_status"]
READ_ONLY_TOOL_IDS: Final[frozenset[str]] = frozenset(
    {"cited_answer", "comparison", "report", "daily_news", "corpus_status"}
)


def is_read_only_tool(tool_id: str) -> bool:
    """Keep domain delegation constrained to the versioned read-only allowlist."""

    return tool_id in READ_ONLY_TOOL_IDS


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
