from uuid import UUID

from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from atlas.api.dependencies import optional_subject_id
from atlas.api.routes.auth import router as auth_router
from atlas.auth.fake_provider import FakeAuthProvider


def _app(provider: FakeAuthProvider) -> FastAPI:
    app = FastAPI()
    app.state.auth_provider = provider
    app.include_router(auth_router)

    @app.get("/subject")
    def subject(subject_id=Depends(optional_subject_id)) -> dict[str, str | None]:  # noqa: B008
        return {"subject": str(subject_id) if subject_id else None}

    return app


def test_optional_dependency_keeps_anonymous_requests_anonymous() -> None:
    provider = FakeAuthProvider(
        {
            "ana@example.test": (
                "secret",
                UUID("00000000-0000-0000-0000-000000000001"),
            )
        }
    )
    client = TestClient(_app(provider))

    assert client.get("/subject").json() == {"subject": None}


def test_optional_dependency_returns_subject_for_a_valid_session() -> None:
    subject_id = UUID("00000000-0000-0000-0000-000000000001")
    client = TestClient(
        _app(FakeAuthProvider({"ana@example.test": ("secret", subject_id)}))
    )

    client.post(
        "/v1/auth/session",
        json={"email": "ana@example.test", "password": "secret"},
    )

    assert client.get("/subject").json() == {"subject": str(subject_id)}
