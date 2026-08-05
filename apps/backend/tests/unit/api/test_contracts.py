from pathlib import Path

from atlas.api.contracts import (
    COMPARISON_CONTRACT_FILES,
    COMPARISON_EVENT_NAMES,
    COMPARISON_ROUTES,
)


def test_comparison_contract_registry_points_to_spec_kit_contracts() -> None:
    repository_root = Path(__file__).resolve().parents[5]
    assert all((repository_root / path).is_file() for path in COMPARISON_CONTRACT_FILES.values())
    assert COMPARISON_ROUTES == (
        "POST /v1/comparisons",
        "GET /v1/comparisons/{run_id}",
        "DELETE /v1/comparisons/{run_id}",
    )
    assert COMPARISON_EVENT_NAMES[-1] == "failed"
