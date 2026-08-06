from uuid import uuid4

import pytest

from atlas.reports.schemas import ReportSpec
from atlas.reports.service import InMemoryReportService


class Source:
    async def get_status(self, run_id, *, visitor_key_hash):
        del run_id, visitor_key_hash
        return None


@pytest.mark.asyncio
async def test_same_key_and_parameters_replays_one_report() -> None:
    service = InMemoryReportService(source=Source())
    spec = ReportSpec(source_run_id=uuid4(), audience="engineer", scope="comparison")
    first = await service.create(
        spec,
        owner_key_hash="visitor",
        idempotency_key="report-key-123456",
        request_id=uuid4(),
    )
    second = await service.create(
        spec,
        owner_key_hash="visitor",
        idempotency_key="report-key-123456",
        request_id=uuid4(),
    )
    assert first == second


@pytest.mark.asyncio
async def test_same_key_with_different_parameters_is_rejected() -> None:
    service = InMemoryReportService(source=Source())
    first = ReportSpec(source_run_id=uuid4(), audience="engineer", scope="comparison")
    second = first.model_copy(update={"audience": "architect"})
    await service.create(
        first,
        owner_key_hash="visitor",
        idempotency_key="report-key-654321",
        request_id=uuid4(),
    )
    with pytest.raises(ValueError, match="idempotency_conflict"):
        await service.create(
            second,
            owner_key_hash="visitor",
            idempotency_key="report-key-654321",
            request_id=uuid4(),
        )
