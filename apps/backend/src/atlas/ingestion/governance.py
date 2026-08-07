"""Deterministic governance state machine for curated ingestion."""

from __future__ import annotations

import hashlib
from collections.abc import Callable, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any, Protocol, cast
from urllib.parse import urlparse
from uuid import UUID, uuid4

from atlas.observability.events import ingestion_event


class PolicyState(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    DISABLED = "disabled"
    TAKEDOWN = "takedown"


class GovernanceError(RuntimeError):
    """A source or collection violates an ingestion governance rule."""


class CollectionDefinition(Protocol):
    @property
    def slug(self) -> str: ...

    @property
    def display_name(self) -> str: ...

    @property
    def kind(self) -> str: ...

    @property
    def allowed_hosts(self) -> frozenset[str]: ...

    @property
    def allowed_paths(self) -> tuple[str, ...]: ...

    @property
    def ttl_hours(self) -> int: ...

    @property
    def policy_state(self) -> PolicyState: ...

    @property
    def robots_status(self) -> str: ...

    @property
    def terms_status(self) -> str: ...

    @property
    def license_status(self) -> str: ...


@dataclass(frozen=True, slots=True)
class GovernedSource:
    source_id: UUID
    collection_slug: str
    canonical_url: str
    title: str
    author_or_org: str | None
    license: str | None
    published_at: datetime | None
    captured_at: datetime
    content_sha256: str
    current_version_id: UUID
    state: str = "current"
    last_update_outcome: str = "new"
    private_owner_id: UUID | None = None


@dataclass(frozen=True, slots=True)
class SourceVersion:
    version_id: UUID
    source_id: UUID
    parent_version_id: UUID | None
    normalized_markdown: str
    content_sha256: str
    captured_at: datetime
    version_label: str | None = None
    status: str = "active"


@dataclass(frozen=True, slots=True)
class CaptureResult:
    source: GovernedSource
    version: SourceVersion
    outcome: str


@dataclass(frozen=True, slots=True)
class ConnectorRun:
    run_id: UUID
    collection_slug: str
    trigger: str
    max_attempts: int
    attempt_count: int = 0
    status: str = "running"
    error_code: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class CoverageSnapshot:
    captured_at: datetime
    collection_count: int
    collections: list[dict[str, object]]
    dead_letter_count: int = 0
    window_days: int = 7
    target_met: bool = True


class InMemoryGovernanceRepository:
    """Reference implementation used by deterministic tests and local operator mode."""

    def __init__(
        self,
        catalog: Sequence[CollectionDefinition],
        *,
        now: Callable[[], datetime] | None = None,
    ) -> None:
        self._catalog = list(catalog)
        self._clock = now or (lambda: datetime.now(UTC))
        self._sources: dict[tuple[str, str], GovernedSource] = {}
        self._versions: dict[UUID, list[SourceVersion]] = {}
        self._runs: dict[UUID, ConnectorRun] = {}
        self._run_max_attempts: dict[UUID, int] = {}
        self._events: list[dict[str, Any]] = []

    def catalog(self) -> list[CollectionDefinition]:
        return list(self._catalog)

    def _collection(self, slug: str) -> CollectionDefinition:
        for item in self._catalog:
            if item.slug == slug:
                return item
        raise GovernanceError("unknown governed collection")

    def _validate_destination(self, collection: CollectionDefinition, url: str) -> None:
        parsed = urlparse(url)
        if parsed.scheme != "https" or not parsed.hostname:
            raise GovernanceError("source URL must use HTTPS")
        host = parsed.hostname.casefold().rstrip(".")
        allowed_hosts = {value.casefold().rstrip(".") for value in collection.allowed_hosts}
        if host not in allowed_hosts:
            raise GovernanceError("source URL host is outside the allowlist")
        path = parsed.path or "/"
        if not any(path.startswith(prefix) for prefix in collection.allowed_paths):
            raise GovernanceError("source URL path is outside the allowlist")

    def validate_destination(self, collection: str, url: str) -> None:
        """Validate a candidate before any network client is allowed to fetch it."""

        self._validate_destination(self._collection(collection), url)

    def plan_discovery(self, collection: str, candidates: Sequence[str]) -> list[str]:
        """Return only bounded, approved candidates; rejected URLs are never fetched."""

        definition = self._collection(collection)
        if definition.policy_state != PolicyState.APPROVED:
            raise GovernanceError("source requires approved policy review")
        approved: list[str] = []
        for candidate in candidates:
            try:
                self._validate_destination(definition, candidate)
            except GovernanceError:
                continue
            if candidate not in approved:
                approved.append(candidate)
        return approved

    def capture(
        self,
        *,
        collection: str,
        url: str,
        title: str,
        normalized_markdown: str,
        content_sha256: str | None = None,
        author_or_org: str | None = None,
        license: str | None = None,
        published_at: datetime | None = None,
        captured_at: datetime | None = None,
        version_label: str | None = None,
        private_owner_id: UUID | None = None,
    ) -> CaptureResult:
        definition = self._collection(collection)
        if definition.policy_state != PolicyState.APPROVED:
            raise GovernanceError("source requires approved policy review")
        self._validate_destination(definition, url)
        observed = (captured_at or self._clock()).astimezone(UTC)
        digest = content_sha256 or hashlib.sha256(normalized_markdown.encode("utf-8")).hexdigest()
        if len(digest) != 64:
            raise GovernanceError("content hash must be SHA-256")
        key = (collection, url)
        previous = self._sources.get(key)
        if previous is not None and previous.content_sha256 == digest:
            refreshed = replace(
                previous,
                captured_at=observed,
                state="current",
                last_update_outcome="unchanged",
            )
            self._sources[key] = refreshed
            return CaptureResult(refreshed, self.current_version(previous.source_id), "unchanged")
        parent = previous.current_version_id if previous is not None else None
        if previous is not None:
            old_version = self.current_version(previous.source_id)
            self._replace_version(old_version, status="superseded")
        source_id = previous.source_id if previous is not None else uuid4()
        version = SourceVersion(
            version_id=uuid4(),
            source_id=source_id,
            parent_version_id=parent,
            normalized_markdown=normalized_markdown,
            content_sha256=digest,
            captured_at=observed,
            version_label=version_label,
        )
        source = GovernedSource(
            source_id=source_id,
            collection_slug=collection,
            canonical_url=url,
            title=title,
            author_or_org=author_or_org,
            license=license,
            published_at=published_at,
            captured_at=observed,
            content_sha256=digest,
            current_version_id=version.version_id,
            state=(
                "stale"
                if observed + timedelta(hours=definition.ttl_hours) < self._clock()
                else "current"
            ),
            last_update_outcome="changed" if previous is not None else "new",
            private_owner_id=private_owner_id,
        )
        self._sources[key] = source
        self._versions.setdefault(source_id, []).append(version)
        return CaptureResult(source, version, source.last_update_outcome)

    def _replace_version(self, version: SourceVersion, *, status: str) -> None:
        versions = self._versions.get(version.source_id, [])
        self._versions[version.source_id] = [
            replace(item, status=status) if item.version_id == version.version_id else item
            for item in versions
        ]

    def current_version(self, source_id: UUID) -> SourceVersion:
        for version in self._versions.get(source_id, []):
            source = next(
                (item for item in self._sources.values() if item.source_id == source_id),
                None,
            )
            if source is not None and version.version_id == source.current_version_id:
                return version
        raise GovernanceError("source version not found")

    def versions(self, source_id: UUID) -> list[SourceVersion]:
        return list(self._versions.get(source_id, []))

    def source(self, source_id: UUID) -> GovernedSource:
        for item in self._sources.values():
            if item.source_id == source_id:
                return item
        raise GovernanceError("source not found")

    def set_policy(self, collection: str, state: PolicyState, *, reason: str) -> None:
        del reason
        definition = self._collection(collection)
        index = self._catalog.index(definition)
        self._catalog[index] = cast(
            CollectionDefinition,
            replace(cast(Any, definition), policy_state=state),
        )
        if state in {PolicyState.DISABLED, PolicyState.TAKEDOWN}:
            for key, source in list(self._sources.items()):
                if source.collection_slug == collection:
                    self._sources[key] = replace(source, state="disabled")

    def enable_collection(self, collection: str) -> None:
        definition = self._collection(collection)
        if definition.policy_state != PolicyState.APPROVED:
            raise GovernanceError("collection must have approved policy review")
        if any(
            getattr(definition, field, "pending") != "approved"
            for field in ("robots_status", "terms_status", "license_status")
        ):
            raise GovernanceError("robots, terms, and license review must be approved")

    def review_collection(
        self,
        collection: str,
        *,
        robots_status: str,
        terms_status: str,
        license_status: str,
        reviewer: str,
    ) -> None:
        """Record an explicit human review before a collection can be enabled."""

        if not reviewer.strip():
            raise GovernanceError("reviewer is required")
        statuses = (robots_status, terms_status, license_status)
        if any(value not in {"approved", "rejected", "pending"} for value in statuses):
            raise GovernanceError("review states are invalid")
        definition = self._collection(collection)
        index = self._catalog.index(definition)
        self._catalog[index] = cast(
            CollectionDefinition,
            replace(
                cast(Any, definition),
                robots_status=robots_status,
                terms_status=terms_status,
                license_status=license_status,
                reviewer=reviewer,
                reviewed_at=self._clock().date().isoformat(),
            ),
        )

    def disable_collection(self, collection: str, *, reason: str) -> None:
        self.set_policy(collection, PolicyState.DISABLED, reason=reason)

    def takedown(self, source_id: UUID, *, reason: str) -> None:
        del reason
        source = self.source(source_id)
        self._sources[(source.collection_slug, source.canonical_url)] = replace(
            source,
            state="disabled",
        )

    def start_run(self, collection: str, *, trigger: str, max_attempts: int = 3) -> ConnectorRun:
        self._collection(collection)
        run = ConnectorRun(uuid4(), collection, trigger, max_attempts, started_at=self._clock())
        self._runs[run.run_id] = run
        self._run_max_attempts[run.run_id] = max_attempts
        return run

    def fail_run(self, run_id: UUID, error_code: str) -> ConnectorRun:
        run = self._runs[run_id]
        attempt = run.attempt_count + 1
        status = "dead_letter" if attempt >= run.max_attempts else "retrying"
        updated = replace(run, attempt_count=attempt, status=status, error_code=error_code)
        self._runs[run_id] = updated
        started = run.started_at or self._clock()
        self._events.append(
            ingestion_event(
                run_id=run_id,
                collection=run.collection_slug,
                outcome=status,
                latency_ms=(self._clock() - started).total_seconds() * 1000,
                error_code=error_code,
            )
        )
        return updated

    def complete_run(self, run_id: UUID) -> ConnectorRun:
        """Close a successful run and emit the same safe operational envelope."""

        run = self._runs[run_id]
        completed_at = self._clock()
        updated = replace(run, status="succeeded", completed_at=completed_at)
        self._runs[run_id] = updated
        started = run.started_at or completed_at
        self._events.append(
            ingestion_event(
                run_id=run_id,
                collection=run.collection_slug,
                outcome="succeeded",
                latency_ms=(completed_at - started).total_seconds() * 1000,
            )
        )
        return updated

    def run(self, run_id: UUID) -> ConnectorRun:
        return self._runs[run_id]

    def events(self) -> list[dict[str, Any]]:
        """Return redacted operational events for local verification dashboards."""

        return list(self._events)

    def coverage(self) -> CoverageSnapshot:
        observed = self._clock().astimezone(UTC)
        rows: list[dict[str, object]] = []
        for definition in self._catalog:
            sources = [
                item for item in self._sources.values() if item.collection_slug == definition.slug
            ]
            retry_count = sum(
                run.collection_slug == definition.slug and run.status == "retrying"
                for run in self._runs.values()
            )
            dead_letter_count = sum(
                run.collection_slug == definition.slug and run.status == "dead_letter"
                for run in self._runs.values()
            )
            rows.append(
                {
                    "slug": definition.slug,
                    "display_name": definition.display_name,
                    "kind": definition.kind,
                    "policy_state": definition.policy_state.value,
                    "enabled": definition.policy_state == PolicyState.APPROVED,
                    "source_count": len(sources),
                    "stale_count": sum(item.state == "stale" for item in sources),
                    "disabled_count": sum(item.state == "disabled" for item in sources),
                    "retry_count": retry_count,
                    "dead_letter_count": dead_letter_count,
                }
            )
        return CoverageSnapshot(
            captured_at=observed,
            collection_count=len(rows),
            collections=rows,
            dead_letter_count=sum(run.status == "dead_letter" for run in self._runs.values()),
            target_met=all(
                item["dead_letter_count"] == 0 and item["stale_count"] == 0 for item in rows
            ),
        )
