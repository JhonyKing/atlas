from __future__ import annotations

from uuid import uuid4

import pytest

from atlas.comparison.events import ComparisonEventOrderError, ComparisonEventWriter


def test_comparison_events_are_monotonic_and_terminal() -> None:
    writer = ComparisonEventWriter(run_id=uuid4())
    accepted = writer.emit("comparison.accepted", {"status": "accepted"})
    retrieval = writer.emit("comparison.retrieval.started", {"status": "retrieving"})
    completed = writer.emit(
        "comparison.completed",
        {"status": "completed", "matrix": {"cells": []}},
    )

    assert "id: 1" in accepted
    assert "id: 2" in retrieval
    assert "id: 3" in completed

    with pytest.raises(ComparisonEventOrderError):
        writer.emit("comparison.failed", {"status": "failed"})


def test_progress_event_cannot_publish_cell_content_before_verification() -> None:
    writer = ComparisonEventWriter(run_id=uuid4())
    writer.emit("comparison.accepted", {"status": "accepted"})

    with pytest.raises(ValueError, match="matrix"):
        writer.emit(
            "comparison.retrieval.completed",
            {"status": "retrieving", "matrix": {"cells": []}},
        )


def test_completed_matrix_requires_evidence_for_supported_cells() -> None:
    writer = ComparisonEventWriter(run_id=uuid4())
    writer.emit("comparison.accepted", {"status": "accepted"})
    writer.emit("comparison.retrieval.started", {"status": "retrieving"})
    writer.emit("comparison.retrieval.completed", {"status": "retrieving"})
    writer.emit("comparison.normalization.completed", {"status": "normalizing"})
    writer.emit("comparison.verification.completed", {"status": "verifying"})

    with pytest.raises(ValueError, match="evidence"):
        writer.emit(
            "comparison.completed",
            {
                "status": "completed",
                "matrix": {
                    "cells": [
                        {"state": "supported", "evidence_ids": []},
                    ]
                },
            },
        )
