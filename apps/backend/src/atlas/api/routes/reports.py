"""HTTP contract for evidence-backed report jobs and artifacts."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Header, HTTPException, Request, status
from fastapi.responses import JSONResponse, Response, StreamingResponse

from atlas.observability.context import current_request_id
from atlas.reports.schemas import ReportSpec
from atlas.reports.service import InMemoryReportService, ReportNotFound, ReportQuotaExceeded

router = APIRouter(prefix="/v1/reports", tags=["Reports"])


def _service(request: Request) -> InMemoryReportService:
    service = request.app.state.report_service
    if service is None:
        raise HTTPException(status_code=503, detail="Report service is unavailable")
    return service


def _owner(request: Request) -> str:
    return getattr(request.state, "visitor_key_hash", "development-anonymous-visitor")


def _request_id(request: Request) -> UUID:
    return current_request_id() or UUID(int=0)


def _problem(request: Request, code: int, detail: str, error_code: str) -> JSONResponse:
    request_id = _request_id(request)
    return JSONResponse(
        status_code=code,
        content={"detail": detail, "error_code": error_code, "request_id": str(request_id)},
        media_type="application/problem+json",
        headers={"X-Request-ID": str(request_id)},
    )


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_report(
    request: Request,
    raw_body: dict[str, object],
    idempotency_key: Annotated[
        str, Header(alias="Idempotency-Key", min_length=16, max_length=128)
    ],
) -> JSONResponse:
    try:
        payload = dict(raw_body)
        payload["source_run_id"] = UUID(str(payload["source_run_id"]))
        spec = ReportSpec.model_validate(payload)
    except (KeyError, ValueError):
        return _problem(request, 400, "Report specification is not valid", "invalid_report_spec")
    try:
        report_id = await _service(request).create(
            spec,
            owner_key_hash=_owner(request),
            idempotency_key=idempotency_key,
            request_id=_request_id(request),
        )
    except ValueError:
        return _problem(
            request, 409, "Idempotency key conflicts with another report", "idempotency_conflict"
        )
    except ReportQuotaExceeded:
        return _problem(request, 429, "Report quota exceeded", "quota_exceeded")
    return JSONResponse(
        status_code=202,
        content={
            "report_id": str(report_id),
            "status": "accepted",
            "request_id": str(_request_id(request)),
        },
        headers={
            "X-Atlas-Report-ID": str(report_id),
            "X-Request-ID": str(_request_id(request)),
        },
    )


@router.get("/{report_id}")
async def get_report(request: Request, report_id: UUID) -> JSONResponse:
    try:
        job = await _service(request).get(report_id, owner_key_hash=_owner(request))
    except ReportNotFound:
        return _problem(request, 404, "Report was not found", "not_found")
    return JSONResponse(status_code=200, content=job.model_dump(mode="json"))


@router.get("/{report_id}/events", response_model=None)
async def report_events(request: Request, report_id: UUID) -> StreamingResponse | JSONResponse:
    try:
        stream = _service(request).stream(report_id, owner_key_hash=_owner(request))
        await _service(request).get(report_id, owner_key_hash=_owner(request))
    except ReportNotFound:
        return _problem(request, 404, "Report was not found", "not_found")
    return StreamingResponse(stream, media_type="text/event-stream")


@router.get("/{report_id}/download", response_model=None)
async def download_report(
    request: Request, report_id: UUID, format: str
) -> Response | JSONResponse:
    try:
        content, _job = await _service(request).download(
            report_id, owner_key_hash=_owner(request), format=format
        )
    except ReportNotFound:
        return _problem(request, 404, "Report artifact was not found", "not_found")
    media_type = (
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        if format == "docx"
        else "application/pdf"
    )
    return Response(
        content=content,
        media_type=media_type,
        headers={
            "Content-Disposition": f'attachment; filename="atlas-report-{report_id}.{format}"'
        },
    )


@router.delete("/{report_id}")
async def delete_report(request: Request, report_id: UUID) -> JSONResponse:
    try:
        job = await _service(request).delete(report_id, owner_key_hash=_owner(request))
    except ReportNotFound:
        return _problem(request, 404, "Report was not found", "not_found")
    return JSONResponse(status_code=200, content=job.model_dump(mode="json"))
