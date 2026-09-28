import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from app.database.database import Base
from app.models.user import User
from app.models.rule import Rule
from app.models.verdict import Verdict
from app.models.audit_log import AuditLog
# Without this import the connector-health table is absent from
# `target_metadata`, so a future `alembic revision --autogenerate` would
# propose dropping and recreating a table the migration already creates.
from app.models.connector import Connector

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def _database_url() -> str:
    """Resolve the migration URL from the environment.

    M7/m7: `alembic.ini` shipped a literal
    `postgresql://validator:validator_dev_pw@localhost:5432/module2_validator`
    in the repository, so the migration target was a real credential committed
    to source, pointed at a database name that no longer matches
    `.env.example`, and silently overrode whatever DATABASE_URL the operator
    had configured -- migrations ran against a different database than the app.

    The ini value is kept only as a placeholder (no credentials) for the
    `env.py` template's benefit; DATABASE_URL is the single source of truth.
    """

    url = os.environ.get("DATABASE_URL")

    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Alembic refuses to fall back to a URL "
            "compiled into alembic.ini, because that file is committed to the "
            "repository. Set DATABASE_URL (see .env.example) and re-run."
        )

    return url


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = _database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Same environment-only resolution as the offline path, so online and
    # offline migrations can never target different databases.
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = _database_url()

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
