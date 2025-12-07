"""JWT token generation and validation."""

from datetime import UTC, datetime, timedelta

from jose import JWTError, jwt
from pydantic import BaseModel

from app.config.settings import get_settings

# Default algorithm (can be overridden)
DEFAULT_ALGORITHM = "HS256"


class TokenData(BaseModel):
    """JWT token payload data."""

    user_id: int
    email: str
    rights: list[str] = ["READ"]
    groups: list[str] = ["ACTIVE_USER"]


def create_access_token(
    data: dict,
    secret_key: str | None = None,
    algorithm: str = DEFAULT_ALGORITHM,
    expires_delta: timedelta | None = None,
) -> str:
    """Create JWT access token.

    Args:
        data: Token payload data
        secret_key: Secret key for token signing (uses settings if None)
        algorithm: Algorithm for token signing
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    settings = get_settings()
    if secret_key is None:
        secret_key = settings.secret_key

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(
            minutes=settings.access_token_expire_minutes
        )

    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})

    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_access_token(
    token: str,
    secret_key: str | None = None,
    algorithm: str = DEFAULT_ALGORITHM,
) -> TokenData | None:
    """Verify JWT access token.

    Args:
        token: JWT token to verify
        secret_key: Secret key for token verification (uses settings if None)
        algorithm: Algorithm for token verification

    Returns:
        Token data if valid, None otherwise
    """
    settings = get_settings()
    if secret_key is None:
        secret_key = settings.secret_key

    try:
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        user_id: int = payload.get("user_id")
        email: str = payload.get("email")

        if user_id is None or email is None:
            return None

        return TokenData(
            user_id=user_id,
            email=email,
            rights=payload.get("rights", ["READ"]),
            groups=payload.get("groups", ["ACTIVE_USER"]),
        )
    except JWTError:
        return None
