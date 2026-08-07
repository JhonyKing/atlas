"""Compatibility module for the governed connector registry.

The registry implementation lives beside the connector contracts so existing
ingestion imports remain stable.  This module provides the explicit path used
by Feature 005 documentation and callers.
"""

from atlas.ingestion.connectors import (
    ConnectorDisabled,
    ConnectorRegistry,
    SourceCandidate,
    SourceConnector,
    SourceReview,
)

__all__ = [
    "ConnectorDisabled",
    "ConnectorRegistry",
    "SourceCandidate",
    "SourceConnector",
    "SourceReview",
]
