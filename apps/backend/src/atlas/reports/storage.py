"""Bounded local artifact storage for the first report slice."""

from __future__ import annotations

import hashlib
from pathlib import Path
from threading import RLock
from uuid import UUID


class LocalArtifactStorage:
    def __init__(self, root: Path | None = None, *, max_bytes: int = 10_000_000) -> None:
        self.root = (root or Path(".atlas-artifacts")).resolve()
        self.max_bytes = max_bytes
        self._lock = RLock()

    def put(self, report_id: UUID, suffix: str, content: bytes) -> tuple[str, int, str]:
        if suffix not in {"docx", "pdf"}:
            raise ValueError("unsupported artifact format")
        if not content or len(content) > self.max_bytes:
            raise ValueError("artifact size is outside the allowed bound")
        digest = hashlib.sha256(content).hexdigest()
        target = (self.root / f"{report_id}.{suffix}").resolve()
        if self.root not in target.parents:
            raise ValueError("unsafe artifact path")
        with self._lock:
            self.root.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        return str(target), len(content), digest

    def get(self, path: str) -> bytes:
        target = Path(path).resolve()
        if self.root not in target.parents:
            raise FileNotFoundError(path)
        return target.read_bytes()

    def delete(self, path: str) -> None:
        target = Path(path).resolve()
        if self.root not in target.parents:
            raise FileNotFoundError(path)
        try:
            target.unlink()
        except FileNotFoundError:
            return
