# ── Multi-Stage Docker Build ─────────────────────────────
# Build stage: installs ALL dependencies
# Production stage: runs as non-root user with app + deps only
# Image target: < 300 MB

# ============================================================
# STAGE 1: Build
# ============================================================
FROM python:3.12-slim AS build

WORKDIR /app

# Install system dependencies: curl for health checks, build-essential for C extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies globally (land in /usr/local/)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and migration files
COPY app/ ./app/
COPY migrations/ ./migrations/
COPY alembic.ini .

# ============================================================
# STAGE 2: Production
# ============================================================
FROM python:3.12-slim AS production

WORKDIR /app

# Copy Python packages from build stage (global install — accessible to any user)
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy application code and configuration
COPY --from=build /app/app ./app
COPY --from=build /app/migrations ./migrations
COPY --from=build /app/alembic.ini .

# Copy and prepare entrypoint script
COPY scripts/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Create non-root user and grant ownership of /app
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Health check — verifies the app is responding
HEALTHCHECK --interval=30s --timeout=10s --retries=3 \
    CMD curl -f http://localhost:8000/ || exit 1

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
