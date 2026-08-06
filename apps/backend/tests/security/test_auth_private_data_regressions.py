from uuid import UUID, uuid4

from atlas.auth.fake_provider import FakeAuthProvider
from atlas.observability.events import security_event
from atlas.privacy.ownership import InMemoryOwnershipService, ResourceNotFound
from atlas.uploads.pipeline import PrivateUploadPipeline, UploadRejected


def test_cross_user_resource_access_is_denied_without_disclosing_existence() -> None:
    service = InMemoryOwnershipService()
    owner = UUID("00000000-0000-0000-0000-000000000001")
    other = UUID("00000000-0000-0000-0000-000000000002")
    resource = service.create(owner, "report", {})

    try:
        service.get_owned(other, resource.resource_id)
    except ResourceNotFound as exc:
        assert str(resource.resource_id) not in str(exc)
    else:
        raise AssertionError("cross-user access must be denied")


def test_rejected_upload_is_not_indexable() -> None:
    pipeline = PrivateUploadPipeline()
    try:
        pipeline.submit(
            UUID("00000000-0000-0000-0000-000000000001"),
            filename="unsafe.txt",
            declared_content_type="text/plain",
            content=b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE",
        )
    except UploadRejected as exc:
        assert exc.record is not None and exc.record.indexable is False
    else:
        raise AssertionError("unsafe upload must be rejected")
    assert pipeline.indexable_uploads() == []


def test_security_event_redacts_token_and_private_content() -> None:
    event = security_event(
        request_id=uuid4(),
        operation="private.upload.accepted",
        subject_id=None,
        fields={"session_token": "secret", "private_content": "hidden", "status": "clean"},
    )
    assert event["fields"] == {
        "session_token": "[REDACTED]",
        "private_content": "[REDACTED]",
        "status": "clean",
    }


def test_fake_auth_never_leaks_provider_password_or_token_in_repr() -> None:
    provider = FakeAuthProvider({"ana@example.test": ("provider-password", None)})
    issued = provider.login("ana@example.test", "provider-password")
    rendered = repr(issued)
    assert "provider-password" not in rendered
    assert issued.access_token not in rendered
