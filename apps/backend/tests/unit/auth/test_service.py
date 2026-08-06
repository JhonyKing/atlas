from uuid import UUID

import pytest

from atlas.auth.fake_provider import FakeAuthProvider
from atlas.auth.ports import AuthError
from atlas.auth.service import SessionService


def test_session_service_delegates_login_and_validation_to_auth_port() -> None:
    subject_id = UUID("00000000-0000-0000-0000-000000000001")
    service = SessionService(
        FakeAuthProvider({"ana@example.test": ("secret", subject_id)})
    )

    issued = service.login("ana@example.test", "secret")

    assert service.current(issued.access_token).subject_id == subject_id


def test_session_service_rejects_missing_or_invalid_tokens() -> None:
    service = SessionService(FakeAuthProvider({"ana@example.test": ("secret", None)}))

    with pytest.raises(AuthError, match="invalid session"):
        service.current(None)
    with pytest.raises(AuthError, match="invalid session"):
        service.current("not-a-real-token")
