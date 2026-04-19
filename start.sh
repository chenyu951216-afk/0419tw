#!/bin/sh
set -eu
mkdir -p /data
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8080}"
