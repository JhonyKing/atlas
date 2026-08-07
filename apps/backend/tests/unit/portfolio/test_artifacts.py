import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]


def test_portfolio_kpis_and_evidence_ledger_are_valid_and_linked() -> None:
    kpis = json.loads((ROOT / "docs/portfolio/kpis.json").read_text(encoding="utf-8"))
    ledger = json.loads((ROOT / "docs/portfolio/evidence-ledger.json").read_text(encoding="utf-8"))
    assert len(kpis["definitions"]) >= 7
    assert len(ledger["entries"]) >= 5
    for entry in ledger["entries"]:
        if entry["status"] == "verified-local":
            assert (ROOT / entry["artifact"]).exists()


def test_readme_points_to_the_portfolio_proof() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "docs/portfolio" in readme
    assert "Feature 011" in readme
