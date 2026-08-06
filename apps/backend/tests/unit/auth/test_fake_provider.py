from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from atlas.auth.fake_provider import AuthError, FakeAuthProvider


def test_fake_provider_issues_and_validates_an_opaque_session() -> None:
    subject_id = UUID("00000000-0000-0000-0000-000000000001")
    provider = FakeAuthProvider(
        {"ana@example.test": ("correct horse", subject_id)},
        ttl=timedelta(minutes=5),
    )
    now = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)

    issued = provider.login("ana@example.test", "correct horse", now=now)

    assert issued.access_token
    assert provider.validate(issued.access_token, now=now).subject_id == subject_id
    assert issued.access_token not in repr(issued)


def test_renewal_rotates_token_and_revokes_the_previous_one() -> None:
    provider = FakeAuthProvider({"ana@example.test": ("secret", None)})
    issued = provider.login("ana@example.test", "secret")

    renewed = provider.renew(issued.access_token)

    assert renewed.access_token != issued.access_token
    with pytest.raises(AuthError, match="revoked session"):
        provider.validate(issued.access_token)
    assert provider.validate(renewed.access_token).subject_id == issued.session.subject_id


def test_expired_and_revoked_sessions_are_rejected() -> None:
    now = datetime(2026, 8, 6, 12, 0, tzinfo=UTC)
    provider = FakeAuthProvider({"ana@example.test": ("secret", None)}, ttl=timedelta(seconds=1))
    issued = provider.login("ana@example.test", "secret", now=now)

    with pytest.raises(AuthError, match="expired session"):
        provider.validate(issued.access_token, now=now + timedelta(seconds=2))

    current = provider.login("ana@example.test", "secret", now=now)
    assert provider.revoke(current.access_token) is True
    assert provider.revoke(current.access_token) is False
    with pytest.raises(AuthError, match="revoked session"):
        provider.validate(current.access_token, now=now)


def test_invalid_credentials_do_not_disclose_account_existence() -> None:
    provider = FakeAuthProvider({"ana@example.test": ("secret", None)})

    with pytest.raises(AuthError, match="invalid credentials"):
        provider.login("missing@example.test", "secret")
    with pytest.raises(AuthError, match="invalid credentials"):
        provider.login("ana@example.test", "wrong")
