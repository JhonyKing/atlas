"""Print the validated repository migration manifest as JSON."""

from __future__ import annotations

import json
from pathlib import Path

from atlas.database.migration_manifest import load_migration_manifest


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    manifest = load_migration_manifest(root / "database" / "migrations" / "versions")
    print(json.dumps([item.model_dump(mode="json") for item in manifest], indent=2))


if __name__ == "__main__":
    main()
