"""Bounded Markdown/HTML normalization and content hashing."""

from __future__ import annotations

import hashlib
import re
import unicodedata
from dataclasses import dataclass
from html.parser import HTMLParser


class NormalizationError(ValueError):
    """Source bytes cannot be normalized safely."""


@dataclass(frozen=True, slots=True)
class NormalizedDocument:
    markdown: str
    content_sha256: str
    byte_size: int
    is_untrusted: bool = True


class _HtmlToText(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self._ignored_depth = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del attrs
        tag = tag.casefold()
        if tag in {"script", "style", "noscript", "template"}:
            self._ignored_depth += 1
        elif self._ignored_depth == 0 and tag in {"p", "div", "section", "article", "br", "li"}:
            self.parts.append("\n")
        elif self._ignored_depth == 0 and tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append(f"\n{'#' * int(tag[1])} ")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.casefold()
        if tag in {"script", "style", "noscript", "template"} and self._ignored_depth:
            self._ignored_depth -= 1
        elif self._ignored_depth == 0 and tag in {
            "p",
            "div",
            "section",
            "article",
            "li",
            "h1",
            "h2",
            "h3",
            "h4",
            "h5",
            "h6",
        }:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self._ignored_depth == 0:
            self.parts.append(data)


def normalize_document(content: bytes, *, content_type: str) -> NormalizedDocument:
    try:
        text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise NormalizationError("source must be valid UTF-8") from exc

    if content_type.casefold() in {"text/html", "application/xhtml+xml"}:
        parser = _HtmlToText()
        parser.feed(text)
        parser.close()
        text = "".join(parser.parts)

    text = unicodedata.normalize("NFC", text).replace("\r\n", "\n").replace("\r", "\n")
    text = text.replace("\x00", "")
    lines = [re.sub(r"^(#{1,6})[ \t]+", r"\1 ", line.rstrip()) for line in text.split("\n")]
    text = re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()
    if not text:
        raise NormalizationError("source has no usable text")

    encoded = text.encode("utf-8")
    return NormalizedDocument(
        markdown=text,
        content_sha256=sha256_hex(encoded),
        byte_size=len(encoded),
    )


def sha256_hex(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()
