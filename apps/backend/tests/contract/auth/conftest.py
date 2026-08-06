"""Reusable authenticated and anonymous API client fixtures."""

import pytest
from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.auth.fake_provider import FakeAuthProvider
from atlas.privacy.ownership import InMemoryOwnershipService
from atlas.uploads.pipeline import PrivateUploadPipeline


@pytest.fixture
def auth_client() -> TestClient:
    client = TestClient(
        create_app(
            auth_provider=FakeAuthProvider({"ana@example.test": ("secret", None)}),
            private_resource_service=InMemoryOwnershipService(),
            private_upload_pipeline=PrivateUploadPipeline(),
        )
    )
    client.post("/v1/auth/session", json={"email": "ana@example.test", "password": "secret"})
    return client


@pytest.fixture
def anonymous_client() -> TestClient:
    return TestClient(create_app())
