"""Persist validated migration evidence without leaking sensitive content."""

from __future__ import annotations

import json
from pathlib import Path

from atlas.database.migration_evidence import MigrationEvidence


def write_evidence(evidence: MigrationEvidence, output_dir: Path) -> Path:
    """Write one validated artifact and return its path."""

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"supabase-migration-{evidence.run_id}.json"
    output_path.write_text(
        json.dumps(evidence.model_dump(mode="json"), indent=2, ensure_ascii=True) + "\n",
        encoding="utf-8",
    )
    return output_path
