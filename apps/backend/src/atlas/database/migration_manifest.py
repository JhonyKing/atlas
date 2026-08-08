"""Read and validate the repository's ordered Alembic migration manifest."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Final

from pydantic import BaseModel, ConfigDict, Field

REVISION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^revision\s*=\s*[\"']([^\"']+)[\"']", re.MULTILINE
)
DOWN_REVISION_PATTERN: Final[re.Pattern[str]] = re.compile(
    r"^down_revision\s*=\s*(?:None|[\"']([^\"']+)[\"'])", re.MULTILINE
)


class MigrationRevision(BaseModel):
    """A content-addressed repository migration revision."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    revision_id: str = Field(min_length=1)
    down_revision: str | None = None
    path: str = Field(min_length=1)
    sha256: str = Field(pattern=r"^[0-9a-f]{64}$")


def _parse_revision(path: Path) -> MigrationRevision:
    source = path.read_text(encoding="utf-8")
    revision_match = REVISION_PATTERN.search(source)
    down_revision_match = DOWN_REVISION_PATTERN.search(source)
    if revision_match is None or down_revision_match is None:
        raise ValueError(f"Migration metadata is incomplete: {path}")
    return MigrationRevision(
        revision_id=revision_match.group(1),
        down_revision=down_revision_match.group(1),
        path=path.as_posix(),
        sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
    )


def load_migration_manifest(
    migrations_dir: Path, *, expected_count: int = 24
) -> list[MigrationRevision]:
    """Return a validated, dependency-ordered manifest for all migration files."""

    paths = sorted(migrations_dir.glob("*.py"))
    paths = [path for path in paths if path.name != "__init__.py"]
    revisions = [_parse_revision(path) for path in paths]
    if len(revisions) != expected_count:
        raise ValueError(f"Expected {expected_count} migrations, found {len(revisions)}")

    ids = [item.revision_id for item in revisions]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        raise ValueError(f"Duplicate migration revision IDs: {', '.join(duplicates)}")

    by_id = {item.revision_id: item for item in revisions}
    roots = [item for item in revisions if item.down_revision is None]
    if len(roots) != 1:
        raise ValueError(f"Expected one migration root, found {len(roots)}")
    for item in revisions:
        if item.down_revision is not None and item.down_revision not in by_id:
            raise ValueError(
                f"Migration {item.revision_id} references missing down_revision "
                f"{item.down_revision}"
            )

    ordered: list[MigrationRevision] = []
    current = roots[0]
    while True:
        ordered.append(current)
        children = [item for item in revisions if item.down_revision == current.revision_id]
        if not children:
            break
        if len(children) > 1:
            raise ValueError(f"Migration history branches after {current.revision_id}")
        current = children[0]

    if len(ordered) != len(revisions):
        missing = sorted(set(ids) - {item.revision_id for item in ordered})
        raise ValueError(f"Migration history is disconnected: {', '.join(missing)}")
    return ordered
