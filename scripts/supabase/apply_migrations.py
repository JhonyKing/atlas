"""Plan a reviewed, ordered Supabase migration apply.

The actual remote calls are deliberately injected by the authenticated MCP
operator.  This command only validates the remote prefix, environment gate, and
approval flags before printing the exact missing suffix.  It cannot write remotely
by itself.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import cast

from atlas.database.migration_manifest import load_migration_manifest
from atlas.database.supabase_workflow import (
    RemoteSnapshot,
    WorkflowError,
    assert_safe_write,
    plan_missing_revisions,
)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--confirm", action="store_true")
    parser.add_argument("--owner-confirmed", action="store_true")
    parser.add_argument("--apply", action="store_true", help="Require explicit MCP handoff flags.")
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    manifest = load_migration_manifest(root / "database" / "migrations" / "versions")
    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("snapshot must be a JSON object")
    remote = RemoteSnapshot.from_mapping(cast(dict[str, object], payload))
    repository_revisions = [item.revision_id for item in manifest]
    try:
        missing = plan_missing_revisions(repository_revisions, remote.remote_revisions)
        if args.apply:
            if not args.confirm:
                raise WorkflowError("--apply requires --confirm")
            if not args.owner_confirmed:
                raise WorkflowError("--apply requires --owner-confirmed")
            assert_safe_write(remote, owner_confirmed=True)
    except WorkflowError as exc:
        raise SystemExit(f"REFUSED: {exc}") from exc

    print(
        json.dumps(
            {
                "project_ref": remote.project_ref,
                "environment": remote.environment,
                "dry_run": not args.apply,
                "missing_revisions": list(missing),
                "next_action": (
                    "Invoke Supabase MCP apply_migration once per revision in this order."
                    if args.apply and missing
                    else "No remote write requested."
                ),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
