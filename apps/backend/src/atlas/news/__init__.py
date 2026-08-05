"""Previous-day news selection primitives."""

from atlas.news.feeds import FeedError, parse_feed
from atlas.news.ranking import InMemoryDailyNewsService, select_previous_day
from atlas.news.schemas import NewsCandidate, NewsSelection

__all__ = [
    "FeedError",
    "InMemoryDailyNewsService",
    "NewsCandidate",
    "NewsSelection",
    "parse_feed",
    "select_previous_day",
]

