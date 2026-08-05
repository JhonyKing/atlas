from __future__ import annotations

import json

import pytest

from atlas.api.answer_events import SSEEventWriter


def test_progress_events_are_sequenced_and_content_free() -> None:
    writer = SSEEventWriter()

    first = writer.emit("run.accepted", {"stage": "accepted", "remaining": 9})
    second = writer.emit("retrieval.completed", {"candidate_count": 20})

    assert first.startswith("id: 1\nevent: run.accepted\n")
    assert second.startswith("id: 2\nevent: retrieval.completed\n")
    assert '"candidate_count":20' in second


def test_progress_rejects_draft_claims_and_source_content() -> None:
    writer = SSEEventWriter()

    with pytest.raises(ValueError, match="forbidden content"):
        writer.emit("retrieval.completed", {"claims": [{"text": "draft"}]})
    with pytest.raises(ValueError, match="forbidden content"):
        writer.emit("retrieval.completed", {"canonical_url": "https://example.test"})


def test_terminal_event_may_contain_verified_claims() -> None:
    writer = SSEEventWriter()

    frame = writer.emit(
        "answer.completed",
        {"claims": [{"text": "verified"}], "citations": []},
    )

    payload = json.loads(frame.split("data: ", 1)[1])
    assert payload["claims"][0]["text"] == "verified"
