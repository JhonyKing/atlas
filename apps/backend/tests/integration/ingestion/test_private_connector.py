from uuid import UUID

import pytest

from atlas.ingestion.connectors.private_content import PrivateContentConnector


def test_private_connector_requires_owner_and_never_marks_public() -> None:
    owner = UUID("00000000-0000-0000-0000-000000000001")
    connector = PrivateContentConnector(owner_id=owner)
    record = connector.accept(owner, filename="notes.md", content=b"# private")
    assert record.private is True
    assert record.public_promoted is False
    with pytest.raises(PermissionError):
        connector.accept(
            UUID("00000000-0000-0000-0000-000000000002"), filename="x.md", content=b"x"
        )
