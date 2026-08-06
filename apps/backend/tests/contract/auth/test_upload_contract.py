import base64
from uuid import UUID

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.auth.fake_provider import FakeAuthProvider
from atlas.privacy.ownership import InMemoryOwnershipService
from atlas.uploads.pipeline import PrivateUploadPipeline


def _client() -> TestClient:
    subject_id = UUID("00000000-0000-0000-0000-000000000001")
    return TestClient(
        create_app(
            auth_provider=FakeAuthProvider({"ana@example.test": ("secret", subject_id)}),
            private_resource_service=InMemoryOwnershipService(),
            private_upload_pipeline=PrivateUploadPipeline(),
        )
    )


def test_valid_upload_is_quarantined_then_clean() -> None:
    client = _client()
    client.post("/v1/auth/session", json={"email": "ana@example.test", "password": "secret"})
    content = base64.b64encode(b"# Private notes\nATLAS").decode("ascii")

    response = client.post(
        "/v1/private/uploads",
        headers={"Idempotency-Key": "upload-key-000001"},
        json={
            "filename": "notes.md",
            "declared_content_type": "text/markdown",
            "content_base64": content,
        },
    )

    assert response.status_code == 202
    assert response.json()["scan_status"] == "clean"
    assert response.json()["parse_status"] == "parsed"
    assert response.json()["detected_content_type"] == "text/markdown"
    assert response.json()["provenance"] == "private_upload"


def test_rejected_upload_is_never_indexable() -> None:
    client = _client()
    client.post("/v1/auth/session", json={"email": "ana@example.test", "password": "secret"})
    content = base64.b64encode(b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE").decode("ascii")

    response = client.post(
        "/v1/private/uploads",
        headers={"Idempotency-Key": "upload-key-000002"},
        json={
            "filename": "bad.txt",
            "declared_content_type": "text/plain",
            "content_base64": content,
        },
    )

    assert response.status_code == 400
    assert response.json()["indexable"] is False
