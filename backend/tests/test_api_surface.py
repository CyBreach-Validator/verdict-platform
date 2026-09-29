"""Guard for B13: the assembled API must expose the plan's documented
endpoints at the plan's paths.

`POST /api/v2/validate` did not exist -- the router carried
`prefix="/validator"`, so the route resolved to `/api/v2/validator/validate`
and no `/api/v2/validate` string appeared anywhere in the repository. This test
walks the assembled OpenAPI schema (the same approach as
`test_auth_coverage.py`, so it cannot drift from the routers that are actually
mounted) and fails if a documented endpoint is missing or if the old nested
path reappears.
"""

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault(
    "DATABASE_URL", "postgresql://user:pass@localhost:5432/verdict_db"
)

sys.path.insert(0, str(BACKEND_DIR))

# The `/api/v2/*` endpoints the plan (Section 5 "API Endpoints") names, mapped
# to the HTTP methods each one answers.
#
# `POST /api/v2/connectors/register` is deliberately absent: plan Section 7
# assigns the Connector Framework to Alpha, and Delta's connector router is
# read-only (GET). Listing it here would encode a route Delta does not own.
PLAN_ENDPOINTS = {
    "/api/v2/validate": {"post"},
    "/api/v2/rules": {"get", "post"},
    "/api/v2/verdicts": {"get"},
    "/api/v2/dashboard/coverage": {"get"},
    "/api/v2/connectors": {"get"},
    "/api/v2/auth/login": {"post"},
}


def _operations():
    from app.main import app

    schema = app.openapi()
    found = {}

    for path, methods in schema["paths"].items():
        for method in methods:
            if method.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE"}:
                found.setdefault(path, set()).add(method.lower())

    return found


def test_every_plan_endpoint_resolves():
    operations = _operations()

    missing = []

    for path, methods in PLAN_ENDPOINTS.items():
        if path not in operations:
            missing.append(path)
            continue
        missing.extend(f"{method.upper()} {path}" for method in methods - operations[path])

    assert not missing, (
        "B13: the plan's endpoint list does not resolve against the assembled "
        "app:\n  " + "\n  ".join(sorted(missing))
    )


def test_validate_is_not_nested_under_a_validator_prefix():
    """The specific regression: the path must be flat, not `/validator/validate`."""

    operations = _operations()

    assert "/api/v2/validator/validate" not in operations, (
        "B13: POST is back under /api/v2/validator/validate; the plan's "
        "documented path is POST /api/v2/validate"
    )
