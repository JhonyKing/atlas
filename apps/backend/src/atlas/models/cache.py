"""Tenant-safe versioned cache/evidence-pack keys."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256


@dataclass(frozen=True, slots=True)
class CacheKey:
    tenant_scope: str
    corpus_version: str
    retrieval_version: str
    prompt_version: str
    model_version: str
    embedding_version: str
    question_hash: str

    def as_string(self) -> str:
        return ":".join(
            (
                "atlas",
                self.tenant_scope,
                self.corpus_version,
                self.retrieval_version,
                self.prompt_version,
                self.model_version,
                self.embedding_version,
                self.question_hash,
            )
        )


def make_cache_key(
    question: str,
    *,
    tenant_scope: str,
    corpus_version: str,
    retrieval_version: str,
    prompt_version: str,
    model_version: str,
    embedding_version: str,
) -> CacheKey:
    question_hash = sha256(question.strip().encode("utf-8")).hexdigest()[:24]
    return CacheKey(
        tenant_scope,
        corpus_version,
        retrieval_version,
        prompt_version,
        model_version,
        embedding_version,
        question_hash,
    )
