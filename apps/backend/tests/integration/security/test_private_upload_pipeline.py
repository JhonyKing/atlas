from uuid import UUID

import pytest

from atlas.uploads.pipeline import PrivateUploadPipeline, UploadRejected


def test_unsafe_content_cannot_reach_index_stage() -> None:
    pipeline = PrivateUploadPipeline()
    owner = UUID("00000000-0000-0000-0000-000000000001")

    with pytest.raises(UploadRejected):
        pipeline.submit(
            owner,
            filename="payload.txt",
            declared_content_type="text/plain",
            content=b"EICAR-STANDARD-ANTIVIRUS-TEST-FILE",
        )

    assert pipeline.indexable_uploads() == []
