"""
Global logger configuration with Correlation ID support.

This module sets up logging with correlation IDs that are automatically
tracked through requests and included in all log messages.
"""

import logging
import sys
import uuid
from contextvars import ContextVar

# Context variable to store correlation ID for the current request
_correlation_id: ContextVar[str | None] = ContextVar("correlation_id", default=None)


def get_correlation_id() -> str | None:
    """Get the current correlation ID from context."""
    return _correlation_id.get()


def set_correlation_id(correlation_id: str) -> None:
    """Set the correlation ID for the current context."""
    _correlation_id.set(correlation_id)


def generate_correlation_id() -> str:
    """Generate a new correlation ID."""
    return str(uuid.uuid4())[:16]


class CorrelationIdFilter(logging.Filter):
    """Logging filter that adds correlation ID to log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        """Add correlation ID to the log record."""
        correlation_id = get_correlation_id()
        record.correlation_id = correlation_id or "NO_CORRELATION_ID"
        return True


class CorrelationIdFormatter(logging.Formatter):
    """Formatter that includes correlation ID in log messages."""

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        include_correlation_id: bool = True,
    ):
        """
        Initialize the formatter.

        Args:
            fmt: Log message format
            datefmt: Date format
            include_correlation_id: Whether to include correlation ID in logs
        """
        if include_correlation_id:
            if fmt is None:
                fmt = (
                    "[%(asctime)s] [%(name)s] [%(levelname)s] "
                    "[correlation_id=%(correlation_id)s] %(message)s"
                )
        else:
            if fmt is None:
                fmt = "[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s"

        super().__init__(fmt, datefmt)

    def format(self, record: logging.LogRecord) -> str:
        """Format the log record."""
        # Add correlation_id if not already present
        if not hasattr(record, "correlation_id"):
            record.correlation_id = get_correlation_id() or "NO_CORRELATION_ID"
        return super().format(record)


def setup_logging(
    level: int = logging.INFO,
    include_correlation_id: bool = True,
) -> logging.Logger:
    """
    Setup global logging configuration with correlation ID support.

    Args:
        level: Logging level (default: INFO)
        include_correlation_id: Whether to include correlation ID in logs

    Returns:
        Configured root logger
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)

    # Create formatter with correlation ID
    formatter = CorrelationIdFormatter(include_correlation_id=include_correlation_id)

    # Add filter to inject correlation ID
    console_handler.addFilter(CorrelationIdFilter())

    # Set formatter and add handler
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance with the given name.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Logger instance configured with correlation ID support
    """
    logger = logging.getLogger(name)
    # Ensure the logger has the correlation ID filter
    if not any(isinstance(f, CorrelationIdFilter) for f in logger.filters):
        logger.addFilter(CorrelationIdFilter())
    return logger


# Initialize logging on module import
setup_logging()
