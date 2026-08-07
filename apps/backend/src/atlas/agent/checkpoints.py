"""Content-safe checkpoint and idempotent replay adapters."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4

from atlas.agent.state import AtlasState


class CheckpointConflict(RuntimeError):
    """Replay key is already bound to a different state."""


class CheckpointUnavailable(RuntimeError):
    """Checkpoint is expired, missing, or corrupted."""


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

    @staticmethod
    def redact_summary(value: dict[str, Any]) -> dict[str, object]:
        secret_words = ("key", "token", "secret", "password", "content", "prompt")
        return {
            key: "[REDACTED]" if any(word in key.casefold() for word in secret_words) else val
            for key, val in value.items()
        }

    def save(self, state: AtlasState, *, node: str, replay_key: str) -> Checkpoint:
        key = (state.thread_id, replay_key)
        safe = self.redact_summary(
            {"request_id": str(state.request_id), "route": state.route.route, "node": node}
        )
        payload = json.dumps(safe, sort_keys=True)
        digest = hashlib.sha256(payload.encode()).hexdigest()
        existing = self._items.get(key)
        if existing is not None and existing.state_hash != digest:
            raise CheckpointConflict("replay key is bound to a different state")
        if existing is not None:
            return existing
        created = self._now()
        checkpoint = Checkpoint(
            uuid4(), state.thread_id, node, replay_key, digest, safe, created, created + self._ttl
        )
        self._items[key] = checkpoint
        return checkpoint

    def resume(self, thread_id: UUID, *, replay_key: str) -> Checkpoint:
        item = self._items.get((thread_id, replay_key))
        if item is None or item.expires_at <= self._now():
            raise CheckpointUnavailable("checkpoint is missing or expired")
        return item
