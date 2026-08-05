import json
from pathlib import Path

from atlas.ingestion.bootstrap import main

MANIFEST = Path(__file__).resolve().parents[5] / "corpus" / "manifests" / "launch-v1.yaml"


def test_bootstrap_defaults_to_safe_dry_run(capsys) -> None:
    exit_code = main(["--manifest", str(MANIFEST)])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["execute"] is False
    assert payload["source_count"] == 12
    assert payload["review_status"] == "pending_operator_approval"

