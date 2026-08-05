"""Structure-aware Markdown chunking with reproducible offsets and hashes."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MarkdownChunk:
    ordinal: int
    heading_path: tuple[str, ...]
    text: str
    text_sha256: str
    token_count: int
    start_offset: int
    end_offset: int
    anchor: str | None = None
    page_start: int = 1
    page_end: int = 1
    language: str = "unknown"
    ocr_used: bool = False
    ocr_confidence: float | None = None


_HEADING = re.compile(r"^(#{1,6})[ \t]+(.+?)\s*$")


def chunk_markdown(
    markdown: str,
    *,
    max_chars: int = 1200,
    source_language: str = "unknown",
    ocr_used: bool = False,
    ocr_confidence: float | None = None,
) -> list[MarkdownChunk]:
    if max_chars <= 0:
        raise ValueError("max_chars must be positive")
    sections = _sections(markdown)
    chunks: list[MarkdownChunk] = []
    for heading_path, section_start, section_end, section_text in sections:
        for text, relative_start, relative_end in _split_section(section_text, max_chars):
            start = section_start + relative_start
            end = min(section_start + relative_end, section_end)
            chunks.append(
                MarkdownChunk(
                    ordinal=len(chunks),
                    heading_path=heading_path,
                    text=text,
                    text_sha256=hashlib.sha256(text.encode("utf-8")).hexdigest(),
                    token_count=len(re.findall(r"\S+", text)),
                    start_offset=start,
                    end_offset=max(end, start + len(text)),
                    page_start=_page_for_offset(markdown, start),
                    page_end=_page_for_offset(markdown, max(end, start + len(text))),
                    language=source_language,
                    ocr_used=ocr_used,
                    ocr_confidence=ocr_confidence,
                )
            )
    return chunks


def _page_for_offset(markdown: str, offset: int) -> int:
    return markdown[:offset].count("\f") + 1


def _sections(markdown: str) -> list[tuple[tuple[str, ...], int, int, str]]:
    lines = markdown.splitlines(keepends=True)
    sections: list[tuple[tuple[str, ...], int, int, str]] = []
    stack: list[str] = []
    section_start = 0
    current_path: tuple[str, ...] = ()
    offset = 0

    for line in lines:
        match = _HEADING.match(line.rstrip("\r\n"))
        if match:
            if markdown[section_start:offset].strip():
                sections.append(
                    (current_path, section_start, offset, markdown[section_start:offset].strip())
                )
            level = len(match.group(1))
            title = match.group(2).strip()
            stack = stack[: level - 1]
            stack.append(title)
            current_path = tuple(stack)
            section_start = offset
        offset += len(line)

    if markdown[section_start:].strip():
        sections.append(
            (current_path, section_start, len(markdown), markdown[section_start:].strip())
        )
    return sections


def _split_section(text: str, max_chars: int) -> list[tuple[str, int, int]]:
    if len(text) <= max_chars:
        return [(text, 0, len(text))]
    paragraphs = [
        paragraph.strip() for paragraph in re.split(r"\n\s*\n", text) if paragraph.strip()
    ]
    result: list[tuple[str, int, int]] = []
    cursor = 0
    for paragraph in paragraphs:
        if len(paragraph) <= max_chars:
            start = text.find(paragraph, cursor)
            result.append((paragraph, max(start, 0), max(start, 0) + len(paragraph)))
            cursor = max(start, 0) + len(paragraph)
            continue
        words = paragraph.split()
        current = ""
        for word in words:
            candidate = f"{current} {word}".strip()
            if current and len(candidate) > max_chars:
                start = text.find(current, cursor)
                result.append((current, max(start, 0), max(start, 0) + len(current)))
                cursor = max(start, 0) + len(current)
                current = word
            else:
                current = candidate
        if current:
            start = text.find(current, cursor)
            result.append((current, max(start, 0), max(start, 0) + len(current)))
            cursor = max(start, 0) + len(current)
    return result
