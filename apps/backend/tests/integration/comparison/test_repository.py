from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from atlas.comparison.schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
    ComparisonRun,
    ComparisonRunStatus,
)
from atlas.domain import CollectionSlug
from atlas.persistence.comparison_repository import (
    ComparisonRunNotFound,
    InMemoryComparisonRepository,
)


def _run(visitor: str) -> ComparisonRun:
    return ComparisonRun(
        run_id=uuid4(),
        request_id=uuid4(),
        visitor_key_hash=visitor,
        snapshot_id=uuid4(),
        status=ComparisonRunStatus.ACCEPTED,
        created_at=datetime(2026, 8, 5, tzinfo=UTC),
        retained_until=datetime(2026, 9, 4, tzinfo=UTC),
    )


def _matrix(evidence_id) -> ComparisonMatrix:
    return ComparisonMatrix(
        technology_ids=[CollectionSlug.OPENAI, CollectionSlug.LANGGRAPH],
        criterion_ids=[ComparisonCriterion.CAPABILITY],
        cells=[
            ComparisonCell(
                technology_id=technology,
                criterion_id=ComparisonCriterion.CAPABILITY,
                state=ComparisonCellState.SUPPORTED,
                value="Available",
                evidence_ids=[evidence_id],
            )
            for technology in [CollectionSlug.OPENAI, CollectionSlug.LANGGRAPH]
        ],
    )


def test_repository_round_trips_snapshot_matrix_and_evidence_links() -> None:
    repository = InMemoryComparisonRepository()
    run = _run("a" * 64)
    evidence_id = uuid4()
    repository.create(run)
    repository.save_matrix(run.run_id, _matrix(evidence_id))

    stored = repository.get(run.run_id, visitor_key_hash="a" * 64)

    assert stored.run.snapshot_id == run.snapshot_id
    assert stored.matrix is not None
    assert stored.matrix.cells[0].evidence_ids == [evidence_id]


def test_repository_requires_terminal_timestamp_and_isolates_visitors() -> None:
    repository = InMemoryComparisonRepository()
    run = _run("a" * 64)
    repository.create(run)

    with pytest.raises(ComparisonRunNotFound):
        repository.get(run.run_id, visitor_key_hash="b" * 64)

    repository.save_matrix(run.run_id, _matrix(uuid4()))
    completed = repository.complete(
        run.run_id,
        visitor_key_hash="a" * 64,
        completed_at=datetime(2026, 8, 5, 0, 1, tzinfo=UTC),
    )
    assert completed.status is ComparisonRunStatus.COMPLETED
    assert completed.completed_at is not None
