from datetime import UTC, date, datetime
from uuid import UUID, uuid4

import pytest
from pydantic import HttpUrl, ValidationError

from atlas.domain import (
    AnswerDraft,
    AnswerStatus,
    Citation,
    Claim,
    ClaimType,
    CollectionSlug,
    CollectionState,
    CollectionStatus,
    ControlledError,
    CorpusStatus,
    ErrorCode,
    Evidence,
    Question,
    SourceType,
)

NOW = datetime(2026, 8, 4, 12, 0, tzinfo=UTC)
EVIDENCE_ID = UUID("0198e4d5-7c4a-7c3e-8f0b-8c5c4d2e1f01")
CITATION_ID = UUID("0198e4d5-7c4a-7c3e-8f0b-8c5c4d2e1f02")


def evidence() -> Evidence:
    return Evidence(
        id=EVIDENCE_ID,
        source_title="LangGraph persistence",
        publisher="LangChain",
        canonical_url=HttpUrl("https://langchain-ai.github.io/langgraph/concepts/persistence/"),
        excerpt="A checkpointer saves graph state at super-step boundaries.",
        captured_at=NOW,
        published_at=None,
        version_label=None,
        source_type=SourceType.DOCUMENTATION,
    )


def citation() -> Citation:
    return Citation(id=CITATION_ID, evidence_id=EVIDENCE_ID)


def test_question_preserves_original_text_and_exposes_normalized_form() -> None:
    question = Question(
        text="  When does LangGraph need a checkpointer?  ",
        product=CollectionSlug.LANGGRAPH,
        version="1.0",
        date_from=date(2025, 1, 1),
        date_to=date(2026, 1, 1),
    )

    assert question.text.startswith("  ")
    assert question.normalized_text == "when does langgraph need a checkpointer?"
    assert question.product is CollectionSlug.LANGGRAPH


@pytest.mark.parametrize("text", ["", "  ", "?!...", "x" * 2001])
def test_question_rejects_empty_punctuation_only_and_over_limit_text(text: str) -> None:
    with pytest.raises(ValidationError):
        Question(text=text)


def test_domain_models_forbid_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        Question.model_validate({"text": "What is LangGraph?", "internal_prompt": "secret"})
    with pytest.raises(ValidationError):
        Evidence.model_validate({**evidence().model_dump(), "provider_response": "raw"})


def test_claim_requires_unique_citations_and_non_negative_ordinal() -> None:
    claim = Claim(
        id=uuid4(),
        ordinal=0,
        text="A checkpointer saves graph state.",
        type=ClaimType.FACTUAL,
        citation_ids=[CITATION_ID],
    )
    assert claim.citation_ids == [CITATION_ID]

    with pytest.raises(ValidationError):
        Claim(
            id=uuid4(),
            ordinal=-1,
            text="A claim",
            type=ClaimType.FACTUAL,
            citation_ids=[CITATION_ID],
        )
    with pytest.raises(ValidationError):
        Claim(
            id=uuid4(),
            ordinal=0,
            text="A claim",
            type=ClaimType.FACTUAL,
            citation_ids=[CITATION_ID, CITATION_ID],
        )


def test_answer_draft_requires_claims_for_non_abstention_and_exposes_only_ids() -> None:
    claim = Claim(
        id=uuid4(),
        ordinal=0,
        text="A checkpointer saves graph state.",
        type=ClaimType.FACTUAL,
        citation_ids=[CITATION_ID],
    )
    draft = AnswerDraft(
        answer_status=AnswerStatus.COMPLETE,
        claims=[claim],
        evidence_ids=[EVIDENCE_ID],
        limitations=[],
    )
    assert draft.evidence_ids == [EVIDENCE_ID]
    assert not hasattr(draft, "source_title")

    with pytest.raises(ValidationError):
        AnswerDraft(answer_status=AnswerStatus.COMPLETE, claims=[], evidence_ids=[])

    abstention = AnswerDraft(
        answer_status=AnswerStatus.ABSTAINED,
        claims=[],
        evidence_ids=[],
        limitations=["The corpus has no supporting evidence."],
    )
    assert abstention.answer_status is AnswerStatus.ABSTAINED


def test_evidence_and_citation_keep_canonical_provenance_separate() -> None:
    record = evidence()
    link = citation()

    assert str(record.canonical_url).startswith("https://")
    assert link.evidence_id == record.id

    with pytest.raises(ValidationError):
        Evidence(
            id=EVIDENCE_ID,
            source_title="Source",
            publisher="Publisher",
            canonical_url=HttpUrl("http://example.com/source"),
            excerpt="Evidence",
            captured_at=NOW,
            source_type=SourceType.DOCUMENTATION,
        )


def test_corpus_status_requires_three_unique_collections() -> None:
    collection = CollectionStatus(
        slug=CollectionSlug.LANGGRAPH,
        name="LangGraph",
        publisher="LangChain",
        source_types=[SourceType.DOCUMENTATION],
        status=CollectionState.READY,
        last_success_at=NOW,
        last_attempt_at=NOW,
        canonical_root=HttpUrl("https://langchain-ai.github.io/langgraph/"),
    )
    status = CorpusStatus(
        snapshot_id=uuid4(),
        generated_at=NOW,
        collections=[
            collection,
            collection.model_copy(update={"slug": CollectionSlug.LANGCHAIN}),
            collection.model_copy(update={"slug": CollectionSlug.OPENAI}),
        ],
    )
    assert len(status.collections) == 3

    with pytest.raises(ValidationError):
        CorpusStatus(snapshot_id=uuid4(), generated_at=NOW, collections=[collection])


def test_controlled_error_has_safe_code_and_no_raw_exception_field() -> None:
    error = ControlledError(
        code=ErrorCode.QUOTA_EXCEEDED,
        message="The anonymous question limit has been reached.",
        retryable=True,
        request_id=uuid4(),
    )

    assert error.code is ErrorCode.QUOTA_EXCEEDED
    assert "exception" not in error.model_dump()

    with pytest.raises(ValidationError):
        ControlledError.model_validate(
            {
                "code": "database_password=secret",
                "message": "failed",
                "request_id": uuid4(),
            }
        )
