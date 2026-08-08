"""Secret-safe, schema-compatible evidence models for Supabase migration runs."""

from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

PROJECT_REF = "fcbclsaytbjpywlaplbh"

_SECRET_KEY_PATTERN = re.compile(
    r"(?:api[_-]?key|password|secret|token|authorization|service[_-]?role)", re.I
)
_SECRET_VALUE_PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{12,}\b"),
    re.compile(r"\bBearer\s+[A-Za-z0-9._-]{12,}\b", re.I),
    re.compile(r"postgres(?:ql)?://[^\s]+:[^\s@]+@", re.I),
)


def _contains_secret(value: object, *, key: str | None = None) -> bool:
    if key is not None and _SECRET_KEY_PATTERN.search(key):
        return True
    if isinstance(value, str):
        return any(pattern.search(value) is not None for pattern in _SECRET_VALUE_PATTERNS)
    if isinstance(value, list):
        return any(_contains_secret(item) for item in value)
    if isinstance(value, dict):
        return any(_contains_secret(item, key=item_key) for item_key, item in value.items())
    return False


class MigrationCheck(BaseModel):
    """One bounded, content-free verification check."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1)
    status: str = Field(pattern=r"^(passed|failed|blocked|skipped)$")
    elapsed_ms: float | None = Field(default=None, ge=0)
    detail: str | None = Field(default=None, max_length=1000)


class DriftFinding(BaseModel):
    """One non-secret difference between repository and remote state."""

    model_config = ConfigDict(extra="forbid")

    kind: str = Field(pattern=r"^(revision|table|function|index|policy|extension|seed)$")
    object_name: str = Field(min_length=1)
    expected: str
    actual: str
    severity: str = Field(pattern=r"^(blocking|warning|informational)$")
    resolution: str | None = Field(default=None, max_length=1000)


class MigrationEvidence(BaseModel):
    """Top-level migration artifact that can safely be committed to the repository."""

    model_config = ConfigDict(extra="forbid")

    run_id: str = Field(min_length=1)
    project_ref: str = Field(default=PROJECT_REF, pattern=r"^[a-z0-9]{20}$")
    environment: str = Field(pattern=r"^(development|staging|production|unknown)$")
    mode: str = Field(pattern=r"^(inspect|apply|verify)$")
    started_at: datetime
    finished_at: datetime
    repository_head: str | None = None
    repository_revisions: list[str] = Field(default_factory=list)
    remote_revisions: list[str] = Field(default_factory=list)
    applied_revisions: list[str] = Field(default_factory=list)
    schema_inventory: dict[str, object] = Field(default_factory=dict)
    checks: list[MigrationCheck] = Field(default_factory=list)
    drift: list[DriftFinding] = Field(default_factory=list)
    status: str = Field(pattern=r"^(passed|failed|blocked|drift_detected)$")

    @field_validator("project_ref")
    @classmethod
    def require_project_ref(cls, value: str) -> str:
        if value != PROJECT_REF:
            raise ValueError(f"Evidence must target project {PROJECT_REF}")
        return value

    @field_validator("finished_at")
    @classmethod
    def finish_after_start(cls, value: datetime, info: object) -> datetime:
        start = getattr(info, "data", {}).get("started_at")
        if isinstance(start, datetime) and value < start:
            raise ValueError("finished_at must not precede started_at")
        return value

    @field_validator("schema_inventory")
    @classmethod
    def reject_secrets(cls, value: dict[str, object]) -> dict[str, object]:
        if _contains_secret(value):
            raise ValueError("Evidence schema_inventory must not contain credentials or tokens")
        return value

    @field_validator(
        "repository_head", "repository_revisions", "remote_revisions", "applied_revisions"
    )
    @classmethod
    def reject_secret_strings(cls, value: object) -> object:
        if _contains_secret(value if isinstance(value, (str, list, dict)) else None):
            raise ValueError("Evidence revision fields must not contain credentials or tokens")
        return value
