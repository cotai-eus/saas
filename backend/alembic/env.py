import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

from infrastructure.database.base import Base
from infrastructure.settings import settings as app_settings

import infrastructure.database.models.tenant
import infrastructure.database.models.user
import infrastructure.database.models.audit
import infrastructure.database.models.subscription
import infrastructure.database.models.session
import infrastructure.database.models.api_key
import infrastructure.database.models.feature_flag


def find_infra_env() -> Path | None:
    curr = Path(__file__).resolve().parent
    for parent in [curr, *curr.parents]:
        candidate = parent / "infra" / ".env"
        if candidate.exists():
            return candidate
    return None


env_path = find_infra_env()
if env_path:
    load_dotenv(env_path)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=app_settings.resolved_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "pyformat"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = app_settings.resolved_database_url
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
