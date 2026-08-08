from datetime import UTC, datetime

import pytest

from atlas.agent.planning import PlanValidationError, validate_plan
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolCallRequest


def _validate(step: ToolCallRequest):
    return validate_plan(
        catalog=ToolCatalog.default(),
        request="How does LangGraph persist state?",
        locale="en-US",
        steps=(step,),
        now=datetime(2026, 8, 7, tzinfo=UTC),
    )


def test_explicit_selection_and_arguments_are_validated() -> None:
    plan = _validate(
        ToolCallRequest(
            tool_id="cited_answer", tool_version="1.0.0", arguments={"question": "How?"}
        )
    )
    assert len(plan.plan_hash) == 64


@pytest.mark.parametrize(
    "step, message",
    [
        (ToolCallRequest(tool_id="unknown_tool", tool_version="1.0.0"), "unknown tool"),
        (ToolCallRequest(tool_id="cited_answer", tool_version="1.0.0"), "missing"),
    ],
)
def test_invalid_tool_and_arguments_fail_closed(step: ToolCallRequest, message: str) -> None:
    with pytest.raises(PlanValidationError, match=message):
        _validate(step)


def test_dependency_cycle_is_rejected() -> None:
    steps = (
        ToolCallRequest(tool_id="daily_news", tool_version="1.0.0", dependencies=("step-1",)),
        ToolCallRequest(tool_id="corpus_status", tool_version="1.0.0", dependencies=("step-0",)),
    )
    with pytest.raises(PlanValidationError, match="cycle"):
        validate_plan(catalog=ToolCatalog.default(), request="status", locale="en-US", steps=steps)


def test_disabled_tool_and_budget_overflow_fail_closed() -> None:
    catalog = ToolCatalog.default()
    disabled = catalog.model_copy(
        update={
            "tools": tuple(
                tool.model_copy(update={"availability": "disabled"})
                if tool.tool_id == "daily_news"
                else tool
                for tool in catalog.tools
            )
        }
    )
    with pytest.raises(PlanValidationError, match="unavailable"):
        validate_plan(
            catalog=disabled,
            request="news",
            locale="en-US",
            steps=(ToolCallRequest(tool_id="daily_news", tool_version="1.0.0"),),
        )

    overflow = catalog.model_copy(
        update={
            "tools": tuple(
                tool.model_copy(update={"budget": {"max_calls": 1, "max_evidence": 65}})
                if tool.tool_id == "daily_news"
                else tool
                for tool in catalog.tools
            )
        }
    )
    with pytest.raises(PlanValidationError, match="evidence budget"):
        validate_plan(
            catalog=overflow,
            request="news",
            locale="en-US",
            steps=(ToolCallRequest(tool_id="daily_news", tool_version="1.0.0"),),
        )
