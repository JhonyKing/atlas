"""Content-free process and database readiness endpoint."""

from collections.abc import Awaitable, Callable
from typing import Literal, cast
from uuid import uuid4

from anyio import to_thread
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from psycopg import Connection
from pydantic import BaseModel, ConfigDict, SecretStr

from atlas.observability.context import current_request_id

DatabaseProbe = Callable[[], Awaitable[bool]]
MigrationProbe = Callable[[], Awaitable[tuple[bool, str]]]


class HealthChecks(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: Literal["ready", "unavailable"]


class ReadinessChecks(BaseModel):
    """Machine-readable dependency checks used by deployment gates."""

    model_config = ConfigDict(extra="forbid")

    database: Literal["ready", "failed"]
    migrations: Literal["ready", "failed", "unknown"]
    model_provider: Literal["ready", "degraded", "disabled"]
    observability: Literal["ready", "degraded"]


class HealthStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "degraded"]
    checks: HealthChecks


class ReadinessStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ready", "degraded", "unavailable"]
    environment: str
    release_id: str
    source_revision: str
    migration_revision: str
    checks: ReadinessChecks


_REQUEST_ID_HEADER = {
    "X-Request-ID": {
        "description": "Stable identifier for content-free request correlation.",
        "schema": {"type": "string", "format": "uuid"},
    }
}

router = APIRouter(tags=["Health"])


def _database_probe_from(request: Request) -> DatabaseProbe:
    return cast(DatabaseProbe, request.app.state.database_probe)


@router.get(
    "/healthz",
    response_model=HealthStatus,
    responses={
        200: {
            "description": "Process and database are ready.",
            "headers": _REQUEST_ID_HEADER,
        },
        503: {
            "description": "Process is alive but the database is unavailable.",
            "headers": _REQUEST_ID_HEADER,
            "model": HealthStatus,
        },
    },
)
async def get_health(request: Request) -> JSONResponse:
    request_id = str(current_request_id() or uuid4())

    # Liveness deliberately does not probe dependencies: an orchestrator must be able to
    # distinguish a live process from a process that is not yet ready for traffic.
    payload = HealthStatus(status="ok", checks=HealthChecks(database="ready"))

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=payload.model_dump(mode="json"),
        headers={
            "X-Request-ID": request_id,
            "Cache-Control": "no-store",
        },
    )


@router.get(
    "/readyz",
    response_model=ReadinessStatus,
    responses={503: {"description": "A required runtime dependency is unavailable."}},
)
async def get_readiness(request: Request) -> JSONResponse:
    """Report dependency readiness without exposing connection strings or provider secrets."""

    request_id = str(current_request_id() or uuid4())
    try:
        database_is_ready = await _database_probe_from(request)()
    except Exception:
        database_is_ready = False
    settings = getattr(request.app.state, "settings", None)
    environment = getattr(settings, "atlas_env", "development")
    release_id = getattr(request.app.state, "release_id", "local")
    source_revision = getattr(request.app.state, "source_revision", "local")
    migration_revision = getattr(request.app.state, "migration_revision", "unknown")
    provider = cast(
        Literal["ready", "degraded", "disabled"],
        getattr(request.app.state, "model_provider_status", "disabled"),
    )
    observability = cast(
        Literal["ready", "degraded"],
        getattr(request.app.state, "observability_status", "ready"),
    )
    migrations = cast(
        Literal["ready", "failed", "unknown"],
        getattr(request.app.state, "migration_status", "unknown"),
    )
    if migrations == "unknown":
        migration_probe = getattr(request.app.state, "migration_probe", None)
        if migration_probe is not None:
            try:
                migration_ready, detected_revision = await migration_probe()
            except Exception:
                migration_ready, detected_revision = False, "unknown"
            migrations = "ready" if migration_ready else "failed"
            migration_revision = detected_revision
    checks = ReadinessChecks(
        database="ready" if database_is_ready else "failed",
        migrations=migrations,
        model_provider=provider,
        observability=observability,
    )
    ready = database_is_ready and migrations == "ready"
    payload = ReadinessStatus(
        status="ready" if ready else "unavailable",
        environment=environment,
        release_id=release_id,
        source_revision=source_revision,
        migration_revision=migration_revision,
        checks=checks,
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK if ready else status.HTTP_503_SERVICE_UNAVAILABLE,
        content=payload.model_dump(mode="json"),
        headers={"X-Request-ID": request_id, "Cache-Control": "no-store"},
    )


async def probe_database(database_url: SecretStr) -> bool:
    """Run the smallest readiness query without logging the connection string."""

    connection_string = database_url.get_secret_value().replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

    return await to_thread.run_sync(_probe_database_sync, connection_string)


async def probe_migration_head(database_url: SecretStr, expected_head: str) -> tuple[bool, str]:
    """Verify the applied Alembic head without logging the database URL."""

    connection_string = database_url.get_secret_value().replace(
        "postgresql+psycopg://", "postgresql://", 1
    )
    return await to_thread.run_sync(_probe_migration_head_sync, connection_string, expected_head)


def _probe_migration_head_sync(connection_string: str, expected_head: str) -> tuple[bool, str]:
    with (
        Connection.connect(connection_string, autocommit=True, connect_timeout=2) as connection,
        connection.cursor() as cursor,
    ):
        cursor.execute("SELECT version_num FROM alembic_version LIMIT 1")
        row = cursor.fetchone()
    revision = str(row[0]) if row else "unknown"
    return revision == expected_head, revision


def _probe_database_sync(connection_string: str) -> bool:
    """Use a worker thread so Windows and Linux event-loop policies behave identically."""

    with Connection.connect(
        connection_string,
        autocommit=True,
        connect_timeout=2,
    ) as connection, connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        row = cursor.fetchone()

    return row == (1,)
