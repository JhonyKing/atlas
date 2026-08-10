from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app


def test_tool_catalog_and_read_only_run_are_explicit() -> None:
    client = TestClient(create_app())
    catalog = client.get("/v1/agent/tools", params={"locale": "es-MX"})
    assert catalog.status_code == 200
    assert catalog.json()["locale"] == "es-MX"
    assert {tool["tool_id"] for tool in catalog.json()["tools"]} >= {
        "cited_answer",
        "private_delete",
    }

    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "How does LangGraph persist state?",
            "locale": "en-US",
            "selected_tool": "cited_answer",
            "input": {"question": "How does LangGraph persist state?"},
        },
    )
    assert plan.status_code == 200
    assert plan.json()["required_approval_ids"] == []
    run = client.post("/v1/agent/runs", json={"plan_hash": plan.json()["plan_hash"]})
    assert run.status_code == 202
    assert run.json()["status"] == "completed"
    assert [event["event_type"] for event in run.json()["events"]] == [
        "run.accepted",
        "plan.created",
        "tool_call.abstained",
        "run.completed",
    ]
    tool_call = client.app.state.agent_run_repository.get_tool_call(
        UUID(run.json()["run_id"]), "step-0"
    )
    assert tool_call is not None
    assert tool_call["status"] == "abstained"


def test_side_effect_tool_stays_blocked_until_explicit_approval() -> None:
    client = TestClient(create_app())
    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "Delete my private resource",
            "locale": "en-US",
            "selected_tool": "private_delete",
            "input": {"resource_id": "resource-1"},
        },
    )
    assert plan.status_code == 200
    body = plan.json()
    approval_id = body["required_approval_ids"][0]
    pending = client.post("/v1/agent/runs", json={"plan_hash": body["plan_hash"]})
    assert pending.status_code == 202
    assert pending.json()["status"] == "awaiting_approval"
    pending_call = client.app.state.agent_run_repository.get_tool_call(
        UUID(pending.json()["run_id"]), "step-0"
    )
    assert pending_call is not None
    assert pending_call["status"] == "awaiting_approval"

    decision = client.post(
        f"/v1/agent/approvals/{approval_id}/decision",
        json={
            "actor_id": "anonymous",
            "decision": "approved",
            "decision_key": body["approval_decision_keys"][approval_id],
        },
    )
    assert decision.status_code == 200
    completed = client.post(
        "/v1/agent/runs",
        json={"plan_hash": body["plan_hash"], "approval_ids": [approval_id]},
    )
    assert completed.status_code == 202
    assert completed.json()["status"] == "completed"
    assert any(event["event_type"] == "tool_call.abstained" for event in completed.json()["events"])
    completed_call = client.app.state.agent_run_repository.get_tool_call(
        UUID(completed.json()["run_id"]), "step-0"
    )
    assert completed_call is not None
    assert completed_call["status"] == "abstained"


def test_run_cancel_and_resume_are_explicit_and_non_replaying() -> None:
    client = TestClient(create_app())
    plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "What is the corpus status?",
            "locale": "en-US",
            "selected_tool": "corpus_status",
            "input": {},
        },
    ).json()
    run = client.post("/v1/agent/runs", json={"plan_hash": plan["plan_hash"]}).json()
    run_id = run["run_id"]
    cancelled = client.post(f"/v1/agent/runs/{run_id}/cancel")
    assert cancelled.status_code == 409

    private_plan = client.post(
        "/v1/agent/plans",
        json={
            "request": "Delete my private resource",
            "locale": "en-US",
            "selected_tool": "private_delete",
            "input": {"resource_id": "resource-2"},
        },
    ).json()
    pending = client.post(
        "/v1/agent/runs", json={"plan_hash": private_plan["plan_hash"]}
    ).json()
    pending_id = pending["run_id"]
    assert client.post(f"/v1/agent/runs/{pending_id}/cancel").json()["status"] == "cancelled"
    resumed = client.post(f"/v1/agent/runs/{pending_id}/resume")
    assert resumed.status_code == 200
    assert resumed.json()["status"] == "accepted"
