import asyncio
from uuid import UUID, uuid4

import pytest

from atlas.reports.schemas import ReportSpec
from atlas.reports.service import InMemoryReportService, ReportQuotaExceeded


class Source:
    async def get_status(self, run_id: UUID, *, visitor_key_hash: str) -> None:
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


@pytest.mark.asyncio
async def test_default_report_quota_is_twenty_per_visitor_per_rolling_day() -> None:
    service = InMemoryReportService(source=Source())
    for index in range(20):
        await service.create(
            ReportSpec(source_run_id=uuid4(), audience="engineer", scope="comparison"),
            owner_key_hash="visitor-one",
            idempotency_key=f"report-key-{index:04d}",
            request_id=uuid4(),
        )
    with pytest.raises(ReportQuotaExceeded):
        await service.create(
            ReportSpec(source_run_id=uuid4(), audience="engineer", scope="comparison"),
            owner_key_hash="visitor-one",
            idempotency_key="report-key-limit",
            request_id=uuid4(),
        )

    # Quotas are isolated by visitor identity, not shared globally.
    await service.create(
        ReportSpec(source_run_id=uuid4(), audience="engineer", scope="comparison"),
        owner_key_hash="visitor-two",
        idempotency_key="report-key-other-visitor",
        request_id=uuid4(),
    )
    await asyncio.sleep(0)
