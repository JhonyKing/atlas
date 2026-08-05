from __future__ import annotations

from fastapi.testclient import TestClient

from atlas.api.main import create_app


def test_answers_preflight_allows_browser_origin_and_required_headers() -> None:
    async def database_probe() -> bool:
        return True

    client = TestClient(create_app(database_probe=database_probe))
    response = client.options(
        "/v1/answers",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "accept,content-type,idempotency-key",
        },
    )

    assert response.status_code in {200, 204}
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
    assert "POST" in response.headers["access-control-allow-methods"]
    assert "Idempotency-Key" in response.headers["access-control-allow-headers"]


def test_development_runtime_answers_without_provider_secret() -> None:
    from atlas.api.main import create_runtime_app

    client = TestClient(create_runtime_app(use_real_provider=False))

    corpus = client.get("/v1/corpus")
    answer = client.post(
        "/v1/answers",
        headers={"Idempotency-Key": "local-demo-answer-001"},
        json={"question": "How do conditional edges route state in LangGraph?"},
    )

    assert corpus.status_code == 200
    assert answer.status_code == 200
    assert "event: answer.completed" in answer.text
    assert "citations" in answer.text
