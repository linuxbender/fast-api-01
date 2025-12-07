"""
Middleware for JWT token validation and expiration checking.

This middleware validates JWT tokens from Authorization header or cookies,
checks if they are expired, and returns redirect information if needed.
"""

from datetime import UTC, datetime

from fastapi import Request
from jose import JWTError, jwt
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse, Response

from app.config.logger import get_logger
from app.config.settings import get_settings
from app.security.jwt import DEFAULT_ALGORITHM

logger = get_logger(__name__)


class JWTValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware that validates JWT tokens and checks for expiration.

    Checks tokens in:
    1. Authorization header (Bearer scheme)
    2. HTTP-Only Cookie named 'access_token'

    Returns redirect information if token is expired.
    """

    # Routes that don't require token validation
    EXCLUDED_ROUTES = {
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/login",
        "/register",
        "/api/v1/login",
        "/api/v1/register",
    }

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and validate JWT token.

        Args:
            request: The incoming request
            call_next: The next middleware/handler

        Returns:
            Response or redirect information if token is expired
        """
        # Skip validation for excluded routes
        if self._should_skip_validation(request.url.path):
            return await call_next(request)

        # Get token from request
        token = self._extract_token(request)

        if token is None:
            # No token found - let other middleware/dependencies handle it
            return await call_next(request)

        # Validate token and check expiration
        token_status = self._validate_token(token)

        if token_status["is_expired"]:
            logger.warning(
                f"Token expired for request: {request.method} {request.url.path}",
                extra={
                    "expired_at": token_status.get("exp"),
                    "email": token_status.get("email"),
                },
            )

            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Token expired",
                    "error_code": "TOKEN_EXPIRED",
                    "redirect_to": "/login",
                    "expired_at": token_status.get("exp"),
                    "user_email": token_status.get("email"),
                },
            )

        if token_status["is_invalid"]:
            logger.warning(
                f"Invalid token for request: {request.method} {request.url.path}"
            )

            return JSONResponse(
                status_code=401,
                content={
                    "detail": "Invalid token",
                    "error_code": "INVALID_TOKEN",
                    "redirect_to": "/login",
                },
            )

        # Token is valid, proceed with request
        return await call_next(request)

    def _should_skip_validation(self, path: str) -> bool:
        """
        Check if the route should skip JWT validation.

        Args:
            path: Request path

        Returns:
            True if validation should be skipped, False otherwise
        """
        for excluded_route in self.EXCLUDED_ROUTES:
            if path == excluded_route or path.startswith(excluded_route + "/"):
                return True
        return False

    def _extract_token(self, request: Request) -> str | None:
        """
        Extract JWT token from request.

        Checks in order:
        1. Authorization header (Bearer scheme)
        2. access_token cookie

        Args:
            request: The incoming request

        Returns:
            Token string or None if not found
        """
        # Try Authorization header first
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            return auth_header[7:]  # Remove "Bearer " prefix

        # Try cookie
        token_cookie = request.cookies.get("access_token")
        if token_cookie:
            # Cookie might contain "bearer <token>", extract the token
            if token_cookie.startswith("bearer "):
                return token_cookie[7:]
            return token_cookie

        return None

    def _validate_token(self, token: str) -> dict:
        """
        Validate JWT token and check expiration.

        Args:
            token: JWT token to validate

        Returns:
            Dictionary with validation status:
            {
                "is_valid": bool,
                "is_expired": bool,
                "is_invalid": bool,
                "exp": int (unix timestamp),
                "email": str,
            }
        """
        try:
            # Decode without verification of expiration first
            # to check if token is expired
            unverified_payload = jwt.get_unverified_claims(token)
            exp_timestamp = unverified_payload.get("exp")

            # Check if token is expired
            if exp_timestamp:
                exp_datetime = datetime.fromtimestamp(exp_timestamp, tz=UTC)
                is_expired = datetime.now(UTC) > exp_datetime

                if is_expired:
                    return {
                        "is_valid": False,
                        "is_expired": True,
                        "is_invalid": False,
                        "exp": exp_timestamp,
                        "email": unverified_payload.get("email"),
                    }

            # Now verify with expiration check
            settings = get_settings()
            payload = jwt.decode(
                token,
                settings.secret_key,
                algorithms=[DEFAULT_ALGORITHM],
            )

            return {
                "is_valid": True,
                "is_expired": False,
                "is_invalid": False,
                "exp": payload.get("exp"),
                "email": payload.get("email"),
            }

        except JWTError as e:
            logger.debug(f"JWT validation error: {str(e)}")
            return {
                "is_valid": False,
                "is_expired": False,
                "is_invalid": True,
                "exp": None,
                "email": None,
            }
