import json
from pathlib import Path

from atlas.providers.prompts.comparison import build_comparison_prompt


def test_comparison_prompt_keeps_source_instructions_untrusted() -> None:
    fixture = Path(__file__).parents[2] / "fixtures" / "security" / "comparison_malicious_source.md"
    source_text = fixture.read_text(encoding="utf-8")

    prompt = build_comparison_prompt(
        question="Compare tool calling support.",
        evidence=[{"technology": "openai", "excerpt": source_text}],
        language="en-US",
    )

    assert "untrusted evidence" in prompt.system_message.lower()
    assert "never authorize tools" in prompt.system_message.lower()
    payload = json.loads(prompt.user_message)
    assert payload["evidence_blocks"][0]["excerpt"] == source_text
    assert prompt.tools == ()
