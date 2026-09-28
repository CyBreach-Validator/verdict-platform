import hmac
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.security.security import create_access_token

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

# M7 / m7: the credentials were the literals "admin" / "admin123" in the source
# tree, so the only account on the platform was readable by anyone with the
# repo, and the Swagger page shipped with working login credentials.
#
# `os.environ.get` with no default is intentional: `None` is not a credential,
# it is an unconfigured service. Login fails closed below rather than falling
# back to a well-known pair.
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Authenticate user and return JWT token.
    """

    if not ADMIN_USERNAME or not ADMIN_PASSWORD:
        raise HTTPException(
            status_code=503,
            detail=(
                "Authentication is not configured. Set ADMIN_USERNAME and "
                "ADMIN_PASSWORD in the environment and restart the process."
            )
        )

    # `hmac.compare_digest` on both fields: a plain `!=` comparison returns as
    # soon as it finds a differing byte, which leaks the length of the matching
    # prefix through response timing and makes an online guess cheaper.
    username_ok = hmac.compare_digest(
        form_data.username.encode("utf-8"),
        ADMIN_USERNAME.encode("utf-8"),
    )
    password_ok = hmac.compare_digest(
        form_data.password.encode("utf-8"),
        ADMIN_PASSWORD.encode("utf-8"),
    )

    if not (username_ok and password_ok):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token(
        data={
            "sub": form_data.username
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }
