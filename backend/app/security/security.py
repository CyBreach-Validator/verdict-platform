import os
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

# M7 / m7: this used to be the literal string "cybreach_validator_secret_key",
# committed to the repository. Anyone with read access to the repo could mint
# an admin token, and rotating the key meant editing code and redeploying.
#
# There is deliberately no fallback default. An empty value is not a safe
# default, it is an unusable one: the module still imports (the CI job "the app
# must import with only DATABASE_URL set" depends on that, and it is the proof
# that no secret is baked into the import path), but the first attempt to sign
# or verify a token raises instead of silently signing with a key every
# deployment shares.
SECRET_KEY = os.environ.get("SECRET_KEY", "")

ALGORITHM = "HS256"

ACCESS_TOKEN_EXPIRE_MINUTES = int(
    os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
)


def _require_secret_key() -> str:
    if not SECRET_KEY:
        raise RuntimeError(
            "SECRET_KEY is not set. Delta signs JWTs with HS256 and refuses to "
            "use a built-in key, because a hardcoded default would let anyone "
            "who has read the source forge a token. Set SECRET_KEY in the "
            "environment (see .env.example) and restart the process."
        )

    return SECRET_KEY


def create_access_token(data: dict):
    """
    Create a JWT access token.
    """

    to_encode = data.copy()

    expire = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        _require_secret_key(),
        algorithm=ALGORITHM
    )

    return encoded_jwt


def verify_access_token(token: str):
    # The previous implementation printed every received token and the whole
    # decoded payload to stdout. That writes live bearer tokens into container
    # logs, which is the one place a token must never end up: anyone with log
    # access could replay them until expiry.
    try:
        payload = jwt.decode(
            token,
            _require_secret_key(),
            algorithms=[ALGORITHM]
        )
    except JWTError:
        # Deliberately not chained into the response: the specific jose error
        # ("Signature verification failed" vs "Signature has expired") tells an
        # attacker which of their guesses was structurally right.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired"
        )

    username = payload.get("sub")

    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )

    return payload


# `tokenUrl` must match the mounted prefix, otherwise the Swagger "Authorize"
# button posts to a 404 and the flow appears broken.
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/api/v2/auth/login"
)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user from JWT token.
    """

    payload = verify_access_token(token)

    return payload.get("sub")
