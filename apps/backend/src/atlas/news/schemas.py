"""Safe public schemas for attributed news metadata."""

from __future__ import annotations

from datetime import UTC, date, datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator


class NewsCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=1, max_length=300)
    summary: str = Field(default="", max_length=4000)
    publisher: str = Field(min_length=1, max_length=160)
    canonical_url: HttpUrl
    published_at: datetime
    captured_at: datetime
    authority_score: float = Field(ge=0, le=1)
    topic_score: float = Field(ge=0, le=1)
    corroboration_count: int = Field(default=1, ge=1, le=100)
    content_sha256: str = Field(min_length=64, max_length=64)

    @field_validator("published_at", "captured_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("news timestamps must include a timezone")
        return value.astimezone(UTC)


class NewsSelection(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ready", "unavailable"]
    day: date
    timezone: Literal["UTC"] = "UTC"
    candidate: NewsCandidate | None = None
    candidate_count: int = Field(default=0, ge=0)
    score: float | None = Field(default=None, ge=0, le=1)
    reason_code: Literal["none", "not_configured", "no_evidence", "insufficient_signal"] = "none"

