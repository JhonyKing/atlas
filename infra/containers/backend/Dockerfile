FROM python:3.13-slim-bookworm AS build

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PROJECT_ENVIRONMENT=/opt/venv
WORKDIR /app
RUN pip install --no-cache-dir uv==0.12.1
COPY apps/backend/uv.lock ./apps/backend/uv.lock
COPY apps/backend/pyproject.toml ./apps/backend/pyproject.toml
COPY apps/backend/src ./apps/backend/src
RUN uv sync --project apps/backend --frozen --no-dev
RUN uv pip install --python /opt/venv/bin/python ./apps/backend

FROM python:3.13-slim-bookworm
ENV PATH="/opt/venv/bin:$PATH" PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY --from=build /opt/venv /opt/venv
COPY database ./database
COPY corpus ./corpus
COPY infra/containers/backend/entrypoint.sh /entrypoint.sh
RUN useradd --create-home --uid 10001 atlas && chmod 0555 /entrypoint.sh && chown -R atlas:atlas /app /opt/venv
USER atlas
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz', timeout=3)"
ENTRYPOINT ["/entrypoint.sh"]
