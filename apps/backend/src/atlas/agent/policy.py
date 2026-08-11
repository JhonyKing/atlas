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
    idempotency_key: str | None = None,
) -> Approval:
    current = now or datetime.now(UTC)
    digest = arguments_hash(arguments)
    expires = min(plan.expires_at, current + timedelta(seconds=ttl_seconds))
    decision_key = _approval_decision_key(
        run_id=plan.run_id,
        call_id=call_id,
        actor_id=actor_id,
        tool_id=tool_id,
        tool_version=tool_version,
        arguments_hash_value=digest,
        target_resource=target_resource or target_from_arguments(arguments),
        idempotency_key=idempotency_key,
    )
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
    idempotency_key: str | None = None,
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
    if idempotency_key is not None:
        assert_approval_idempotency_key(approval, idempotency_key)


def assert_approval_idempotency_key(approval: Approval, idempotency_key: str) -> None:
    """Require the same operation key that was bound when the approval was issued."""

    expected = _approval_decision_key(
        run_id=approval.run_id,
        call_id=approval.call_id,
        actor_id=approval.actor_id,
        tool_id=approval.tool_id,
        tool_version=approval.tool_version,
        arguments_hash_value=approval.arguments_hash,
        target_resource=approval.target_resource,
        idempotency_key=idempotency_key,
    )
    if approval.decision_key != expected:
        raise PolicyError("approval idempotency key mismatch")


def _approval_decision_key(
    *,
    run_id: UUID,
    call_id: str,
    actor_id: str,
    tool_id: str,
    tool_version: str,
    arguments_hash_value: str,
    target_resource: str,
    idempotency_key: str | None,
) -> str:
    payload = {
        "run_id": str(run_id),
        "call_id": call_id,
        "actor_id": actor_id,
        "tool_id": tool_id,
        "tool_version": tool_version,
        "arguments_hash": arguments_hash_value,
        "target": target_resource,
    }
    if idempotency_key is not None:
        payload["idempotency_key"] = idempotency_key
    return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
