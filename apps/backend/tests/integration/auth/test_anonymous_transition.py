from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.auth.fake_provider import FakeAuthProvider


def test_sign_in_does_not_replace_anonymous_visitor_cookie() -> None:
    client = TestClient(
        create_app(auth_provider=FakeAuthProvider({"ana@example.test": ("secret", None)})),
        base_url="https://testserver",
    )

    before = client.get("/v1/auth/session")
    visitor_cookie = client.cookies.get("atlas_visitor")
    login = client.post(
        "/v1/auth/session",
        json={"email": "ana@example.test", "password": "secret"},
    )

    assert before.status_code == 401
    assert login.status_code == 200
    assert visitor_cookie
    assert client.cookies.get("atlas_visitor") == visitor_cookie
