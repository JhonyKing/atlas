"""Remote retrieval and provenance checks consume only bounded flags."""

from atlas.database.supabase_workflow import RemoteSnapshot


def test_retrieval_provenance_contract_has_required_objects() -> None:
    remote = RemoteSnapshot(
        "fcbclsaytbjpywlaplbh",
        "development",
        ("0001_foundation",),
        functions=("atlas.search_evidence",),
        tables=("atlas.sources", "atlas.source_versions", "atlas.answer_citations"),
    )
    assert "atlas.search_evidence" in remote.functions
    assert "atlas.answer_citations" in remote.tables
