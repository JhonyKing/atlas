"""ATLAS FastAPI application factory and local entry point."""

from datetime import timedelta
from functools import partial

import psycopg
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from atlas.api.answer_service import InMemoryAnswerRunService
from atlas.api.comparison_service import InMemoryComparisonRunService
from atlas.api.middleware.anonymous_identity import AnonymousIdentityMiddleware
from atlas.api.routes.answers import AnswerRunControl
from atlas.api.routes.answers import router as answers_router
from atlas.api.routes.comparisons import ComparisonRunControl
from atlas.api.routes.comparisons import router as comparisons_router
from atlas.api.routes.corpus import router as corpus_router
from atlas.api.routes.feedback import FeedbackControl
from atlas.api.routes.feedback import router as feedback_router
from atlas.api.routes.health import DatabaseProbe, probe_database
from atlas.api.routes.health import router as health_router
from atlas.api.routes.news import router as news_router
from atlas.api.routes.operator_ingestion import router as operator_ingestion_router
from atlas.api.routes.review_cases import router as review_cases_router
from atlas.config import Settings, get_settings
from atlas.demo import DemoAnswerGraph, DemoCorpusStatusProvider, OpenAIConnectedDemoGraph
from atlas.ingestion.service import OperatorIngestionService
from atlas.news.ranking import DailyNewsProvider
from atlas.observability.context import RequestContextMiddleware
from atlas.observability.langsmith import LangSmithTraceSink
from atlas.persistence.comparison_quota import (
    ComparisonQuotaService,
    InMemoryComparisonQuotaRepository,
)
from atlas.persistence.comparison_repository import InMemoryComparisonRepository
from atlas.persistence.corpus_status import CorpusStatusProvider, PostgresCorpusStatusRepository
from atlas.persistence.review_cases import InMemoryReviewCaseService, ReviewCaseListing
from atlas.providers.openai_responses import OpenAIResponsesAdapter, derive_safety_identifier


def create_app(
    *,
    database_probe: DatabaseProbe | None = None,
    operator_service: OperatorIngestionService | None = None,
    operator_token: str | None = None,
    answer_service: AnswerRunControl | None = None,
    comparison_service: ComparisonRunControl | None = None,
    feedback_service: FeedbackControl | None = None,
    corpus_service: CorpusStatusProvider | None = None,
    news_service: DailyNewsProvider | None = None,
    review_case_service: ReviewCaseListing | None = None,
    visitor_hmac_secret: str | None = None,
) -> FastAPI:
    """Build an isolated application whose external dependencies can be replaced in tests."""

    settings = get_settings()
    resolved_database_probe = database_probe or partial(probe_database, settings.database_url)

    application = FastAPI(
        title="ATLAS AI API",
        description="Evidence-first technical research with verifiable cited answers.",
        version="0.1.0",
    )
    application.add_middleware(
        CORSMiddleware,
        allow_origins=[str(settings.web_origin).rstrip("/")],
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["Accept", "Authorization", "Content-Type", "Idempotency-Key"],
        expose_headers=["X-Atlas-Run-ID", "X-Request-ID"],
    )
    application.add_middleware(RequestContextMiddleware)
    resolved_visitor_secret = visitor_hmac_secret or (
        settings.atlas_visitor_hmac_secret.get_secret_value()
        if settings.atlas_visitor_hmac_secret is not None
        else None
    )
    application.add_middleware(
        AnonymousIdentityMiddleware,
        secret=resolved_visitor_secret or "atlas-development-only-visitor-secret",
    )
    application.state.database_probe = resolved_database_probe
    application.state.operator_service = operator_service
    application.state.answer_service = answer_service
    application.state.comparison_service = comparison_service
    application.state.feedback_service = feedback_service
    application.state.corpus_service = corpus_service
    application.state.news_service = news_service
    application.state.review_case_service = review_case_service
    application.state.operator_token = operator_token or (
        settings.atlas_operator_token.get_secret_value()
        if settings.atlas_operator_token is not None
        else None
    )
    application.include_router(health_router)
    application.include_router(answers_router)
    application.include_router(comparisons_router)
    application.include_router(feedback_router)
    application.include_router(corpus_router)
    application.include_router(operator_ingestion_router)
    application.include_router(review_cases_router)
    application.include_router(news_router)
    return application


def create_runtime_app(*, use_real_provider: bool | None = None) -> FastAPI:
    """Build the process-level app, including safe deterministic development services.

    Tests use ``create_app`` with explicit dependencies. The local process uses a deterministic
    corpus/answer graph when running in development so a missing provider key cannot turn the
    portfolio demo into a broken browser experience. Production deliberately receives no such
    fallback and must wire a real provider service.
    """

    settings = get_settings()
    if settings.atlas_env == "development":
        corpus_service = _verified_corpus_or_demo(settings)
        corpus_snapshot = (
            str(corpus_service.get_status().snapshot_id)
            if isinstance(corpus_service, PostgresCorpusStatusRepository)
            else "demo-unverified"
        )
        real_provider = (
            use_real_provider
            if use_real_provider is not None
            else bool(
                settings.openai_api_key and settings.openai_api_key.get_secret_value().strip()
            )
        )
        answer_graph = DemoAnswerGraph()
        if real_provider and settings.openai_api_key is not None:
            client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
            safety_secret = (
                settings.atlas_visitor_hmac_secret.get_secret_value()
                if settings.atlas_visitor_hmac_secret is not None
                else "atlas-development-only-visitor-secret"
            )
            generator = OpenAIResponsesAdapter(
                client=client,
                safety_identifier=derive_safety_identifier(
                    safety_secret,
                    "development-anonymous-visitor",
                ),
            )
            answer_graph = OpenAIConnectedDemoGraph(generator)
        return create_app(
            answer_service=InMemoryAnswerRunService(
                answer_graph,
                trace_sink=LangSmithTraceSink.from_settings(settings),
                trace_metadata={
                    "model": settings.atlas_answer_model,
                    "prompt_version": "cited-answer-v1",
                    "retrieval_version": "hybrid-v1",
                    "embedding_profile": (
                        f"{settings.atlas_embedding_model}:{settings.atlas_embedding_dimensions}"
                    ),
                    "application_version": "0.1.0",
                    "corpus_snapshot": corpus_snapshot,
                },
            ),
            corpus_service=corpus_service,
            comparison_service=_comparison_service(settings, corpus_service),
            review_case_service=InMemoryReviewCaseService(),
        )
    corpus_service = _verified_corpus_or_demo(settings)
    return create_app(
        corpus_service=corpus_service,
        comparison_service=_comparison_service(settings, corpus_service),
    )


def _comparison_service(
    settings: Settings, corpus_service: CorpusStatusProvider
) -> InMemoryComparisonRunService:
    """Wire a fail-closed comparison coordinator into every runtime environment."""

    return InMemoryComparisonRunService(
        quota=ComparisonQuotaService(
            InMemoryComparisonQuotaRepository(
                limit=settings.atlas_anonymous_comparison_limit,
                window=timedelta(hours=settings.atlas_anonymous_window_hours),
            )
        ),
        repository=InMemoryComparisonRepository(),
        snapshot_provider=lambda: corpus_service.get_status().snapshot_id,
        trace_sink=LangSmithTraceSink.from_settings(settings),
        model=settings.atlas_answer_model,
    )


def _verified_corpus_or_demo(settings: Settings) -> CorpusStatusProvider:
    """Use PostgreSQL status after snapshot promotion, otherwise keep the visible demo fallback."""

    dsn = settings.database_url.get_secret_value().replace(
        "postgresql+psycopg://", "postgresql://", 1
    )
    connection = None
    try:
        connection = psycopg.connect(dsn)
        provider = PostgresCorpusStatusRepository(connection)
        provider.get_status()
        return provider
    except Exception as exc:
        if connection is not None:
            connection.close()
        if settings.atlas_env != "development":
            raise RuntimeError(
                "a verified corpus snapshot is required outside development"
            ) from exc
        return DemoCorpusStatusProvider()


app = create_runtime_app()


def run() -> None:
    """Start the local API process using the documented development address."""

    uvicorn.run("atlas.api.main:app", host="127.0.0.1", port=8000)
