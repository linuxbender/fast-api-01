"""
Middleware for handling correlation IDs in FastAPI requests.

This middleware automatically generates a correlation ID for each request
and makes it available throughout the request lifecycle.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from app.config.logger import generate_correlation_id, set_correlation_id, get_logger

logger = get_logger(__name__)


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """
    Middleware that manages correlation IDs for requests.

    Each request either gets a new correlation ID or uses one provided
    in the X-Correlation-ID header.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process the request and set correlation ID.

        Args:
            request: The incoming request
            call_next: The next middleware/handler

        Returns:
            The response with correlation ID header
        """
        # Get correlation ID from header or generate new one
        correlation_id = request.headers.get(
            "X-Correlation-ID",
            generate_correlation_id(),
        )

        # Set correlation ID in context for this request
        set_correlation_id(correlation_id)

        logger.info(
            f"Request started: {request.method} {request.url.path}",
            extra={"correlation_id": correlation_id},
        )

        try:
            # Call next middleware/handler
            response = await call_next(request)

            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id

            logger.info(
                f"Request completed: {request.method} {request.url.path} "
                f"Status={response.status_code}",
                extra={"correlation_id": correlation_id},
            )

            return response

        except Exception as exc:
            logger.error(
                f"Request failed: {request.method} {request.url.path} - {str(exc)}",
                extra={"correlation_id": correlation_id},
                exc_info=True,
            )
            raise
