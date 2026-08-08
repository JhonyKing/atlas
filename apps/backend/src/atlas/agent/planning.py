"""Validated finite plans for the ATLAS agent."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime, timedelta
from typing import cast
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import Locale, ToolCallRequest, validate_json_object


class PlanValidationError(ValueError):
    """Raised when an untrusted proposed plan is not executable."""


class AgentPlan(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    run_id: UUID = Field(default_factory=uuid4)
    model_label: str = "gpt-5.6-luna"
    request: str = Field(min_length=1, max_length=4000)
    locale: Locale = "en-US"
    steps: tuple[ToolCallRequest, ...] = Field(min_length=1, max_length=8)
    risk_summary: tuple[str, ...] = ()
    budget: dict[str, int] = Field(default_factory=lambda: {"max_calls": 8, "max_evidence": 32})
    expires_at: datetime
    plan_hash: str = Field(pattern=r"^[0-9a-f]{64}$")


def normalized_arguments(arguments: dict[str, object]) -> dict[str, object]:
    """Normalize an argument object before hashing or policy evaluation."""

    return cast(
        dict[str, object],
        json.loads(json.dumps(arguments, sort_keys=True, separators=(",", ":"))),
    )


def arguments_hash(arguments: dict[str, object]) -> str:
    payload = json.dumps(normalized_arguments(arguments), sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode()).hexdigest()


def compute_plan_hash(
    request: str,
    locale: Locale,
    steps: tuple[ToolCallRequest, ...],
    expires_at: datetime,
    model_label: str = "gpt-5.6-luna",
) -> str:
    payload = {
        "request": request.strip(),
        "locale": locale,
        "model_label": model_label,
        "steps": [step.model_dump(mode="json") for step in steps],
        "expires_at": expires_at.isoformat(),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _assert_acyclic(steps: tuple[ToolCallRequest, ...]) -> None:
    ids = {f"step-{index}" for index in range(len(steps))}
    graph = {f"step-{index}": set(step.dependencies) for index, step in enumerate(steps)}
    if any(dependency not in ids for dependencies in graph.values() for dependency in dependencies):
        raise PlanValidationError("plan dependency references an unknown step")
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str) -> None:
        if node in visiting:
            raise PlanValidationError("plan dependency cycle detected")
        if node in visited:
            return
        visiting.add(node)
        for dependency in graph[node]:
            visit(dependency)
        visiting.remove(node)
        visited.add(node)

    for node in ids:
        visit(node)


def validate_plan(
    *,
    catalog: ToolCatalog,
    request: str,
    locale: Locale,
    steps: tuple[ToolCallRequest, ...],
    now: datetime | None = None,
    ttl_seconds: int = 900,
    model_label: str = "gpt-5.6-luna",
) -> AgentPlan:
    """Validate tool IDs, arguments, availability, dependencies, and budgets."""

    if not request.strip():
        raise PlanValidationError("request must not be empty")
    if not steps or len(steps) > 8:
        raise PlanValidationError("plan must contain between one and eight steps")
    _assert_acyclic(steps)
    total_calls = len(steps)
    total_evidence = 0
    risk: list[str] = []
    for step in steps:
        definition = catalog.get(step.tool_id)
        if definition is None:
            raise PlanValidationError(f"unknown tool: {step.tool_id}")
        if definition.version != step.tool_version:
            raise PlanValidationError(f"tool version mismatch: {step.tool_id}")
        if definition.availability != "enabled":
            raise PlanValidationError(f"tool unavailable: {step.tool_id}")
        if definition.timeout_ms <= 0:
            raise PlanValidationError(f"tool timeout invalid: {step.tool_id}")
        try:
            validate_json_object(step.arguments, definition.input_schema)
        except ValueError as exc:
            raise PlanValidationError(str(exc)) from exc
        total_evidence += definition.budget.get("max_evidence", 0)
        if definition.approval != "none":
            risk.append(f"approval:{step.tool_id}")
    if total_calls > 8:
        raise PlanValidationError("plan call budget exceeded")
    if total_evidence > 64:
        raise PlanValidationError("plan evidence budget exceeded")
    current = now or datetime.now(UTC)
    expires_at = current + timedelta(seconds=ttl_seconds)
    digest = compute_plan_hash(request, locale, steps, expires_at, model_label)
    return AgentPlan(
        request=request.strip(),
        model_label=model_label,
        locale=locale,
        steps=steps,
        risk_summary=tuple(risk),
        budget={"max_calls": total_calls, "max_evidence": total_evidence},
        expires_at=expires_at,
        plan_hash=digest,
    )


def proposal_for_request(request: str, *, locale: Locale = "en-US") -> tuple[ToolCallRequest, ...]:
    """Deterministic proposal used when the provider is unavailable.

    A real model may propose the same typed objects through the provider adapter, but this
    fallback never treats model text as authorization.
    """

    lowered = request.casefold()
    if any(word in lowered for word in ("compare", "comparison", "compara", "versus")):
        return (ToolCallRequest(tool_id="comparison", tool_version="1.0.0"),)
    if any(word in lowered for word in ("report", "reporte", "pdf", "document")):
        return (ToolCallRequest(tool_id="report", tool_version="1.0.0"),)
    if any(word in lowered for word in ("news", "noticia", "headline", "titular")):
        return (ToolCallRequest(tool_id="daily_news", tool_version="1.0.0"),)
    del locale
    return (
        ToolCallRequest(
            tool_id="cited_answer", tool_version="1.0.0", arguments={"question": request.strip()}
        ),
    )
