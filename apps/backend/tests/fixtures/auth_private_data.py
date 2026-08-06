"""Deterministic fixtures shared by Feature 004 tests."""

from uuid import UUID

from atlas.auth.fake_provider import FakeAuthProvider
from atlas.privacy.ownership import InMemoryOwnershipService
from atlas.uploads.pipeline import PrivateUploadPipeline

TEST_SUBJECT = UUID("00000000-0000-0000-0000-000000000001")


def feature004_fixtures() -> tuple[
    FakeAuthProvider,
    InMemoryOwnershipService,
    PrivateUploadPipeline,
]:
    return (
        FakeAuthProvider({"ana@example.test": ("secret", TEST_SUBJECT)}),
        InMemoryOwnershipService(),
        PrivateUploadPipeline(),
    )
