import os
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv

# ── Environment Discovery ───────────────────────────────────────────────────
def find_infra_env() -> Path:
    """Discovery .env file by traversing up from this script."""
    curr = Path(__file__).resolve().parent
    for parent in [curr, *curr.parents]:
        candidate = parent / "infra" / ".env"
        if candidate.exists():
            return candidate
    return None

env_path = find_infra_env()
if env_path:
    load_dotenv(env_path)

# ── Alembic Configuration ───────────────────────────────────────────────────
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

from infrastructure.database.base import Base
# Import all models to ensure they are registered
import infrastructure.database.models.tenant
import infrastructure.database.models.user
import infrastructure.database.models.audit
import infrastructure.database.models.subscription
import infrastructure.database.models.session
import infrastructure.database.models.api_key
import infrastructure.database.models.feature_flag

target_metadata = Base.metadata

def get_url():
    # Priority: DATABASE_URL > individual components
    if url := os.getenv("DATABASE_URL"):
        return url
    
    user = os.getenv("DB_USER", "saas")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    db = os.getenv("DB_NAME", "saas")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{db}"

def run_migrations_offline() -> None:
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "pyformat"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_url()
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
