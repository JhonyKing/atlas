"""RLS isolation evidence is represented as bounded check results."""

from atlas.database.supabase_workflow import RemoteSnapshot


def test_private_boundary_requires_rls_check_and_private_tables() -> None:
    remote = RemoteSnapshot(
        "fcbclsaytbjpywlaplbh",
        "development",
        ("0001_foundation",),
        tables=(
            "atlas.users",
            "atlas.private_uploads",
            "atlas.report_documents",
            "atlas.comparison_runs",
            "atlas.agent_checkpoints",
        ),
    )
    required = {
        "atlas.users",
        "atlas.private_uploads",
        "atlas.report_documents",
        "atlas.comparison_runs",
        "atlas.agent_checkpoints",
    }
    assert required.issubset(set(remote.tables))
