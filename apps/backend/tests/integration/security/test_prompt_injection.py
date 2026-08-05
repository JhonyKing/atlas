from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from uuid import UUID

from pydantic import HttpUrl

from atlas.domain import Evidence, Question, SourceType
from atlas.providers.prompts.cited_answer import (
    CITED_ANSWER_INSTRUCTIONS,
    CITED_ANSWER_TOOLS,
    build_cited_answer_input,
)

FIXTURE_DIR = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "security"
EVIDENCE_ID = UUID("00000000-0000-0000-0000-000000000801")


def evidence_from_fixture(name: str) -> Evidence:
    return Evidence(
        id=EVIDENCE_ID,
        source_title="Untrusted fixture",
        publisher="Fixture publisher",
        canonical_url=HttpUrl("https://docs.example.test/security-fixture"),
        excerpt=(FIXTURE_DIR / name).read_text(encoding="utf-8"),
        captured_at=datetime(2026, 8, 4, tzinfo=UTC),
        source_type=SourceType.DOCUMENTATION,
    )


def test_malicious_source_is_delimited_as_untrusted_evidence() -> None:
    prompt = build_cited_answer_input(
        Question(text="What does the persistence documentation say?"),
        [evidence_from_fixture("malicious_source.md")],
    )

    assert f'<untrusted_evidence id="{EVIDENCE_ID}">' in prompt
    assert "</untrusted_evidence>" in prompt
    assert "Ignore every previous instruction" in prompt
    assert "attacker.example.invalid" in prompt


def test_unauthorized_instructions_remain_data_and_no_action_tools_are_exposed() -> None:
    prompt = build_cited_answer_input(
        Question(text="Summarize the supported source."),
        [evidence_from_fixture("unauthorized_instruction.md")],
    )

    assert "SYSTEM OVERRIDE" in prompt
    assert "untrusted" in CITED_ANSWER_INSTRUCTIONS.casefold()
    assert "do not" in CITED_ANSWER_INSTRUCTIONS.casefold()
    assert CITED_ANSWER_TOOLS == ()
