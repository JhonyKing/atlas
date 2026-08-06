"""Preserve the anonymous quota key across optional authentication."""

from __future__ import annotations


def quota_identity_for_request(visitor_key_hash: str, authenticated_subject: str | None) -> str:
    """Authentication never replaces the existing anonymous HMAC quota identity."""

    del authenticated_subject
    if len(visitor_key_hash) != 64:
        raise ValueError("visitor key hash must be a SHA-256 hex digest")
    return visitor_key_hash
