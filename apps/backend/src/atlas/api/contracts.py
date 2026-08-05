"""Small registry of versioned public API contracts."""

from __future__ import annotations

COMPARISON_CONTRACT_FILES = {
    "openapi": "specs/002-technology-comparator/contracts/openapi.yaml",
    "events": "specs/002-technology-comparator/contracts/comparison-events.md",
}

COMPARISON_ROUTES = (
    "POST /v1/comparisons",
    "GET /v1/comparisons/{run_id}",
    "DELETE /v1/comparisons/{run_id}",
)

COMPARISON_EVENT_NAMES = (
    "accepted",
    "retrieval",
    "normalization",
    "verification",
    "completed",
    "cancelled",
    "failed",
)
