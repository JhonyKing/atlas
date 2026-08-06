from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.auth.fake_provider import FakeAuthProvider


def _client() -> TestClient:
    return TestClient(
        create_app(
            auth_provider=FakeAuthProvider(
                {
                    "ana@example.test": (
                        "correct horse",
                        UUID("00000000-0000-0000-0000-000000000001"),
                    )
                }
            )
        )
    )


def test_login_sets_httponly_cookie_and_returns_session_metadata() -> None:
    response = _client().post(
        "/v1/auth/session",
        json={"email": "ana@example.test", "password": "correct horse"},
    )

    assert response.status_code == 200
    assert response.json()["subject_id"] == "00000000-0000-0000-0000-000000000001"
    assert response.cookies.get("atlas_session")
    assert "HttpOnly" in response.headers["set-cookie"]


def test_session_and_logout_use_the_cookie_without_exposing_the_token() -> None:
    client = _client()
    login = client.post(
        "/v1/auth/session",
        json={"email": "ana@example.test", "password": "correct horse"},
    )

    current = client.get("/v1/auth/session")
    logout = client.delete("/v1/auth/session")
    after_logout = client.get("/v1/auth/session")

    assert current.status_code == 200
    assert "access_token" not in current.text
    assert logout.status_code == 204
    assert after_logout.status_code == 401
    assert login.json()["session_id"]
