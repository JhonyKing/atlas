"""Repeat-safe upload deletion and retention cleanup."""

from __future__ import annotations

from datetime import UTC, datetime
from threading import RLock
from uuid import UUID

from atlas.uploads.pipeline import PrivateUploadPipeline


class UploadDeletionService:
    def __init__(self, pipeline: PrivateUploadPipeline) -> None:
        self._pipeline = pipeline
        self._requests: set[tuple[UUID, UUID, str]] = set()
        self._lock = RLock()

    def delete(self, owner_id: UUID, upload_id: UUID, idempotency_key: str) -> bool:
        key = (owner_id, upload_id, idempotency_key)
        with self._lock:
            if key in self._requests:
                return False
            self._pipeline.delete(owner_id, upload_id)
            self._requests.add(key)
            return True

    def purge_expired(self, *, now: datetime | None = None) -> int:
        observed = (now or datetime.now(UTC)).astimezone(UTC)
        removed = 0
        for record in self._pipeline.records():
            if record.retention_until <= observed:
                self._pipeline.delete(record.owner_id, record.upload_id)
                removed += 1
        return removed
