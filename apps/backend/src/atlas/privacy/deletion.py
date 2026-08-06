"""Repeat-safe private-resource deletion commands."""

from __future__ import annotations

import hashlib
from threading import RLock
from uuid import UUID

from atlas.privacy.ownership import InMemoryOwnershipService, ResourceNotFound


class DeletionIdempotencyConflict(ValueError):
    """One idempotency key was reused for a different deletion request."""


class IdempotentDeletionService:
    """Apply a deletion at most once for one owner/key/fingerprint tuple."""

    def __init__(self, ownership: InMemoryOwnershipService) -> None:
        self._ownership = ownership
        self._requests: dict[tuple[UUID, str], str] = {}
        self._lock = RLock()

    def request(self, owner_id: UUID, resource_id: UUID, idempotency_key: str) -> bool:
        if len(idempotency_key.strip()) < 8:
            raise ValueError("idempotency key is too short")
        key = (owner_id, idempotency_key)
        fingerprint = hashlib.sha256(str(resource_id).encode("ascii")).hexdigest()
        with self._lock:
            previous = self._requests.get(key)
            if previous is not None:
                if previous != fingerprint:
                    raise DeletionIdempotencyConflict
                return False
            self._requests[key] = fingerprint
            try:
                return self._ownership.delete_owned(owner_id, resource_id)
            except ResourceNotFound:
                self._requests.pop(key, None)
                raise
