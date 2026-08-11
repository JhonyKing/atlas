"""Safe LangSmith/OpenTelemetry fields for agent orchestration runs."""

from __future__ import annotations

from typing import Final

from atlas.agent.planning import AgentPlan

MAX_TAGS: Final[int] = 8


def agent_trace_tags(plan: AgentPlan) -> tuple[str, ...]:
    """Return bounded, non-content tags suitable for a trace backend."""

    tags = [
        "atlas.agent",
        f"locale:{plan.locale}",
        f"tool_count:{len(plan.steps)}",
        *(f"tool:{step.tool_id}:{step.tool_version}" for step in plan.steps),
    ]
    return tuple(tags[:MAX_TAGS])


def agent_trace_fields(plan: AgentPlan) -> dict[str, object]:
    """Return metrics and identifiers without question text or tool arguments."""

    return {
        "plan_hash": plan.plan_hash,
        "run_id": str(plan.run_id),
        "model": plan.model_label,
        "locale": plan.locale,
        "corpus": "configured",
        "tokens": "not_reported",
        "cost_usd": "not_reported",
        "latency_ms": "measured_on_completion",
        "budget_max_calls": plan.budget.get("max_calls", 0),
        "budget_max_evidence": plan.budget.get("max_evidence", 0),
        "approval_required": any(step.tool_id.startswith("private_") for step in plan.steps),
    }
