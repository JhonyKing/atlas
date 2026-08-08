"""Approval-gated boundaries for private and consequential tools."""

from __future__ import annotations

from typing import Final

SIDE_EFFECT_TOOL_IDS: Final[frozenset[str]] = frozenset(
    {"private_resources", "private_upload", "private_delete", "human_review"}
)


def requires_explicit_approval(tool_id: str) -> bool:
    return tool_id in SIDE_EFFECT_TOOL_IDS


def abstained_result(tool_id: str) -> dict[str, object]:
    """Return a non-executing result when a side effect has no approved handler."""

    return {
        "status": "abstained",
        "reason": "side_effect_requires_approval",
        "tool_id": tool_id,
        "evidence_ids": (),
        "artifact_ids": (),
    }
