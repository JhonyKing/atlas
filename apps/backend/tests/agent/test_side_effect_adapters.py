from __future__ import annotations

import pytest

from atlas.agent.planning import validate_plan
from atlas.agent.policy import issue_approval
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolCallRequest
from atlas.agent.tools.side_effects import SideEffectToolAdapters


def _delete_plan():
    return validate_plan(
        catalog=ToolCatalog.default(),
        request="Delete my private resource",
        locale="en-US",
        steps=(
            ToolCallRequest(
                tool_id="private_delete",
                tool_version="1.0.0",
                arguments={"resource_id": "resource-1"},
            ),
        ),
    )


def _approved(plan, *, actor_id: str = "user-1"):
    return issue_approval(
        plan,
        call_id="step-0",
        actor_id=actor_id,
        tool_id="private_delete",
        tool_version="1.0.0",
        arguments={"resource_id": "resource-1"},
        decision="approved",
    )


@pytest.mark.asyncio
async def test_side_effect_adapter_requires_matching_approval_before_handler() -> None:
    called = False

    async def handler(_arguments: dict[str, object]) -> dict[str, object]:
        nonlocal called
        called = True
        return {"status": "completed"}

    plan = _delete_plan()
    adapters = SideEffectToolAdapters(
        ToolCatalog.default(), {"private_delete": handler}, owner_check=lambda *_: True
    )

    result = await adapters.execute(
        "private_delete", {"resource_id": "resource-1"}, plan=plan, actor_id="user-1"
    )

    assert result["status"] == "abstained"
    assert result["reason"] == "approval_required"
    assert called is False


@pytest.mark.asyncio
async def test_side_effect_adapter_enforces_ownership_after_approval() -> None:
    async def handler(_arguments: dict[str, object]) -> dict[str, object]:
        return {"status": "completed", "artifact_ids": ["deleted-1"]}

    plan = _delete_plan()
    approval = _approved(plan)
    adapters = SideEffectToolAdapters(
        ToolCatalog.default(), {"private_delete": handler}, owner_check=lambda *_: False
    )

    result = await adapters.execute(
        "private_delete",
        {"resource_id": "resource-1"},
        plan=plan,
        actor_id="user-1",
        approval=approval,
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "ownership_denied"


@pytest.mark.asyncio
async def test_side_effect_adapter_executes_only_approved_owned_action() -> None:
    calls: list[dict[str, object]] = []

    async def handler(arguments: dict[str, object]) -> dict[str, object]:
        calls.append(arguments)
        return {"status": "completed", "artifact_ids": ["deleted-1"]}

    plan = _delete_plan()
    approval = _approved(plan)
    adapters = SideEffectToolAdapters(
        ToolCatalog.default(), {"private_delete": handler}, owner_check=lambda *_: True
    )

    result = await adapters.execute(
        "private_delete",
        {"resource_id": "resource-1"},
        plan=plan,
        actor_id="user-1",
        approval=approval,
    )

    assert result["status"] == "completed"
    assert result["artifact_ids"] == ("deleted-1",)
    assert calls == [{"resource_id": "resource-1"}]


@pytest.mark.asyncio
async def test_side_effect_adapter_requires_explicit_consent() -> None:
    called = False

    async def handler(_arguments: dict[str, object]) -> dict[str, object]:
        nonlocal called
        called = True
        return {"status": "completed"}

    plan = _delete_plan()
    adapters = SideEffectToolAdapters(
        ToolCatalog.default(), {"private_delete": handler}, owner_check=lambda *_: True
    )

    result = await adapters.execute(
        "private_delete",
        {"resource_id": "resource-1"},
        plan=plan,
        actor_id="user-1",
        approval=_approved(plan),
        consent=False,
    )

    assert result["status"] == "rejected"
    assert result["reason"] == "consent_required"
    assert called is False


def test_side_effect_adapter_rejects_read_only_or_unknown_registration() -> None:
    async def handler(_arguments: dict[str, object]) -> dict[str, object]:
        return {"status": "completed"}

    with pytest.raises(ValueError, match="side-effect"):
        SideEffectToolAdapters(ToolCatalog.default(), {"cited_answer": handler})
