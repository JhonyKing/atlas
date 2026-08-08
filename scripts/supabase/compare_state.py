"""Compare the repository migration contract with a bounded MCP snapshot."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from atlas.database.migration_manifest import load_migration_manifest
from atlas.database.supabase_workflow import RemoteSnapshot, compare_state


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument(
        "--expected-inventory",
        type=Path,
        help="Optional JSON object with table/function/index/policy/extension/seed arrays.",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[2]
    manifest = load_migration_manifest(root / "database" / "migrations" / "versions")
    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("snapshot must be a JSON object")
    remote = RemoteSnapshot.from_mapping(cast(dict[str, object], payload))
    expected: dict[str, list[str]] | None = None
    if args.expected_inventory is not None:
        raw_expected = json.loads(args.expected_inventory.read_text(encoding="utf-8"))
        if not isinstance(raw_expected, dict):
            raise SystemExit("expected inventory must be a JSON object")
        expected = {
            str(kind): [str(value) for value in values]
            for kind, values in raw_expected.items()
            if isinstance(values, list)
        }
    findings = compare_state(
        [item.revision_id for item in manifest], remote, expected_inventory=expected
    )
    print(json.dumps([finding.model_dump(mode="json") for finding in findings], indent=2))
    if findings:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
