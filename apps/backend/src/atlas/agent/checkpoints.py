"""Content-safe checkpoint and idempotent replay adapters."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from threading import Lock
from typing import Any, Protocol
from uuid import UUID, uuid4

from atlas.agent.state import AtlasState


class CheckpointConflict(RuntimeError):
    """Replay key is already bound to a different state."""


class CheckpointUnavailable(RuntimeError):
    """Checkpoint is expired, missing, or corrupted."""


class CheckpointRepository(Protocol):
    def save(self, state: AtlasState, *, node: str, replay_key: str) -> Checkpoint: ...

    def resume(self, thread_id: UUID, *, replay_key: str) -> Checkpoint: ...


@dataclass(frozen=True, slots=True)
class Checkpoint:
    checkpoint_id: UUID
    thread_id: UUID
    node: str
    replay_key: str
    state_hash: str
    safe_summary: dict[str, object]
    created_at: datetime
    expires_at: datetime


class InMemoryCheckpointRepository:
    def __init__(self, *, ttl_hours: int = 24, now: Callable[[], datetime] | None = None) -> None:
        self._ttl = timedelta(hours=ttl_hours)
        self._now = now or (lambda: datetime.now(UTC))
        self._items: dict[tuple[UUID, str], Checkpoint] = {}
        self._claimed: set[tuple[UUID, str]] = set()
        self._lock = Lock()

    @staticmethod
    def redact_summary(value: Mapping[str, Any]) -> dict[str, object]:
        secret_words = ("key", "token", "secret", "password", "content", "prompt")
        return {
            key: "[REDACTED]" if any(word in key.casefold() for word in secret_words) else val
            for key, val in value.items()
        }

    def save(self, state: AtlasState, *, node: str, replay_key: str) -> Checkpoint:
        key = (state.thread_id, replay_key)
        safe = self.redact_summary(
            {
                "request_id": str(state.request_id),
                "thread_id": str(state.thread_id),
                "route": state.route.route,
                "node": node,
                "state_version": state.state_version,
            }
        )
        payload = json.dumps(safe, sort_keys=True)
        digest = hashlib.sha256(payload.encode()).hexdigest()
        with self._lock:
            existing = self._items.get(key)
            if existing is not None and existing.state_hash != digest:
                raise CheckpointConflict("replay key is bound to a different state")
            if existing is not None:
                return existing
            created = self._now()
            checkpoint = Checkpoint(
                uuid4(),
                state.thread_id,
                node,
                replay_key,
                digest,
                safe,
                created,
                created + self._ttl,
            )
            self._items[key] = checkpoint
            return checkpoint

    def resume(self, thread_id: UUID, *, replay_key: str) -> Checkpoint:
        item = self._items.get((thread_id, replay_key))
        if item is None or item.expires_at <= self._now():
            raise CheckpointUnavailable("checkpoint is missing or expired")
        expected = hashlib.sha256(
            json.dumps(item.safe_summary, sort_keys=True).encode()
        ).hexdigest()
        if expected != item.state_hash:
            raise CheckpointUnavailable("checkpoint integrity check failed")
        return item

    def claim_resume(self, thread_id: UUID, *, replay_key: str) -> bool:
        """Claim a replay once; duplicate workers must skip the side effect."""

        key = (thread_id, replay_key)
        with self._lock:
            if key in self._claimed:
                return False
            self.resume(thread_id, replay_key=replay_key)
            self._claimed.add(key)
            return True
