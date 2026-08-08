"""Validate bounded security/retrieval results exported by Supabase MCP."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from atlas.database.migration_evidence import MigrationCheck
from atlas.database.supabase_workflow import RemoteSnapshot, timed_check


REQUIRED_CHECKS = ("vector", "retrieval", "provenance", "rls")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    args = parser.parse_args()
    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("snapshot must be a JSON object")
    remote = RemoteSnapshot.from_mapping(cast(dict[str, object], payload))
    raw_checks = payload.get("checks", {})
    if not isinstance(raw_checks, dict):
        raise SystemExit("checks must be a JSON object")
    checks: list[MigrationCheck] = []
    for name in REQUIRED_CHECKS:
        value = raw_checks.get(name)
        checks.append(
            timed_check(
                name,
                lambda value=value: (
                    "verified"
                    if value is True
                    else (_ for _ in ()).throw(RuntimeError("MCP check did not pass"))
                ),
            )
        )
    print(
        json.dumps(
            {
                "project_ref": remote.project_ref,
                "status": "passed" if all(item.status == "passed" for item in checks) else "failed",
                "checks": [item.model_dump(mode="json") for item in checks],
            },
            indent=2,
        )
    )
    if any(item.status != "passed" for item in checks):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
