from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.auth.fake_provider import FakeAuthProvider
from atlas.privacy.ownership import InMemoryOwnershipService
from atlas.uploads.pipeline import PrivateUploadPipeline


def _client() -> TestClient:
    return TestClient(
        create_app(
            auth_provider=FakeAuthProvider(
                {"ana@example.test": ("secret", UUID("00000000-0000-0000-0000-000000000001"))}
            ),
            private_resource_service=InMemoryOwnershipService(),
            private_upload_pipeline=PrivateUploadPipeline(),
        )
    )


def test_locale_preference_is_saved_for_the_authenticated_subject() -> None:
    client = _client()
    client.post("/v1/auth/session", json={"email": "ana@example.test", "password": "secret"})

    initial = client.get("/v1/auth/preferences")
    updated = client.patch("/v1/auth/preferences", json={"locale": "en-US"})
    current = client.get("/v1/auth/preferences")

    assert initial.json() == {"locale": "es-MX"}
    assert updated.json() == {"locale": "en-US"}
    assert current.json() == {"locale": "en-US"}


def test_account_deletion_is_repeat_safe_and_revokes_session() -> None:
    client = _client()
    client.post("/v1/auth/session", json={"email": "ana@example.test", "password": "secret"})

    token = client.cookies.get("atlas_session")
    first = client.delete("/v1/account", headers={"Idempotency-Key": "account-delete-0001"})
    second = client.delete(
        "/v1/account",
        headers={
            "Idempotency-Key": "account-delete-0001",
            "Authorization": f"Bearer {token}",
        },
    )
    after = client.get("/v1/auth/session")

    assert first.status_code == 202
    assert second.status_code == 202
    assert after.status_code == 401
