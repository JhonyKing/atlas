
from atlas.ingestion.catalog import build_default_catalog
from atlas.ingestion.governance import InMemoryGovernanceRepository


def test_failed_refresh_preserves_last_good_and_enters_dead_letter_after_retries() -> None:
    repository = InMemoryGovernanceRepository(build_default_catalog())
    collection = build_default_catalog()[0]
    run = repository.start_run(collection.slug, trigger="scheduled", max_attempts=2)
    repository.capture(
        collection=collection.slug,
        url=f"https://{next(iter(collection.allowed_hosts))}{collection.allowed_paths[0]}guide.md",
        title="Guide",
        normalized_markdown="# Good",
        content_sha256="a" * 64,
    )
    repository.fail_run(run.run_id, "timeout")
    repository.fail_run(run.run_id, "timeout")
    assert repository.run(run.run_id).status == "dead_letter"
    assert repository.coverage().dead_letter_count == 1
    assert repository.events()[-1]["outcome"] == "dead_letter"
    assert repository.events()[-1]["error_code"] == "timeout"
