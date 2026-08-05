"""ATLAS FastAPI application factory and local entry point."""

from functools import partial

import uvicorn
from fastapi import FastAPI

from atlas.api.routes.health import DatabaseProbe, probe_database
from atlas.api.routes.health import router as health_router
from atlas.config import get_settings


def create_app(*, database_probe: DatabaseProbe | None = None) -> FastAPI:
    """Build an isolated application whose external dependencies can be replaced in tests."""

    settings = get_settings()
    resolved_database_probe = database_probe or partial(probe_database, settings.database_url)

    application = FastAPI(
        title="ATLAS AI API",
        description="Evidence-first technical research with verifiable cited answers.",
        version="0.1.0",
    )
    application.state.database_probe = resolved_database_probe
    application.include_router(health_router)
    return application


app = create_app()


def run() -> None:
    """Start the local API process using the documented development address."""

    uvicorn.run("atlas.api.main:app", host="127.0.0.1", port=8000)
