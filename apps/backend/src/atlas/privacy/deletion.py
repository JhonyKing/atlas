"""Repeat-safe private-resource deletion commands."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from threading import RLock
from uuid import UUID

from atlas.privacy.ownership import InMemoryOwnershipService, ResourceNotFound
from atlas.uploads.pipeline import PrivateUploadPipeline


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


class AccountDeletionService:
    """Coordinate repeat-safe removal of every local resource owned by a subject."""

    def __init__(
        self,
        ownership: InMemoryOwnershipService,
        uploads: PrivateUploadPipeline,
        revoke_subject: Callable[[UUID], int],
    ) -> None:
        self._ownership = ownership
        self._uploads = uploads
        self._revoke_subject = revoke_subject
        self._requests: dict[tuple[UUID, str], bool] = {}
        self._lock = RLock()

    def request(self, owner_id: UUID, idempotency_key: str) -> bool:
        if len(idempotency_key.strip()) < 8:
            raise ValueError("idempotency key is too short")
        key = (owner_id, idempotency_key)
        with self._lock:
            if key in self._requests:
                return False
            self._ownership.delete_all(owner_id)
            self._uploads.delete_owner(owner_id)
            self._revoke_subject(owner_id)
            self._requests[key] = True
            return True
