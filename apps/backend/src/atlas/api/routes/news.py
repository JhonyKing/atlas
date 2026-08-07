"""Public, attributed previous-day news endpoint."""

from __future__ import annotations

from time import monotonic
from uuid import uuid4

from fastapi import APIRouter, Request

from atlas.news.observability import news_observation
from atlas.news.ranking import DailyNewsProvider, unavailable_news
from atlas.news.schemas import NewsSelection
from atlas.observability.context import current_request_id
from atlas.observability.langsmith import NullTraceSink, TraceSink

router = APIRouter(prefix="/v1/news", tags=["News"])


@router.get("/daily", response_model=NewsSelection)
def daily_news(request: Request) -> NewsSelection:
    provider = getattr(request.app.state, "news_service", None)
    sink: TraceSink = getattr(request.app.state, "news_trace_sink", None) or NullTraceSink()
    request_id = current_request_id() or uuid4()
    run_id = uuid4()
    started = monotonic()
    handle = sink.start(
        "atlas.news.daily",
        request_id=request_id,
        run_id=run_id,
        fields={"locale": request.headers.get("accept-language", "en-US").split(",", 1)[0]},
        tags=("news", "daily"),
    )
    try:
        selection = unavailable_news() if provider is None else provider.get_daily()
        sink.end(
            handle,
            status=selection.status,
            fields=news_observation(selection, latency_ms=(monotonic() - started) * 1000),
        )
        return selection
    except Exception:
        selection = unavailable_news(reason_code="no_evidence")
        sink.end(
            handle,
            status="failed",
            fields=news_observation(selection, latency_ms=(monotonic() - started) * 1000),
        )
        return selection


__all__ = ["DailyNewsProvider", "router"]
