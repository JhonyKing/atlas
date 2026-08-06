import pytest

from atlas.quotas.service import quota_identity_for_request


def test_authentication_does_not_replace_anonymous_quota_identity() -> None:
    visitor_hash = "a" * 64
    assert quota_identity_for_request(visitor_hash, "user-1") == visitor_hash


def test_quota_identity_rejects_non_hmac_keys() -> None:
    with pytest.raises(ValueError):
        quota_identity_for_request("visitor", None)
