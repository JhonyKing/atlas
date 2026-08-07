from fastapi.testclient import TestClient

from atlas.api.main import create_app


def test_prepare_endpoint_exposes_route_without_private_state() -> None:
    client = TestClient(create_app())
    response = client.post("/v1/agent/prepare", json={"request": "How does LangGraph work?"})
    assert response.status_code == 200
    assert response.json()["node_history"] == ["classify", "plan", "answer"]
    assert "request" not in response.json()
    thread_id = response.json()["thread_id"]
    replay_key = response.json()["request_id"]
    status = client.get(f"/v1/agent/threads/{thread_id}/status", params={"replay_key": replay_key})
    assert status.status_code == 200
    resumed = client.post(
        f"/v1/agent/threads/{thread_id}/resume", params={"replay_key": replay_key}
    )
    assert resumed.status_code == 200
    assert resumed.json()["claimed"] is True
