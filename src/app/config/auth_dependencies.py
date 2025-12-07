"""Authentication dependencies for FastAPI."""

from fastapi import Cookie, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.security.jwt import verify_access_token

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),  # noqa: B008
    access_token: str | None = Cookie(None),  # noqa: B008
):
    """Get current authenticated user from JWT token.

    Token can be provided via:
    1. HTTP Authorization header (Bearer scheme)
    2. HTTP-Only Cookie named 'access_token'

    Args:
        credentials: HTTP Bearer credentials
        access_token: JWT token from HTTP-Only cookie

    Returns:
        Token data with user information

    Raises:
        HTTPException: If token is invalid or missing
    """
    token = None

    # Try Bearer token from Authorization header first
    if credentials is not None and isinstance(credentials, HTTPAuthorizationCredentials):
        token = credentials.credentials
    # Fall back to cookie token
    elif access_token is not None:
        # Cookie contains "bearer <token>", extract the token
        if access_token.startswith("bearer "):
            token = access_token[7:]  # Remove "bearer " prefix
        else:
            token = access_token

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_data = verify_access_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security_scheme),  # noqa: B008
    access_token: str | None = Cookie(None),  # noqa: B008
):
    """Get current authenticated user from JWT token (optional).

    Token can be provided via:
    1. HTTP Authorization header (Bearer scheme)
    2. HTTP-Only Cookie named 'access_token'

    Args:
        credentials: HTTP Bearer credentials
        access_token: JWT token from HTTP-Only cookie

    Returns:
        Token data with user information or None if not authenticated
    """
    token = None

    # Try Bearer token from Authorization header first
    if credentials is not None and isinstance(credentials, HTTPAuthorizationCredentials):
        token = credentials.credentials
    # Fall back to cookie token
    elif access_token is not None:
        # Cookie contains "bearer <token>", extract the token
        if access_token.startswith("bearer "):
            token = access_token[7:]  # Remove "bearer " prefix
        else:
            token = access_token

    if token is None:
        return None

    token_data = verify_access_token(token)

    return token_data
