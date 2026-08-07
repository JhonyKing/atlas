import json
from pathlib import Path

import pytest

from atlas.ingestion.bootstrap import main

MANIFEST = Path(__file__).resolve().parents[5] / "corpus" / "manifests" / "launch-v1.yaml"
EXPANSION_MANIFEST = (
    Path(__file__).resolve().parents[5] / "corpus" / "manifests" / "expansion-v1.yaml"
)


def test_bootstrap_defaults_to_safe_dry_run(capsys: pytest.CaptureFixture[str]) -> None:
    exit_code = main(["--manifest", str(MANIFEST)])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["execute"] is False
    assert payload["source_count"] == 12
    assert payload["review_status"] == "approved"


def test_bootstrap_refuses_network_execution_for_pending_source_review(tmp_path: Path) -> None:
    pending = tmp_path / "pending.yaml"
    pending.write_text(
        MANIFEST.read_text(encoding="utf-8").replace(
            "review_status: approved", "review_status: pending_source_review"
        ),
        encoding="utf-8",
    )
    with pytest.raises(RuntimeError, match="review_status=approved"):
        main(["--manifest", str(pending), "--execute"])
