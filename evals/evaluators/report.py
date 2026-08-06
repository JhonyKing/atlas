"""Deterministic checks for report representation quality."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_report_cases(path: str | Path) -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict) or not value.get("id"):
                raise ValueError("report eval case must be an object with an id")
            cases.append(value)
    if not cases:
        raise ValueError("report eval dataset must not be empty")
    return cases


def evaluate_report(case: dict[str, Any], report: dict[str, Any]) -> bool:
    citations = report.get("citations", [])
    sections = report.get("sections", [])
    citation_ids = {str(item.get("citation_id")) for item in citations if isinstance(item, dict)}
    if not citation_ids or not isinstance(sections, list):
        return False
    required = set(case.get("required_sections", []))
    titles = {str(section.get("title")) for section in sections if isinstance(section, dict)}
    if case.get("locale") == "es-MX" and "Resumen ejecutivo" not in titles:
        return False
    if required and not required.issubset(titles):
        return False
    for section in sections:
        if not isinstance(section, dict) or not section.get("is_factual", True):
            continue
        if not set(map(str, section.get("citation_ids", []))).issubset(citation_ids):
            return False
    return all(
        str(item.get("excerpt", "")).startswith("Original evidence")
        for item in citations
        if isinstance(item, dict)
    )

