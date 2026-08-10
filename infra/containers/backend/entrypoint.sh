#!/bin/sh
set -eu

exec uvicorn atlas.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
