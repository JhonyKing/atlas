from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.auth.fake_provider import FakeAuthProvider
from atlas.privacy.ownership import InMemoryOwnershipService


def test_authenticated_user_can_list_only_owned_private_resources() -> None:
    subject_id = UUID("00000000-0000-0000-0000-000000000001")
    ownership = InMemoryOwnershipService()
    ownership.create(subject_id, "report", {"title": "Private report"})
    client = TestClient(
        create_app(
            auth_provider=FakeAuthProvider({"ana@example.test": ("secret", subject_id)}),
            private_resource_service=ownership,
        )
    )

    anonymous = client.get("/v1/private/resources")
    client.post(
        "/v1/auth/session",
        json={"email": "ana@example.test", "password": "secret"},
    )
    authenticated = client.get("/v1/private/resources")

    assert anonymous.status_code == 401
    assert authenticated.status_code == 200
    assert authenticated.json()["items"][0]["resource_type"] == "report"


def test_private_resource_delete_is_repeat_safe() -> None:
    subject_id = UUID("00000000-0000-0000-0000-000000000001")
    ownership = InMemoryOwnershipService()
    resource = ownership.create(subject_id, "thread", {})
    client = TestClient(
        create_app(
            auth_provider=FakeAuthProvider({"ana@example.test": ("secret", subject_id)}),
            private_resource_service=ownership,
        )
    )
    client.post("/v1/auth/session", json={"email": "ana@example.test", "password": "secret"})

    first = client.delete(f"/v1/private/resources/{resource.resource_id}")
    repeated = client.delete(f"/v1/private/resources/{resource.resource_id}")

    assert first.status_code == 202
    assert repeated.status_code == 202
