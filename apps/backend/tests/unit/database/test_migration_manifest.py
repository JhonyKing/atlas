"""Tests for the repository migration manifest contract."""

from itertools import pairwise
from pathlib import Path

import pytest

from atlas.database.migration_manifest import load_migration_manifest


def test_repository_contains_one_ordered_27_revision_chain() -> None:
    root = Path(__file__).resolve().parents[5]
    manifest = load_migration_manifest(root / "database" / "migrations" / "versions")

    assert len(manifest) == 27
    assert manifest[0].revision_id == "0001_foundation"
    assert manifest[-1].revision_id == "0027_revoke_public_rls_helper"
    assert all(item.sha256 for item in manifest)
    assert all(
        current.down_revision == previous.revision_id
        for previous, current in pairwise(manifest)
    )


def test_manifest_rejects_an_unexpected_revision_count(tmp_path: Path) -> None:
    source = Path(__file__).resolve().parents[5] / "database" / "migrations" / "versions"
    for path in source.glob("*.py"):
        (tmp_path / path.name).write_bytes(path.read_bytes())

    with pytest.raises(ValueError, match="Expected 28 migrations"):
        load_migration_manifest(tmp_path, expected_count=28)
