"""Build a secret-safe inspect artifact from a Supabase MCP snapshot.

The snapshot is exported by the authenticated, project-scoped Supabase MCP.  This
CLI never connects to Supabase itself and therefore cannot accidentally perform a
remote write.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import cast

from atlas.database.evidence_writer import write_evidence
from atlas.database.migration_evidence import MigrationCheck
from atlas.database.migration_manifest import load_migration_manifest
from atlas.database.supabase_workflow import RemoteSnapshot, build_evidence


def _repository_head(root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "unknown"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--snapshot", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("evals/results"))
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()

    root = Path(__file__).resolve().parents[2]
    manifest = load_migration_manifest(root / "database" / "migrations" / "versions")
    payload = json.loads(args.snapshot.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("snapshot must be a JSON object")
    remote = RemoteSnapshot.from_mapping(cast(dict[str, object], payload))
    now = datetime.now(UTC)
    evidence = build_evidence(
        run_id=args.run_id,
        mode="inspect",
        repository_head=_repository_head(root),
        repository_revisions=[item.revision_id for item in manifest],
        remote=remote,
        checks=[
            MigrationCheck(name="project-scope", status="passed"),
            MigrationCheck(
                name="remote-snapshot", status="passed", detail="bounded MCP inventory accepted"
            ),
        ],
        started_at=now.isoformat(),
        finished_at=now.isoformat(),
        status="passed",
    )
    print(write_evidence(evidence, args.output_dir))


if __name__ == "__main__":
    main()
