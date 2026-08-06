"""Previous-day news selection primitives."""

from atlas.news.feeds import FeedError, parse_feed
from atlas.news.fetch import FeedPolicy, NewsFeedFetcher
from atlas.news.ranking import InMemoryDailyNewsService, select_previous_day
from atlas.news.runtime import LiveDailyNewsService
from atlas.news.scheduler import DailyNewsRefreshService, InMemoryDailyNewsSelectionStore
from atlas.news.schemas import NewsCandidate, NewsSelection

__all__ = [
    "DailyNewsRefreshService",
    "FeedError",
    "FeedPolicy",
    "InMemoryDailyNewsSelectionStore",
    "InMemoryDailyNewsService",
    "LiveDailyNewsService",
    "NewsCandidate",
    "NewsFeedFetcher",
    "NewsSelection",
    "parse_feed",
    "select_previous_day",
]
