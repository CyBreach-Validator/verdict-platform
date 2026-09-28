"""Guard for N-D2: the Alembic migration and the SQLAlchemy models must agree.

The original bug was `Base.metadata.create_all()` running at import while the
Alembic chain created a different schema, so the two silently drifted. This
test fails if they ever drift again.

It works by rendering the migration to offline SQL (`alembic upgrade head
--sql`, no database needed) and diffing the resulting table/column set against
`Base.metadata`.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

# Alembic's offline mode only needs a URL it can build a dialect from; it
# never opens a connection.
os.environ.setdefault(
    "DATABASE_URL", "postgresql://user:pass@localhost:5432/verdict_db"
)

sys.path.insert(0, str(BACKEND_DIR))

CREATE_TABLE_RE = re.compile(r"CREATE TABLE (\w+) \((.*?)\n\);", re.S)
CONSTRAINT_PREFIXES = ("PRIMARY", "UNIQUE", "FOREIGN", "CONSTRAINT")


def _migration_tables() -> dict:
    result = subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head", "--sql"],
        cwd=BACKEND_DIR,
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        raise AssertionError(
            "alembic upgrade head --sql failed:\n"
            f"{result.stdout}\n{result.stderr}"
        )

    tables = {}

    for match in CREATE_TABLE_RE.finditer(result.stdout):
        table, body = match.group(1), match.group(2)

        if table == "alembic_version":
            continue

        tables[table] = {
            line.strip().split()[0]
            for line in body.splitlines()
            if line.strip() and not line.strip().startswith(CONSTRAINT_PREFIXES)
        }

    return tables


def test_migration_matches_models():
    from app.database.base import Base

    # Importing the models registers them on Base.metadata.
    import app.models.user        # noqa: F401
    import app.models.rule        # noqa: F401
    import app.models.verdict     # noqa: F401
    import app.models.audit_log   # noqa: F401
    import app.models.connector   # noqa: F401

    migration = _migration_tables()
    models = {name: set(table.columns.keys()) for name, table in Base.metadata.tables.items()}

    problems = []

    for table in sorted(set(migration) | set(models)):
        if table not in migration:
            problems.append(f"{table}: present in models, missing from migration")
        elif table not in models:
            problems.append(f"{table}: present in migration, missing from models")
        else:
            only_models = models[table] - migration[table]
            only_migration = migration[table] - models[table]

            if only_models or only_migration:
                problems.append(
                    f"{table}: only-in-models={sorted(only_models)} "
                    f"only-in-migration={sorted(only_migration)}"
                )

    assert not problems, (
        "Alembic migrations and SQLAlchemy models have drifted:\n  "
        + "\n  ".join(problems)
        + "\n\nGenerate a revision (`alembic revision --autogenerate`) to reconcile."
    )


def test_expected_tables_present():
    from app.database.database import EXPECTED_TABLES

    assert set(EXPECTED_TABLES) == {
        "users",
        "rules",
        "verdict_events",
        "audit_logs",
        "platform_connector_health",
    }


def test_no_connector_table_name_collision():
    """N-D12: Delta must not create a table named `connectors`."""

    from app.database.base import Base

    import app.models.connector  # noqa: F401

    assert "connectors" not in Base.metadata.tables, (
        "Delta owns `platform_connector_health`; a `connectors` table collides "
        "with Pod Gamma's and the canonical Connector Framework registry."
    )
