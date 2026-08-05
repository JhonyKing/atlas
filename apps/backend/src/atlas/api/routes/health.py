"""Content-free process and database readiness endpoint."""

from collections.abc import Awaitable, Callable
from typing import Literal, cast
from uuid import uuid4

from anyio import to_thread
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse
from psycopg import Connection
from pydantic import BaseModel, ConfigDict, SecretStr

DatabaseProbe = Callable[[], Awaitable[bool]]


class HealthChecks(BaseModel):
    model_config = ConfigDict(extra="forbid")

    database: Literal["ready", "unavailable"]


class HealthStatus(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "degraded"]
    checks: HealthChecks


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
    request_id = str(uuid4())

    try:
        database_is_ready = await _database_probe_from(request)()
    except Exception:
        database_is_ready = False

    payload = HealthStatus(
        status="ok" if database_is_ready else "degraded",
        checks=HealthChecks(
            database="ready" if database_is_ready else "unavailable",
        ),
    )
    response_status = (
        status.HTTP_200_OK if database_is_ready else status.HTTP_503_SERVICE_UNAVAILABLE
    )

    return JSONResponse(
        status_code=response_status,
        content=payload.model_dump(mode="json"),
        headers={
            "X-Request-ID": request_id,
            "Cache-Control": "no-store",
        },
    )


async def probe_database(database_url: SecretStr) -> bool:
    """Run the smallest readiness query without logging the connection string."""

    connection_string = database_url.get_secret_value().replace(
        "postgresql+psycopg://",
        "postgresql://",
        1,
    )

    return await to_thread.run_sync(_probe_database_sync, connection_string)


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
