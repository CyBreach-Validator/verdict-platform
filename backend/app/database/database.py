import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, DeclarativeBase

# Load environment variables
load_dotenv()

# M7: every table this service owns. `verify_schema()` checks the live database
# against exactly this set, so a missing or un-migrated table is reported by
# name instead of surfacing later as an opaque query error.
#
# N-D12: `platform_connector_health`, not `connectors` -- Delta does not own the
# Connector Framework registry (plan Section 7 assigns it to Pod Alpha), and a
# table named `connectors` collides with Pod Gamma's.
EXPECTED_TABLES = (
    "users",
    "rules",
    "verdict_events",
    "audit_logs",
    "platform_connector_health",
)

# The single Alembic revision that owns the whole schema. If this changes, the
# constant changes with it.
EXPECTED_ALEMBIC_REVISION = "0001_initial_verdict_platform"


def _require_database_url() -> str:
    """Resolve `DATABASE_URL` or fail with an actionable message.

    M7: this used to be passed straight to `create_engine()`, which raises
    `TypeError: expected str, bytes or os.PathLike object, not NoneType` deep
    inside SQLAlchemy when the variable is unset. That is a confusing way to
    learn that you forgot to create `backend/.env`.
    """

    url = os.getenv("DATABASE_URL")

    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set.\n"
            "The backend needs it to reach PostgreSQL before it can serve "
            "anything:\n"
            "  export DATABASE_URL=postgresql://<user>:<password>@localhost:5432/module2_validator\n"
            "or add DATABASE_URL=... to backend/.env (see backend/.env.example). "
            "No default is provided, so an unset value can never silently "
            "connect to the wrong database."
        )

    return url


class Base(DeclarativeBase):
    pass


# Create database engine. N-D2: the schema is owned by Alembic alone --
# `Base.metadata.create_all()` used to run at import time, which silently
# created a *different* schema from the one the migrations produce, so the two
# schema sources drifted without anyone noticing. Use `alembic upgrade head`.
engine = create_engine(_require_database_url())

# Create session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def verify_schema(target_engine=None) -> None:
    """Confirm the database is migrated to head before the app serves traffic.

    N-D2: this is the replacement for the import-time `create_all()`. The
    application refuses to start against an unmigrated database rather than
    papering over it, which is what made the broken migration chain invisible
    for so long.
    """

    target_engine = target_engine or engine

    with target_engine.connect() as connection:
        inspector = inspect(connection)

        present = set(inspector.get_table_names())
        missing = [name for name in EXPECTED_TABLES if name not in present]

        if missing:
            raise RuntimeError(
                "The database is missing Delta tables: "
                + ", ".join(missing)
                + ".\nThe schema is owned by Alembic, not by the application. "
                "Run:\n"
                "  cd backend && alembic upgrade head\n"
                "If the tables exist under different names, this service is "
                "pointed at the wrong database -- check DATABASE_URL."
            )

        if "alembic_version" in present:
            revision = connection.exec_driver_sql(
                "SELECT version_num FROM alembic_version"
            ).scalar()

            if revision != EXPECTED_ALEMBIC_REVISION:
                raise RuntimeError(
                    f"The database is at Alembic revision {revision!r}, but "
                    f"this service requires {EXPECTED_ALEMBIC_REVISION!r}.\n"
                    "Run `cd backend && alembic upgrade head` to bring it to "
                    "head before starting the API."
                )


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
