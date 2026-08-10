from fastapi.testclient import TestClient

from atlas.api.main import create_app


def test_plan_and_run_idempotency_replay_same_result() -> None:
    client = TestClient(create_app())
    headers = {"Idempotency-Key": "agent-plan-key-001"}
    body = {
        "request": "How does LangGraph persist state?",
        "locale": "en-US",
        "selected_tool": "cited_answer",
        "input": {"question": "How does LangGraph persist state?"},
    }

    first = client.post("/v1/agent/plans", json=body, headers=headers)
    second = client.post("/v1/agent/plans", json=body, headers=headers)

    assert first.status_code == second.status_code == 200
    assert first.json()["plan_hash"] == second.json()["plan_hash"]
    run_headers = {"Idempotency-Key": "agent-run-key-001"}
    run_body = {"plan_hash": first.json()["plan_hash"]}
    run_first = client.post("/v1/agent/runs", json=run_body, headers=run_headers)
    run_second = client.post("/v1/agent/runs", json=run_body, headers=run_headers)
    assert run_first.status_code == run_second.status_code == 202
    assert run_first.json() == run_second.json()


def test_idempotency_key_conflict_is_rejected() -> None:
    client = TestClient(create_app())
    headers = {"Idempotency-Key": "agent-conflict-key-001"}
    first = client.post(
        "/v1/agent/plans",
        json={
            "request": "What is LangGraph?",
            "selected_tool": "cited_answer",
            "input": {"question": "What is LangGraph?"},
        },
        headers=headers,
    )
    second = client.post(
        "/v1/agent/plans",
        json={
            "request": "What is LangChain?",
            "selected_tool": "cited_answer",
            "input": {"question": "What is LangChain?"},
        },
        headers=headers,
    )
    assert first.status_code == 200
    assert second.status_code == 409
