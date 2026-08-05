"""ATLAS FastAPI application factory and local entry point."""

from functools import partial

import uvicorn
from fastapi import FastAPI

from atlas.api.middleware.anonymous_identity import AnonymousIdentityMiddleware
from atlas.api.routes.answers import AnswerRunControl
from atlas.api.routes.answers import router as answers_router
from atlas.api.routes.corpus import router as corpus_router
from atlas.api.routes.feedback import FeedbackControl
from atlas.api.routes.feedback import router as feedback_router
from atlas.api.routes.health import DatabaseProbe, probe_database
from atlas.api.routes.health import router as health_router
from atlas.api.routes.operator_ingestion import router as operator_ingestion_router
from atlas.config import get_settings
from atlas.ingestion.service import OperatorIngestionService
from atlas.observability.context import RequestContextMiddleware
from atlas.persistence.corpus_status import CorpusStatusProvider


def create_app(
    *,
    database_probe: DatabaseProbe | None = None,
    operator_service: OperatorIngestionService | None = None,
    operator_token: str | None = None,
    answer_service: AnswerRunControl | None = None,
    feedback_service: FeedbackControl | None = None,
    corpus_service: CorpusStatusProvider | None = None,
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
    application.state.feedback_service = feedback_service
    application.state.corpus_service = corpus_service
    application.state.operator_token = operator_token or (
        settings.atlas_operator_token.get_secret_value()
        if settings.atlas_operator_token is not None
        else None
    )
    application.include_router(health_router)
    application.include_router(answers_router)
    application.include_router(feedback_router)
    application.include_router(corpus_router)
    application.include_router(operator_ingestion_router)
    return application


app = create_app()


def run() -> None:
    """Start the local API process using the documented development address."""

    uvicorn.run("atlas.api.main:app", host="127.0.0.1", port=8000)
