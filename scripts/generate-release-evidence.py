"""Create a schema-compatible, secret-free release evidence bundle."""
from __future__ import annotations

import argparse
import json
import os
import re
from datetime import UTC, datetime
from pathlib import Path

SECRET_MARKERS = re.compile(r"(?i)(api[_-]?key|secret|password|token|authorization)\s*[:=]")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--release-id", default=os.getenv("GITHUB_RUN_ID", "local"))
    parser.add_argument("--source-revision", default=os.getenv("GITHUB_SHA", "local"))
    parser.add_argument("--migration-revision", default=os.getenv("ATLAS_MIGRATION_REVISION", "unknown"))
    parser.add_argument("--status", choices=("passed", "failed", "skipped"), default="passed")
    args = parser.parse_args()
    if args.source_revision != "local" and len(args.source_revision) < 7:
        raise SystemExit("source revision must be a commit SHA or local")
    now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
    bundle = {
        "release_id": args.release_id,
        "source_revision": args.source_revision,
        "web_build_id": os.getenv("VERCEL_GIT_COMMIT_SHA"),
        "api_image_digest": os.getenv("ATLAS_API_IMAGE_DIGEST"),
        "migration_revision": args.migration_revision,
        "checks": [
            {
                "name": name,
                "status": args.status,
                "observed_at": now,
                "evidence_url": None,
                "summary": summary,
            }
            for name, summary in (
                ("repository-release-gates", "Recorded by CI."),
                ("corpus-version", os.getenv("ATLAS_CORPUS_VERSION", "unknown")),
                ("model-version", os.getenv("ATLAS_ANSWER_MODEL", "gpt-5.6-luna")),
                ("locale-version", os.getenv("ATLAS_LOCALE_VERSION", "en-US,es-MX")),
            )
        ],
        "smoke_results": [],
        "health": {"environment": os.getenv("ATLAS_ENV", "unknown"), "status": "pending"},
        "created_at": now,
    }
    serialized = json.dumps(bundle, ensure_ascii=False, indent=2)
    if SECRET_MARKERS.search(serialized) or re.search(r"sk-[A-Za-z0-9]{20,}", serialized):
        raise SystemExit("refusing to write a bundle containing a secret marker")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
