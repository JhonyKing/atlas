from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.auth.fake_provider import FakeAuthProvider


def test_renew_rotates_cookie_and_invalidates_previous_cookie() -> None:
    client = TestClient(
        create_app(
            auth_provider=FakeAuthProvider({"ana@example.test": ("secret", None)})
        )
    )
    client.post("/v1/auth/session", json={"email": "ana@example.test", "password": "secret"})
    old_cookie = client.cookies.get("atlas_session")

    renewed = client.post("/v1/auth/renew")

    assert renewed.status_code == 200
    assert client.cookies.get("atlas_session") != old_cookie
    assert client.get("/v1/auth/session").status_code == 200
