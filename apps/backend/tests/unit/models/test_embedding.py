from atlas.models import select_embedding_profile


def test_embedding_selection_falls_back_without_changing_evidence_contract() -> None:
    selection = select_embedding_profile("es-MX", {"en-US": "openai"})
    assert selection.fallback is True
    assert selection.profile == "baseline:multilingual"
