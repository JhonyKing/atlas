from atlas.ingestion.connectors.pricing_snapshots import PricingSnapshotStore


def test_pricing_snapshot_store_detects_changes_and_preserves_history() -> None:
    store = PricingSnapshotStore()
    first = store.record(
        "gpt-5.6-luna", effective_date="2026-08-01", input_price=1.0, output_price=2.0
    )
    unchanged = store.record(
        "gpt-5.6-luna", effective_date="2026-08-01", input_price=1.0, output_price=2.0
    )
    changed = store.record(
        "gpt-5.6-luna", effective_date="2026-08-05", input_price=0.8, output_price=1.6
    )
    assert first.outcome == "new"
    assert unchanged.outcome == "unchanged"
    assert changed.outcome == "changed"
    assert len(store.history("gpt-5.6-luna")) == 2
