"""Small CLI wrapper for writing a validated evidence artifact."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from atlas.database.evidence_writer import write_evidence
from atlas.database.migration_evidence import MigrationEvidence


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("evals/results"))
    parser.add_argument("--run-id", required=True)
    args = parser.parse_args()
    now = datetime.now(UTC)
    evidence = MigrationEvidence(
        run_id=args.run_id,
        environment="unknown",
        mode="inspect",
        started_at=now,
        finished_at=now,
        checks=[{"name": "cli", "status": "blocked", "detail": "Remote MCP not invoked"}],
        status="blocked",
    )
    print(write_evidence(evidence, args.output_dir))


if __name__ == "__main__":
    main()
