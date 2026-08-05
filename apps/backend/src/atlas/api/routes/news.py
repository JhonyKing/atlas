"""Public, attributed previous-day news endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Request

from atlas.news.ranking import DailyNewsProvider, unavailable_news
from atlas.news.schemas import NewsSelection

router = APIRouter(prefix="/v1/news", tags=["News"])


@router.get("/daily", response_model=NewsSelection)
def daily_news(request: Request) -> NewsSelection:
    provider = getattr(request.app.state, "news_service", None)
    if provider is None:
        return unavailable_news()
    return provider.get_daily()


__all__ = ["DailyNewsProvider", "router"]

