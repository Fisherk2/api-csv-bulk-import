#!/bin/bash
# ── Docker Entrypoint ───────────────────────────────────
# Runs database migrations before starting the application.
# Uses strict mode for safety.
# ─────────────────────────────────────────────────────────
set -Eeuo pipefail

echo "[entrypoint] Running database migrations..."
alembic upgrade head

echo "[entrypoint] Starting application..."
exec "$@"
