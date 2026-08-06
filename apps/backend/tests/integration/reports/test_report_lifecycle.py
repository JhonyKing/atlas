import asyncio
from pathlib import Path
from uuid import uuid4

import pytest

from atlas.reports.schemas import ReportSpec, ReportStatus
from atlas.reports.service import InMemoryReportService, ReportNotFound
from atlas.reports.storage import LocalArtifactStorage

from ...unit.reports.test_planner import Source, _completed


@pytest.mark.asyncio
async def test_delete_is_repeat_safe_and_removes_downloads(tmp_path: Path) -> None:
    source = _completed()
    service = InMemoryReportService(source=Source(source), storage=LocalArtifactStorage(tmp_path))
    report_id = await service.create(
        ReportSpec(source_run_id=source.run_id, audience="engineer", scope="comparison"),
        owner_key_hash="visitor",
        idempotency_key="report-lifecycle-123",
        request_id=uuid4(),
    )
    for _ in range(100):
        job = await service.get(report_id, owner_key_hash="visitor")
        if job.status in {ReportStatus.COMPLETED, ReportStatus.FAILED}:
            break
        await asyncio.sleep(0.01)
    assert job.status is ReportStatus.COMPLETED
    await service.delete(report_id, owner_key_hash="visitor")
    deleted = await service.delete(report_id, owner_key_hash="visitor")
    assert deleted.status is ReportStatus.DELETED
    with pytest.raises(ReportNotFound):
        await service.download(report_id, owner_key_hash="visitor", format="pdf")


@pytest.mark.asyncio
async def test_foreign_owner_cannot_read_report(tmp_path: Path) -> None:
    source = _completed()
    service = InMemoryReportService(source=Source(source), storage=LocalArtifactStorage(tmp_path))
    report_id = await service.create(
        ReportSpec(source_run_id=source.run_id, audience="engineer", scope="comparison"),
        owner_key_hash="visitor",
        idempotency_key="report-owner-123456",
        request_id=uuid4(),
    )
    with pytest.raises(ReportNotFound):
        await service.get(report_id, owner_key_hash="another-visitor")
