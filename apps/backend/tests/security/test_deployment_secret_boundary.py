"""Repository-level checks for secret-free deployment artifacts."""

import re
from pathlib import Path

ROOT = Path(__file__).parents[4]


def test_committed_deployment_artifacts_have_no_real_provider_keys() -> None:
    marker = re.compile(r"sk-[A-Za-z0-9]{20,}")
    for relative in ("docs", "evals/results", "infra", "apps/web/src"):
        target = ROOT / relative
        for path in target.rglob("*"):
            if path.is_file() and path.stat().st_size < 2_000_000:
                content = path.read_text(encoding="utf-8", errors="ignore")
                assert marker.search(content) is None, path
