"""Approval-gated boundaries for private and consequential tools."""

from __future__ import annotations

import inspect
from collections.abc import Awaitable, Callable, Mapping
from typing import Final

from atlas.agent.planning import AgentPlan
from atlas.agent.policy import Approval, PolicyError, assert_approval_matches
from atlas.agent.tools.read_only import bounded_result, normalize_result
from atlas.agent.tools.registry import ToolCatalog

SIDE_EFFECT_TOOL_IDS: Final[frozenset[str]] = frozenset(
    {"private_resources", "private_upload", "private_delete", "human_review"}
)
MAX_REFERENCES: Final[int] = 64
MAX_REFERENCE_LENGTH: Final[int] = 256

SideEffectHandler = Callable[[dict[str, object]], Awaitable[Mapping[str, object]]]
OwnerCheck = Callable[[str, Mapping[str, object]], bool | Awaitable[bool]]


def requires_explicit_approval(tool_id: str) -> bool:
    return tool_id in SIDE_EFFECT_TOOL_IDS


class SideEffectToolAdapters:
    """Approval and ownership gate for private and consequential tool handlers."""

    def __init__(
        self,
        catalog: ToolCatalog,
        handlers: Mapping[str, SideEffectHandler],
        *,
        owner_check: OwnerCheck | None = None,
    ) -> None:
        invalid = set(handlers) - SIDE_EFFECT_TOOL_IDS
        if invalid:
            raise ValueError(
                "side-effect adapters may only register catalog tools: "
                + ", ".join(sorted(invalid))
            )
        self._catalog = catalog
        self._handlers = dict(handlers)
        self._owner_check = owner_check

    async def execute(
        self,
        tool_id: str,
        arguments: Mapping[str, object],
        *,
        plan: AgentPlan,
        actor_id: str,
        approval: Approval | None = None,
        consent: bool | None = None,
    ) -> dict[str, object]:
        definition = self._catalog.get(tool_id)
        if definition is None or not requires_explicit_approval(tool_id):
            raise ValueError(f"tool is not a registered side-effect: {tool_id}")
        if not actor_id.strip():
            return _rejected("actor_missing")
        if approval is None:
            return abstained_result_with_reason("approval_required")
        if consent is False:
            return _rejected("consent_required")
        try:
            assert_approval_matches(
                approval,
                plan=plan,
                actor_id=actor_id,
                tool_id=tool_id,
                tool_version=definition.version,
                arguments=dict(arguments),
            )
        except PolicyError:
            return _rejected("approval_mismatch")
        if definition.scopes and actor_id == "anonymous":
            return _rejected("authentication_required")
        if tool_id.startswith("private_"):
            if self._owner_check is None:
                return _rejected("ownership_unavailable")
            owned = self._owner_check(actor_id, arguments)
            if inspect.isawaitable(owned):
                owned = await owned
            if not owned:
                return _rejected("ownership_denied")
        handler = self._handlers.get(tool_id)
        if handler is None:
            return abstained_result_with_reason("adapter_unavailable")
        try:
            raw = await handler(dict(arguments))
        except Exception:
            return _rejected("side_effect_failed")
        return _normalize_result(raw)


def abstained_result(tool_id: str) -> dict[str, object]:
    """Return a non-executing result when a side effect has no approved handler."""

    return {
        "status": "abstained",
        "reason": "side_effect_requires_approval",
        "tool_id": tool_id,
        "evidence_ids": (),
        "artifact_ids": (),
    }


def abstained_result_with_reason(reason: str) -> dict[str, object]:
    return bounded_result(status="abstained", reason=reason)


def _rejected(reason: str) -> dict[str, object]:
    return bounded_result(status="rejected", reason=reason)


def _normalize_result(raw: Mapping[str, object]) -> dict[str, object]:
    """Use the same bounded evidence envelope as read-only tool results."""

    return normalize_result(raw)
