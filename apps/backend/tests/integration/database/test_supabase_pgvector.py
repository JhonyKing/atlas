"""Vector capability checks do not assume an ANN index that the repo never defines."""

from atlas.database.supabase_workflow import RemoteSnapshot


def test_vector_extension_type_and_search_function_are_available() -> None:
    remote = RemoteSnapshot(
        "fcbclsaytbjpywlaplbh",
        "development",
        ("0001_foundation",),
        extensions=("vector",),
        functions=("atlas.search_evidence",),
        tables=("atlas.chunk_embeddings",),
    )
    assert "vector" in remote.extensions
    assert "atlas.search_evidence" in remote.functions
    assert "atlas.chunk_embeddings" in remote.tables
