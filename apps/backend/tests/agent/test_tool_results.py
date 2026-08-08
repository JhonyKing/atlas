from atlas.agent.executor import BoundedExecutor
from atlas.agent.planning import validate_plan
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolCallRequest


def test_tool_result_preserves_evidence_and_artifact_ids() -> None:
    catalog = ToolCatalog.default()
    plan = validate_plan(
        catalog=catalog,
        request="What is the answer?",
        locale="en-US",
        steps=(
            ToolCallRequest(
                tool_id="cited_answer",
                tool_version="1.0.0",
                arguments={"question": "What is the answer?"},
            ),
        ),
    )
    executor = BoundedExecutor(catalog)
    executor.register(
        "cited_answer",
        lambda _args: {
            "status": "completed",
            "evidence_ids": ["ev-1"],
            "artifact_ids": ["answer-1"],
            "claim_count": 1,
        },
    )
    result = executor.execute(plan)
    assert result[0].evidence_ids == ("ev-1",)
    assert result[0].artifact_ids == ("answer-1",)
