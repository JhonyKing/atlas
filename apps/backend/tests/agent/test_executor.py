from __future__ import annotations

import time

from atlas.agent.events import InMemoryEventStore
from atlas.agent.executor import BoundedExecutor
from atlas.agent.planning import validate_plan
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolCallRequest


def _plan(*steps: ToolCallRequest):
    return validate_plan(
        catalog=ToolCatalog.default(),
        request="How does LangGraph persist state?",
        locale="en-US",
        steps=steps,
    )


def test_executor_times_out_a_tool_and_keeps_failure_safe() -> None:
    catalog = ToolCatalog.default().model_copy(
        update={
            "tools": tuple(
                tool.model_copy(update={"timeout_ms": 1})
                if tool.tool_id == "cited_answer"
                else tool
                for tool in ToolCatalog.default().tools
            )
        }
    )
    plan = validate_plan(
        catalog=catalog,
        request="How does LangGraph persist state?",
        locale="en-US",
        steps=(
            ToolCallRequest(
                tool_id="cited_answer",
                tool_version="1.0.0",
                arguments={"question": "How does LangGraph persist state?"},
            ),
        ),
    )
    events = InMemoryEventStore()
    executor = BoundedExecutor(catalog, events=events)

    def slow_handler(_args: dict[str, object]) -> dict[str, object]:
        time.sleep(0.03)
        return {"status": "completed"}

    executor.register("cited_answer", slow_handler)
    result = executor.execute(plan)

    assert result[0].status == "failed"
    assert result[0].error_category == "timeout"
    assert events.list(plan.run_id)[-1].event_type == "run.failed"


def test_executor_rejects_runtime_evidence_budget_overflow() -> None:
    plan = _plan(
        ToolCallRequest(
            tool_id="cited_answer",
            tool_version="1.0.0",
            arguments={"question": "How does LangGraph persist state?"},
        )
    ).model_copy(update={"budget": {"max_calls": 1, "max_evidence": 1}})
    executor = BoundedExecutor(ToolCatalog.default())
    executor.register(
        "cited_answer",
        lambda _args: {"status": "completed", "evidence_ids": ["ev-1", "ev-2"]},
    )

    result = executor.execute(plan)

    assert result[0].status == "failed"
    assert result[0].error_category == "evidence_budget_exceeded"


def test_executor_cancels_before_next_tool_without_invoking_it() -> None:
    plan = _plan(
        ToolCallRequest(
            tool_id="cited_answer",
            tool_version="1.0.0",
            arguments={"question": "first"},
        ),
        ToolCallRequest(
            tool_id="cited_answer",
            tool_version="1.0.0",
            arguments={"question": "second"},
            dependencies=("step-0",),
        ),
    )
    executor = BoundedExecutor(ToolCatalog.default())
    calls = 0

    def handler(_args: dict[str, object]) -> dict[str, object]:
        nonlocal calls
        calls += 1
        return {"status": "completed"}

    executor.register("cited_answer", handler)

    def cancelled() -> bool:
        return calls == 1

    result = executor.execute(plan, cancelled=cancelled)

    assert calls == 1
    assert [item.status for item in result] == ["completed", "cancelled"]


def test_executor_returns_partial_results_and_stops_after_handler_failure() -> None:
    plan = _plan(
        ToolCallRequest(
            tool_id="cited_answer",
            tool_version="1.0.0",
            arguments={"question": "first"},
        ),
        ToolCallRequest(
            tool_id="cited_answer",
            tool_version="1.0.0",
            arguments={"question": "second"},
            dependencies=("step-0",),
        ),
        ToolCallRequest(
            tool_id="cited_answer",
            tool_version="1.0.0",
            arguments={"question": "third"},
            dependencies=("step-1",),
        ),
    )
    executor = BoundedExecutor(ToolCatalog.default())
    calls = 0

    def handler(_args: dict[str, object]) -> dict[str, object]:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise RuntimeError("provider unavailable")
        return {"status": "completed"}

    executor.register("cited_answer", handler)

    result = executor.execute(plan)

    assert calls == 2
    assert [item.status for item in result] == ["completed", "failed"]
    assert result[1].error_category == "RuntimeError"
