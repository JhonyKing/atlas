"""Schema inventory assertions remain bounded to object identifiers."""

from atlas.database.supabase_workflow import RemoteSnapshot, compare_state


def test_expected_objects_are_present_in_snapshot() -> None:
    remote = RemoteSnapshot(
        project_ref="fcbclsaytbjpywlaplbh",
        environment="development",
        remote_revisions=("0001_foundation",),
        tables=("atlas.collections", "atlas.answer_runs"),
        constraints=("atlas.collections_pkey", "atlas.answer_runs_user_id_fkey"),
        functions=("atlas.search_evidence",),
        indexes=("atlas.ix_chunks_collection_id",),
        policies=("private_uploads_owner_select",),
        extensions=("vector",),
    )
    findings = compare_state(
        ("0001_foundation",),
        remote,
        expected_inventory={
            "table": ["atlas.collections", "atlas.answer_runs"],
            "function": ["atlas.search_evidence"],
            "index": ["atlas.ix_chunks_collection_id"],
            "policy": ["private_uploads_owner_select"],
            "extension": ["vector"],
        },
    )
    assert findings == []
    assert "atlas.collections_pkey" in remote.constraints
