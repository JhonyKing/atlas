import json
from pathlib import Path

import pytest

from atlas.ingestion.bootstrap import main

MANIFEST = Path(__file__).resolve().parents[5] / "corpus" / "manifests" / "launch-v1.yaml"
EXPANSION_MANIFEST = (
    Path(__file__).resolve().parents[5] / "corpus" / "manifests" / "expansion-v1.yaml"
)


def test_bootstrap_defaults_to_safe_dry_run(capsys) -> None:
    exit_code = main(["--manifest", str(MANIFEST)])

    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["execute"] is False
    assert payload["source_count"] == 12
    assert payload["review_status"] == "approved"


def test_bootstrap_refuses_network_execution_for_pending_source_review() -> None:
    with pytest.raises(RuntimeError, match="review_status=approved"):
        main(["--manifest", str(EXPANSION_MANIFEST), "--execute"])
