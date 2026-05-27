"""Alembic migrations environment configuration.

Uses synchronous psycopg2 for migrations (Alembic is not async-compatible),
while the application runtime uses asyncpg. Both target the same database.
"""

from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure all model modules are imported so Base.metadata includes all tables.
import app.infrastructure.database.models.product  # noqa: F401
import app.infrastructure.database.models.user  # noqa: F401
from app.config import settings
from app.infrastructure.database.base import Base

# Alembic Config object
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Override sqlalchemy.url with SYNC_DATABASE_URL for synchronous migrations
config.set_main_option("sqlalchemy.url", settings.SYNC_DATABASE_URL)

# Target metadata for autogenerate support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (generate SQL without DB connection).

    Configured with a URL; Alembic generates raw SQL statements.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (connect to DB and apply)."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
