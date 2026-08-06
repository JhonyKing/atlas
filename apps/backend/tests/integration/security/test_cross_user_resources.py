from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.auth.fake_provider import FakeAuthProvider
from atlas.privacy.ownership import InMemoryOwnershipService


def test_user_b_cannot_access_or_delete_user_a_resource() -> None:
    user_a = UUID("00000000-0000-0000-0000-000000000001")
    user_b = UUID("00000000-0000-0000-0000-000000000002")
    ownership = InMemoryOwnershipService()
    resource = ownership.create(user_a, "artifact", {"name": "a-only"})
    provider = FakeAuthProvider(
        {"a@example.test": ("secret-a", user_a), "b@example.test": ("secret-b", user_b)}
    )
    client = TestClient(create_app(auth_provider=provider, private_resource_service=ownership))
    client.post("/v1/auth/session", json={"email": "b@example.test", "password": "secret-b"})

    listing = client.get("/v1/private/resources")
    deletion = client.delete(f"/v1/private/resources/{resource.resource_id}")

    assert listing.status_code == 200
    assert listing.json()["items"] == []
    assert deletion.status_code == 404
