from __future__ import annotations

from collections.abc import Callable
from datetime import timedelta
from uuid import UUID, uuid4

import pytest

from atlas.api.comparison_service import InMemoryComparisonRunService
from atlas.comparison.schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
    ComparisonRequest,
)
from atlas.domain import CollectionSlug
from atlas.persistence.comparison_quota import (
    ComparisonQuotaService,
    InMemoryComparisonQuotaRepository,
)
from atlas.persistence.comparison_repository import InMemoryComparisonRepository


class FakeExecutor:
    async def run(
        self, comparison: ComparisonRequest, *, snapshot_id: UUID, is_cancelled: Callable[[], bool]
    ) -> ComparisonMatrix:
        return ComparisonMatrix(
            technology_ids=[CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI],
            criterion_ids=[ComparisonCriterion.CAPABILITY],
            cells=[
                ComparisonCell(
                    technology_id=technology,
                    criterion_id=ComparisonCriterion.CAPABILITY,
                    state=ComparisonCellState.UNSUPPORTED,
                    explanation="Fixture has no comparison evidence.",
                    evidence_ids=[],
                )
                for technology in [CollectionSlug.LANGGRAPH, CollectionSlug.OPENAI]
            ],
        )


def _service(executor: FakeExecutor | None = None) -> InMemoryComparisonRunService:
    return InMemoryComparisonRunService(
        quota=ComparisonQuotaService(
            InMemoryComparisonQuotaRepository(
                limit=5, window=timedelta(hours=24)
            )
        ),
        repository=InMemoryComparisonRepository(),
        snapshot_provider=lambda: uuid4(),
        executor=executor,
    )


@pytest.mark.asyncio
async def test_service_emits_terminal_matrix_only_after_executor_completes() -> None:
    service = _service(FakeExecutor())
    run_id = await service.start(
        comparison={"technologies": ["langgraph", "openai"], "criteria": ["capability"]},
        visitor_key_hash="a" * 64,
        idempotency_key="comparison-service-key-01",
        request_id=uuid4(),
    )
    frames = [frame async for frame in service.stream(run_id, visitor_key_hash="a" * 64)]

    assert any("comparison.accepted" in frame for frame in frames)
    assert any("comparison.completed" in frame for frame in frames)
    assert "Fixture has no comparison evidence." in "".join(frames)

    stored = service._repository.get(run_id, visitor_key_hash="a" * 64)
    assert stored.run.status.value == "completed"
    assert stored.matrix is not None


@pytest.mark.asyncio
async def test_service_without_executor_fails_closed_without_matrix() -> None:
    service = _service()
    run_id = await service.start(
        comparison={"technologies": ["langgraph", "openai"], "criteria": ["capability"]},
        visitor_key_hash="b" * 64,
        idempotency_key="comparison-service-key-02",
        request_id=uuid4(),
    )
    frames = [frame async for frame in service.stream(run_id, visitor_key_hash="b" * 64)]
    assert any("comparison.failed" in frame for frame in frames)
    status = await service.get_status(run_id, visitor_key_hash="b" * 64)
    assert status is not None and status.status == "failed" and status.matrix is None
