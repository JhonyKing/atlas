#!/bin/sh
set -eu

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

exec uvicorn atlas.api.main:app --host 0.0.0.0 --port "${PORT:-8000}"
