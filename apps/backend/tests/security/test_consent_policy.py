from uuid import uuid4

import pytest

from atlas.privacy.consent import assert_private_not_promoted, grant_consent, withdraw_consent


def test_consent_is_bilingual_and_withdrawal_is_repeat_safe() -> None:
    record = grant_consent(uuid4(), scope="private-documents", locale="es-MX", policy_version="v1")
    withdrawn = withdraw_consent(record)
    assert not withdrawn.active
    assert withdraw_consent(withdrawn) == withdrawn


def test_private_content_requires_tenant_boundary() -> None:
    with pytest.raises(ValueError, match="tenant"):
        assert_private_not_promoted(provenance="private_upload", tenant_id=None)
