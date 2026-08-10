from dataclasses import replace
from datetime import UTC, datetime, timedelta

import pytest

from atlas.agent.planning import validate_plan
from atlas.agent.policy import (
    PolicyError,
    assert_approval_matches,
    evaluate_plan_policy,
    issue_approval,
)
from atlas.agent.tools.registry import ToolCatalog
from atlas.agent.tools.schemas import ToolCallRequest


def _private_plan():
    return validate_plan(
        catalog=ToolCatalog.default(),
        request="Delete resource",
        locale="en-US",
        steps=(
            ToolCallRequest(
                tool_id="private_delete", tool_version="1.0.0", arguments={"resource_id": "r-1"}
            ),
        ),
    )


def test_policy_requires_scope_and_consent() -> None:
    plan = _private_plan()
    reasons = evaluate_plan_policy(
        plan, catalog=ToolCatalog.default(), actor_id="user-1", scopes={"anonymous"}
    )
    assert "scope_missing:private_delete" in reasons
    assert "consent_required:private_delete" in reasons


def test_approval_binds_actor_arguments_and_expiry() -> None:
    plan = _private_plan()
    approval = issue_approval(
        plan,
        call_id="step-0",
        actor_id="user-1",
        tool_id="private_delete",
        tool_version="1.0.0",
        arguments={"resource_id": "r-1"},
    )
    approval = replace(approval, decision="approved")
    assert_approval_matches(
        approval,
        plan=plan,
        actor_id="user-1",
        tool_id="private_delete",
        tool_version="1.0.0",
        arguments={"resource_id": "r-1"},
    )
    with pytest.raises(PolicyError, match="arguments"):
        assert_approval_matches(
            approval,
            plan=plan,
            actor_id="user-1",
            tool_id="private_delete",
            tool_version="1.0.0",
            arguments={"resource_id": "r-2"},
        )


def test_approval_key_is_repeatable_and_expiry_is_fail_closed() -> None:
    plan = _private_plan()
    now = datetime(2026, 8, 7, tzinfo=UTC)
    first = issue_approval(
        plan,
        call_id="step-0",
        actor_id="user-1",
        tool_id="private_delete",
        tool_version="1.0.0",
        arguments={"resource_id": "r-1"},
        now=now,
    )
    second = issue_approval(
        plan,
        call_id="step-0",
        actor_id="user-1",
        tool_id="private_delete",
        tool_version="1.0.0",
        arguments={"resource_id": "r-1"},
        now=now,
    )
    assert first.decision_key == second.decision_key
    with pytest.raises(PolicyError, match="expired"):
        assert_approval_matches(
            replace(first, decision="approved", expires_at=now + timedelta(seconds=1)),
            plan=plan,
            actor_id="user-1",
            tool_id="private_delete",
            tool_version="1.0.0",
            arguments={"resource_id": "r-1"},
            now=now + timedelta(seconds=2),
        )


def test_approval_rejects_a_different_bound_target() -> None:
    plan = _private_plan()
    approval = issue_approval(
        plan,
        call_id="step-0",
        actor_id="user-1",
        tool_id="private_delete",
        tool_version="1.0.0",
        arguments={"resource_id": "r-1"},
        target_resource="r-1",
    )

    with pytest.raises(PolicyError, match="target"):
        assert_approval_matches(
            replace(approval, decision="approved", target_resource="r-2"),
            plan=plan,
            actor_id="user-1",
            tool_id="private_delete",
            tool_version="1.0.0",
            arguments={"resource_id": "r-1"},
        )
