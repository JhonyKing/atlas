"""Fail-closed authorization and approval contracts for tool calls."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Literal
from uuid import UUID, uuid4

from atlas.agent.planning import AgentPlan, arguments_hash, normalized_arguments
from atlas.agent.tools.registry import ToolCatalog

Decision = Literal["approved", "rejected", "expired"]


@dataclass(frozen=True, slots=True)
class Approval:
    approval_id: UUID
    run_id: UUID
    call_id: str
    actor_id: str
    tool_id: str
    tool_version: str
    arguments_hash: str
    target_resource: str
    decision: Decision
    decision_key: str
    expires_at: datetime


class PolicyError(ValueError):
    """Raised when a call is not authorized."""


def target_from_arguments(arguments: dict[str, object]) -> str:
    candidate = (
        arguments.get("resource_id")
        or arguments.get("target")
        or arguments.get("collection")
    )
    return str(candidate)[:200] if candidate is not None else "none"


def evaluate_plan_policy(
    plan: AgentPlan,
    *,
    catalog: ToolCatalog,
    actor_id: str,
    scopes: set[str],
    consent: bool = False,
) -> tuple[str, ...]:
    """Return redacted policy reasons; an empty tuple means the plan may proceed."""

    if not actor_id.strip():
        return ("actor_missing",)
    reasons: list[str] = []
    for step in plan.steps:
        tool = catalog.get(step.tool_id)
        if tool is None:
            reasons.append("tool_unknown")
            continue
        if tool.scopes and not set(tool.scopes).issubset(scopes):
            reasons.append(f"scope_missing:{tool.tool_id}")
        if tool.side_effect_level != "read" and not consent:
            reasons.append(f"consent_required:{tool.tool_id}")
    return tuple(reasons)


def issue_approval(
    plan: AgentPlan,
    *,
    call_id: str,
    actor_id: str,
    tool_id: str,
    tool_version: str,
    arguments: dict[str, object],
    target_resource: str | None = None,
    ttl_seconds: int = 600,
    now: datetime | None = None,
    decision: Decision = "rejected",
) -> Approval:
    current = now or datetime.now(UTC)
    digest = arguments_hash(arguments)
    expires = min(plan.expires_at, current + timedelta(seconds=ttl_seconds))
    decision_key = hashlib.sha256(
        json.dumps(
            {
                "run_id": str(plan.run_id),
                "call_id": call_id,
                "actor_id": actor_id,
                "tool_id": tool_id,
                "tool_version": tool_version,
                "arguments_hash": digest,
                "target": target_resource or target_from_arguments(arguments),
            },
            sort_keys=True,
        ).encode()
    ).hexdigest()
    return Approval(
        approval_id=uuid4(),
        run_id=plan.run_id,
        call_id=call_id,
        actor_id=actor_id,
        tool_id=tool_id,
        tool_version=tool_version,
        arguments_hash=digest,
        target_resource=target_resource or target_from_arguments(arguments),
        decision=decision,
        decision_key=decision_key,
        expires_at=expires,
    )


def assert_approval_matches(
    approval: Approval,
    *,
    plan: AgentPlan,
    actor_id: str,
    tool_id: str,
    tool_version: str,
    arguments: dict[str, object],
    now: datetime | None = None,
) -> None:
    current = now or datetime.now(UTC)
    if approval.decision != "approved":
        raise PolicyError("approval is not approved")
    if approval.expires_at <= current or approval.expires_at > plan.expires_at:
        raise PolicyError("approval is expired")
    if (
        approval.run_id != plan.run_id
        or approval.actor_id != actor_id
        or approval.tool_id != tool_id
        or approval.tool_version != tool_version
    ):
        raise PolicyError("approval actor, tool, or plan mismatch")
    if approval.arguments_hash != arguments_hash(normalized_arguments(arguments)):
        raise PolicyError("approval arguments mismatch")
    if approval.target_resource != target_from_arguments(arguments):
        raise PolicyError("approval target mismatch")
