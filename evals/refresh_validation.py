"""Record one day of the seven-day failed-refresh safety validation."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import psycopg

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "apps" / "backend" / "src"))

from atlas.config import Settings
from atlas.domain import CollectionSlug


def validate_failed_refresh(day: int, collection: CollectionSlug) -> dict[str, object]:
    if not 1 <= day <= 7:
        raise ValueError("day must be between 1 and 7")
    settings = Settings()
    dsn = settings.database_url.get_secret_value().replace("postgresql+psycopg://", "postgresql://", 1)
    key = f"refresh-validation-day-{day}-{uuid4()}"
    observed_at = datetime.now(UTC)
    with psycopg.connect(dsn) as connection:
        before = connection.execute(
            "SELECT id FROM atlas.corpus_snapshots ORDER BY revision DESC LIMIT 1"
        ).fetchone()
        if before is None:
            raise RuntimeError("a promoted snapshot is required before refresh validation")
        collection_id = connection.execute(
            "SELECT id FROM atlas.collections WHERE slug = %s", (collection.value,)
        ).fetchone()
        if collection_id is None:
            raise RuntimeError(f"collection is not seeded: {collection.value}")
        run = connection.execute(
            "SELECT atlas.enqueue_ingestion(%s, 'operator', %s, 'refresh-validation')",
            (collection_id[0], key),
        ).fetchone()
        if run is None:
            raise RuntimeError("failed refresh run was not created")
        connection.execute(
            "SELECT atlas.fail_ingestion_run(%s, 'validation_failure', 3)",
            (run[0],),
        )
        connection.commit()
        after = connection.execute(
            "SELECT id FROM atlas.corpus_snapshots ORDER BY revision DESC LIMIT 1"
        ).fetchone()
        status = connection.execute(
            "SELECT status FROM atlas.ingestion_runs WHERE id = %s", (run[0],)
        ).fetchone()
    preserved = after is not None and after[0] == before[0]
    return {
        "day": day,
        "observed_at": observed_at.isoformat(),
        "collection": collection.value,
        "snapshot_before": str(before[0]),
        "snapshot_after": str(after[0]) if after else None,
        "failed_run_status": status[0] if status else None,
        "snapshot_preserved": preserved,
    }


def main() -> int:
    parser = argparse.ArgumentParser(prog="atlas-refresh-validation")
    parser.add_argument("--day", type=int, required=True)
    parser.add_argument("--collection", choices=[slug.value for slug in CollectionSlug], default="anthropic")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    record = validate_failed_refresh(args.day, CollectionSlug(args.collection))
    serialized = json.dumps(record, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(serialized, end="")
    if not record["snapshot_preserved"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
