"""Guard for B11: authentication coverage across the whole API.

The original defect was not a broken check -- `get_current_user` worked and was
applied to most routers. It was an omission: `users`, `connectors` and
`dashboard` never got it, so an anonymous caller could create accounts, list
every user, and read the connector inventory and detection statistics.

Enumerating routes by hand does not survive the next router someone adds, so
this test walks the assembled OpenAPI schema instead and fails if any operation
other than login is missing a security requirement.
"""

import os
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent

os.environ.setdefault(
    "DATABASE_URL", "postgresql://user:pass@localhost:5432/verdict_db"
)

sys.path.insert(0, str(BACKEND_DIR))

# The only endpoints that may be reachable without a token.
#
# FastAPI's own routes (`/docs`, `/redoc`, `/openapi.json`,
# `/docs/oauth2-redirect`) are deliberately absent: FastAPI does not list them
# in `app.openapi()["paths"]`, so this test can never observe them, and an
# allowlist entry that can never be observed would only rot unnoticed. They are
# ungated by design -- gating the docs would make the Swagger "Authorize"
# button unusable, since the token has to come from there.
PUBLIC_OPERATIONS = {
    ("/api/v2/auth/login", "post"),
    # Liveness probes. Both return a static dict and touch no data.
    ("/health", "get"),
    ("/", "get"),
}

# Paths that only exist when slowapi's limiter is enabled.
DOC_PATHS = {"/docs", "/redoc", "/openapi.json", "/docs/oauth2-redirect"}


def _operations():
    from app.main import app

    schema = app.openapi()
    found = {}

    for path, methods in schema["paths"].items():
        for method in methods:
            if method.upper() in {"GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"}:
                found[(path, method.lower())] = schema["paths"][path][method]

    return found


def test_public_allowlist_has_no_stale_entries():
    """Keeps PUBLIC_OPERATIONS honest in the other direction: an entry for a
    route that no longer exists would silently mask a future regression on that
    path."""

    operations = _operations()

    stale = [op for op in PUBLIC_OPERATIONS if op not in operations]

    assert not stale, (
        "PUBLIC_OPERATIONS lists routes that no longer exist, so they are not "
        f"being checked: {sorted(stale)}"
    )


def test_all_non_public_routes_require_authentication():
    from app.main import app

    schema = app.openapi()
    problems = []

    for (path, method), operation in _operations().items():
        if (path, method) in PUBLIC_OPERATIONS:
            continue

        if not operation.get("security"):
            problems.append(f"{method.upper()} {path}")

    assert not problems, (
        "B11: these routes are reachable without a JWT:\n  "
        + "\n  ".join(sorted(problems))
        + "\n\nAdd `dependencies=[Depends(get_current_user)]` to the router, or "
        "list the route in PUBLIC_OPERATIONS if it is genuinely public."
    )


def test_the_token_is_actually_verified(monkeypatch):
    """A dependency that resolved without checking the signature would satisfy
    `security` in the OpenAPI output while accepting a forged token."""

    from app.security import security

    # `SECRET_KEY` and the token TTL are read into module globals at import
    # time (deliberately: the process is meant to be restarted after changing
    # them), so these tests patch the attributes rather than the environment.
    monkeypatch.setattr(security, "SECRET_KEY", "unit-test-signing-key-not-real")

    from fastapi import HTTPException

    from app.security.security import verify_access_token

    for bad in ("not-a-jwt", "", "a.b.c", "eyJhbGciOiJIUzI1NiJ9.e30.bm90LWEtc2ln"):
        try:
            verify_access_token(bad)
        except HTTPException as exc:
            assert exc.status_code == 401, (
                f"a malformed or forged token produced {exc.status_code}, "
                "expected 401"
            )
        else:
            raise AssertionError(f"verify_access_token accepted {bad!r}")


def test_get_current_user_returns_the_token_subject(monkeypatch):
    from app.security import security

    monkeypatch.setattr(security, "SECRET_KEY", "unit-test-signing-key-not-real")

    token = security.create_access_token(data={"sub": "analyst-1"})

    # Called directly with the token, bypassing the Depends() plumbing, to
    # assert the identity is the verified `sub` claim.
    assert security.get_current_user(token) == "analyst-1"


def test_expired_token_is_refused(monkeypatch):
    """TTL enforcement, so a leaked token stops working."""

    from app.security import security

    monkeypatch.setattr(security, "SECRET_KEY", "unit-test-signing-key-not-real")
    monkeypatch.setattr(security, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)

    from fastapi import HTTPException

    token = security.create_access_token(data={"sub": "analyst-1"})

    try:
        security.verify_access_token(token)
    except HTTPException as exc:
        assert exc.status_code == 401
    else:
        raise AssertionError("an already-expired token was accepted")
