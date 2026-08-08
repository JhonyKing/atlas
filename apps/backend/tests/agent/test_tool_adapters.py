from atlas.agent.tools.read_only import bounded_result, is_read_only_tool
from atlas.agent.tools.side_effects import abstained_result, requires_explicit_approval


def test_read_only_adapter_boundary_is_allowlisted_and_bounded() -> None:
    assert is_read_only_tool("cited_answer")
    assert is_read_only_tool("daily_news")
    assert not is_read_only_tool("private_delete")
    result = bounded_result(status="completed", evidence_ids=("ev-1",))
    assert result == {"status": "completed", "evidence_ids": ("ev-1",), "artifact_ids": ()}


def test_side_effect_adapter_boundary_abstains_without_a_handler() -> None:
    assert requires_explicit_approval("private_delete")
    assert not requires_explicit_approval("cited_answer")
    result = abstained_result("private_delete")
    assert result["status"] == "abstained"
    assert result["reason"] == "side_effect_requires_approval"
