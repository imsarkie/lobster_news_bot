import logging
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

# ── Alembic config object ────────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ── Import models so Alembic can detect schema changes ──────────────────────
from app.models import Base  # noqa: E402

target_metadata = Base.metadata


# ── Helpers ──────────────────────────────────────────────────────────────────
def get_url() -> str:
    """Read the sync database URL from the application Settings."""
    from app.config import settings

    return settings.sync_database_url


# ── Migration runners ────────────────────────────────────────────────────────
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no live DB connection needed)."""
    context.configure(
        url=get_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (requires a live DB connection)."""
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = get_url()

    connectable = engine_from_config(
        cfg,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
