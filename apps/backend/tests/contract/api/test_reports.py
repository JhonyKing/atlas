import time
from datetime import UTC, datetime, timedelta
from uuid import uuid4

from fastapi.testclient import TestClient

from atlas.api.main import create_app
from atlas.api.routes.comparisons import ComparisonRunResponse
from atlas.comparison.schemas import (
    ComparisonCell,
    ComparisonCellState,
    ComparisonCriterion,
    ComparisonMatrix,
)
from atlas.domain import CollectionSlug
from atlas.reports.service import InMemoryReportService
from atlas.reports.storage import LocalArtifactStorage


class Source:
    def __init__(self, run: ComparisonRunResponse) -> None:
        self.run = run

    async def get_status(self, run_id, *, visitor_key_hash):
        del visitor_key_hash
        return self.run if run_id == self.run.run_id else None


def test_create_report_completes_and_downloads_pdf(tmp_path) -> None:
    run_id = uuid4()
    evidence_id = uuid4()
    matrix = ComparisonMatrix(
        technology_ids=[CollectionSlug("openai"), CollectionSlug("anthropic")],
        criterion_ids=[ComparisonCriterion.CAPABILITY],
        cells=[
            ComparisonCell(
                technology_id=CollectionSlug("openai"),
                criterion_id=ComparisonCriterion.CAPABILITY,
                state=ComparisonCellState.SUPPORTED,
                value="yes",
                evidence_ids=[evidence_id],
            ),
            ComparisonCell(
                technology_id=CollectionSlug("anthropic"),
                criterion_id=ComparisonCriterion.CAPABILITY,
                state=ComparisonCellState.SUPPORTED,
                value="yes",
                evidence_ids=[evidence_id],
            ),
        ],
    )
    source = Source(
        ComparisonRunResponse(
            run_id=run_id,
            status="completed",
            created_at=datetime.now(UTC),
            completed_at=datetime.now(UTC),
            matrix=matrix,
            retained_until=datetime.now(UTC) + timedelta(days=30),
        )
    )
    report_service = InMemoryReportService(source=source, storage=LocalArtifactStorage(tmp_path))
    client = TestClient(create_app(report_service=report_service), base_url="https://testserver")
    body = {"source_run_id": str(run_id), "audience": "engineer", "scope": "comparison"}
    response = client.post(
        "/v1/reports", json=body, headers={"Idempotency-Key": "report-test-key-001"}
    )
    assert response.status_code == 202
    report_id = response.json()["report_id"]
    for _ in range(50):
        status = client.get(f"/v1/reports/{report_id}")
        if status.json().get("status") in {"completed", "failed"}:
            break
        time.sleep(0.02)
    assert status.json()["status"] == "completed"
    pdf = client.get(f"/v1/reports/{report_id}/download", params={"format": "pdf"})
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert len(pdf.content) > 100
