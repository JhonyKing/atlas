"""ATLAS FastAPI application factory and local entry point."""

from datetime import timedelta
from functools import partial
from pathlib import Path

import psycopg
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from openai import AsyncOpenAI

from atlas.agent.cited_answer_graph import CitedAnswerDependencies, CitedAnswerGraph
from atlas.api.answer_service import InMemoryAnswerRunService
from atlas.api.comparison_service import InMemoryComparisonRunService
from atlas.api.middleware.anonymous_identity import AnonymousIdentityMiddleware
from atlas.api.routes.answers import AnswerRunControl
from atlas.api.routes.answers import router as answers_router
from atlas.api.routes.auth import router as auth_router
from atlas.api.routes.comparisons import ComparisonRunControl
from atlas.api.routes.comparisons import router as comparisons_router
from atlas.api.routes.corpus import router as corpus_router
from atlas.api.routes.feedback import FeedbackControl
from atlas.api.routes.feedback import router as feedback_router
from atlas.api.routes.health import DatabaseProbe, probe_database
from atlas.api.routes.health import router as health_router
from atlas.api.routes.news import router as news_router
from atlas.api.routes.operator_ingestion import router as operator_ingestion_router
from atlas.api.routes.reports import router as reports_router
from atlas.api.routes.review_cases import router as review_cases_router
from atlas.auth.ports import AuthPort
from atlas.comparison.demo_executor import DemoComparisonExecutor
from atlas.comparison.executor import (
    OpenAIComparisonObservationExtractor,
    RetrievalComparisonExecutor,
)
from atlas.comparison.retrieval import ComparisonRetrievalService, CorpusComparisonBranchRetriever
from atlas.config import Settings, get_settings
from atlas.demo import DemoAnswerGraph, DemoCorpusStatusProvider
from atlas.ingestion.service import OperatorIngestionService
from atlas.news.ranking import DailyNewsProvider
from atlas.news.runtime import LiveDailyNewsService
from atlas.observability.context import RequestContextMiddleware
from atlas.observability.langsmith import LangSmithTraceSink
from atlas.persistence.comparison_quota import (
    ComparisonQuotaService,
    InMemoryComparisonQuotaRepository,
)
from atlas.persistence.comparison_repository import InMemoryComparisonRepository
from atlas.persistence.corpus_repository import PostgresCorpusRepository
from atlas.persistence.corpus_status import CorpusStatusProvider, PostgresCorpusStatusRepository
from atlas.persistence.review_cases import InMemoryReviewCaseService, ReviewCaseListing
from atlas.providers.openai_embeddings import OpenAIEmbeddingsAdapter
from atlas.providers.openai_responses import OpenAIResponsesAdapter, derive_safety_identifier
from atlas.reports.service import InMemoryReportService
from atlas.retrieval.service import RetrievalService


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
    report_service: InMemoryReportService | None = None,
    visitor_hmac_secret: str | None = None,
    auth_provider: AuthPort | None = None,
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
    application.state.report_service = report_service
    application.state.operator_token = operator_token or (
        settings.atlas_operator_token.get_secret_value()
        if settings.atlas_operator_token is not None
        else None
    )
    application.state.auth_provider = auth_provider
    application.include_router(health_router)
    application.include_router(auth_router)
    application.include_router(answers_router)
    application.include_router(comparisons_router)
    application.include_router(feedback_router)
    application.include_router(corpus_router)
    application.include_router(operator_ingestion_router)
    application.include_router(review_cases_router)
    application.include_router(news_router)
    application.include_router(reports_router)
    return application


def create_runtime_app(*, use_real_provider: bool | None = None) -> FastAPI:
    """Build the process-level app, including safe deterministic development services.

    Tests use ``create_app`` with explicit dependencies. The local process uses a deterministic
    corpus/answer graph when running in development so a missing provider key cannot turn the
    portfolio demo into a broken browser experience. Production deliberately receives no such
    fallback and must wire a real provider service.
    """

    settings = get_settings()
    news_service = _news_service(settings)
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
            answer_graph = (
                _answer_graph(
                    settings,
                    corpus_service,
                    client=client,
                    generator=generator,
                )
                or answer_graph
            )
        comparison_executor = _comparison_executor(
            settings,
            corpus_service,
            client=client if real_provider and settings.openai_api_key is not None else None,
            allow_real=real_provider,
        )
        comparison_service = _comparison_service(
            settings, corpus_service, executor=comparison_executor
        )
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
            comparison_service=comparison_service,
            report_service=_report_service(settings, comparison_service=comparison_service),
            review_case_service=InMemoryReviewCaseService(),
            news_service=news_service,
        )
    corpus_service = _verified_corpus_or_demo(settings)
    comparison_service = _comparison_service(
        settings, corpus_service, executor=_comparison_executor(settings, corpus_service)
    )
    return create_app(
        corpus_service=corpus_service,
        comparison_service=comparison_service,
        report_service=_report_service(settings, comparison_service=comparison_service),
        news_service=news_service,
    )


def _news_service(settings: Settings) -> DailyNewsProvider | None:
    if not settings.atlas_news_enabled:
        return None
    manifest = Path(__file__).resolve().parents[5] / "corpus" / "manifests" / "news-v1.yaml"
    try:
        return LiveDailyNewsService(manifest)
    except (OSError, ValueError, KeyError, TypeError):
        return None


def _comparison_service(
    settings: Settings,
    corpus_service: CorpusStatusProvider,
    *,
    executor=None,
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
        executor=executor,
        trace_sink=LangSmithTraceSink.from_settings(settings),
        model=settings.atlas_answer_model,
    )


def _report_service(settings: Settings, *, comparison_service) -> InMemoryReportService:
    """Wire reports to the same comparison source; local storage is intentionally bounded."""

    del settings
    source = comparison_service
    if source is None:
        # Runtime wiring is completed after app construction in ``create_runtime_app``.
        class _Unavailable:
            async def get_status(self, run_id, *, visitor_key_hash):
                del run_id, visitor_key_hash
                return None

        source = _Unavailable()
    return InMemoryReportService(source=source)


def _comparison_executor(
    settings: Settings,
    corpus_service: CorpusStatusProvider,
    *,
    client: AsyncOpenAI | None = None,
    allow_real: bool = True,
):
    """Select a safe executor: local fixture in development, real graph only for verified data."""

    if isinstance(corpus_service, DemoCorpusStatusProvider) or (
        settings.atlas_env == "development" and not allow_real
    ):
        return DemoComparisonExecutor()
    if client is None and settings.openai_api_key is not None:
        client = AsyncOpenAI(api_key=settings.openai_api_key.get_secret_value())
    if client is None or not isinstance(corpus_service, PostgresCorpusStatusRepository):
        return None
    connection = None
    try:
        dsn = settings.database_url.get_secret_value().replace(
            "postgresql+psycopg://", "postgresql://", 1
        )
        connection = psycopg.connect(dsn)
        repository = PostgresCorpusRepository(connection)
        extractor = OpenAIComparisonObservationExtractor(
            client=client, model=settings.atlas_answer_model
        )
        return RetrievalComparisonExecutor(
            embedding_provider=OpenAIEmbeddingsAdapter(client=client),
            retrieval=ComparisonRetrievalService(CorpusComparisonBranchRetriever(repository)),
            extractor=extractor,
        )
    except Exception:
        if connection is not None:
            connection.close()
        return None


def _answer_graph(
    settings: Settings,
    corpus_service: CorpusStatusProvider,
    *,
    client: AsyncOpenAI,
    generator: OpenAIResponsesAdapter,
) -> CitedAnswerGraph | None:
    """Wire real evidence retrieval into the cited-answer graph.

    The local development fallback remains available when PostgreSQL is unavailable, but a
    configured provider must use the promoted corpus rather than the old demo evidence pack.
    The repository owns its connection for the lifetime of the graph process.
    """

    if not isinstance(corpus_service, PostgresCorpusStatusRepository):
        return None
    connection = None
    try:
        dsn = settings.database_url.get_secret_value().replace(
            "postgresql+psycopg://", "postgresql://", 1
        )
        connection = psycopg.connect(dsn)
        repository = PostgresCorpusRepository(connection)
        return CitedAnswerGraph(
            CitedAnswerDependencies(
                embedding_provider=OpenAIEmbeddingsAdapter(client=client),
                retriever=RetrievalService(repository),
                answer_generator=generator,
                top_k=20,
                timeout_seconds=15.0,
            )
        )
    except Exception:
        if connection is not None:
            connection.close()
        return None


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
