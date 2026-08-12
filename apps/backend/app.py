"""Vercel Python runtime entrypoint for the ATLAS API beta."""

from atlas.api.main import app

__all__ = ["app"]
