"""Public corpus snapshot and freshness status endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from atlas.observability.context import current_request_id
from atlas.persistence.corpus_status import CorpusUnavailableError

router = APIRouter(prefix="/v1/corpus", tags=["Corpus"])


def _problem(request: Request, *, detail: str) -> JSONResponse:
    request_id = str(current_request_id())
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "type": "about:blank",
            "title": "Corpus unavailable",
            "status": status.HTTP_503_SERVICE_UNAVAILABLE,
            "detail": detail,
            "request_id": request_id,
            "error_code": "corpus_unavailable",
        },
        headers={"Cache-Control": "no-store"},
    )


@router.get("")
def get_corpus_status(request: Request) -> JSONResponse:
    provider = request.app.state.corpus_service
    if provider is None:
        return _problem(request, detail="ATLAS corpus status is temporarily unavailable.")
    try:
        payload = provider.get_status()
    except CorpusUnavailableError:
        return _problem(request, detail="ATLAS corpus status is temporarily unavailable.")
    if payload is None:
        return _problem(request, detail="ATLAS corpus status is temporarily unavailable.")
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=payload.model_dump(mode="json"),
        headers={"Cache-Control": "no-store"},
    )
