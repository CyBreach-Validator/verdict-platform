from datetime import datetime, timedelta

from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer


# Secret key used to sign JWT tokens
SECRET_KEY = "cybreach_validator_secret_key"

# JWT signing algorithm
ALGORITHM = "HS256"

# Token expiration time (minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict):
    """
    Create a JWT access token.
    """

    to_encode = data.copy()

    expire = datetime.utcnow() + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return encoded_jwt


def verify_access_token(token: str):
    print("========== JWT DEBUG ==========")
    print("Received Token:", token)

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        print("Decoded Payload:", payload)

        username = payload.get("sub")

        if username is None:
            print("No 'sub' found in token")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

        return payload

    except JWTError as e:
        print("JWT Error:", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid or expired"
        )


# OAuth2 configuration for Swagger authorization
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Get current authenticated user from JWT token.
    """

    payload = verify_access_token(token)

    username = payload.get("sub")

    return username