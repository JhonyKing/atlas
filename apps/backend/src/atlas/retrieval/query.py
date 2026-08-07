"""Provider-independent query preparation and retrieval filters."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from atlas.domain import CollectionSlug, SourceType

MAX_REWRITE_TERMS = 12
MAX_TERM_LENGTH = 80


@dataclass(frozen=True, slots=True)
class RetrievalFilters:
    """Filters applied before ranking; values are data, never destinations."""

    provider: str | None = None
    framework: str | None = None
    version: str | None = None
    date_from: date | None = None
    date_to: date | None = None
    language: str | None = None
    source_type: SourceType | None = None
    collection: CollectionSlug | None = None

    def as_metadata(self) -> dict[str, str]:
        values = {
            "provider": self.provider,
            "framework": self.framework,
            "version": self.version,
            "date_from": self.date_from.isoformat() if self.date_from else None,
            "date_to": self.date_to.isoformat() if self.date_to else None,
            "language": self.language,
            "source_type": str(self.source_type) if self.source_type else None,
            "collection": str(self.collection) if self.collection else None,
        }
        return {key: value for key, value in values.items() if value is not None}


@dataclass(frozen=True, slots=True)
class QueryRewrite:
    """Original query plus deterministic, bounded expansion terms."""

    original: str
    terms: tuple[str, ...] = field(default_factory=tuple)
    language: str = "en-US"

    @property
    def search_text(self) -> str:
        return " ".join((self.original, *self.terms))


def resolve_embedding_profile(
    language: str,
    available_profiles: set[str],
    *,
    baseline_profile: str = "baseline-multilingual",
) -> tuple[str, bool]:
    """Select a language profile or explicitly fall back to the safe baseline."""

    preferred = f"{baseline_profile}:{language}"
    if preferred in available_profiles:
        return preferred, False
    return baseline_profile, True


def build_query_rewrite(
    text: str,
    *,
    language: str = "en-US",
    aliases: dict[str, tuple[str, ...]] | None = None,
    max_terms: int = MAX_REWRITE_TERMS,
) -> QueryRewrite:
    """Expand known terms without changing the original or creating URLs."""

    if not 0 <= max_terms <= MAX_REWRITE_TERMS:
        raise ValueError(f"max_terms must be between 0 and {MAX_REWRITE_TERMS}")
    normalized = " ".join(text.split())
    lowered = normalized.casefold()
    candidates: list[str] = []
    for key, values in sorted((aliases or {}).items(), key=lambda item: item[0].casefold()):
        if key.casefold() not in lowered:
            continue
        for value in values:
            term = " ".join(value.split())
            if (
                term
                and len(term) <= MAX_TERM_LENGTH
                and term.casefold() not in lowered
                and not term.casefold().startswith(("http://", "https://"))
            ):
                candidates.append(term)
    unique = tuple(dict.fromkeys(candidates))[:max_terms]
    return QueryRewrite(original=normalized, terms=unique, language=language)
