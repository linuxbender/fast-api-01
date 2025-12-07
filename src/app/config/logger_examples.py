"""
Example demonstrating how to use the global logger with correlation ID.

This shows how logging automatically tracks correlation IDs across
the application.
"""

from app.config.logger import get_correlation_id, get_logger, set_correlation_id

logger = get_logger(__name__)


def example_function_with_logging():
    """Example function showing logger usage with automatic correlation ID."""
    correlation_id = get_correlation_id()
    logger.info(f"Function called with correlation_id={correlation_id}")

    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")

    try:
        # Simulate some work
        result = 10 / 2
        logger.info(f"Operation successful: result={result}")
    except ZeroDivisionError as e:
        logger.error(f"Operation failed: {str(e)}", exc_info=True)


def example_with_manual_correlation_id():
    """Example showing manual correlation ID setting."""
    # Set a specific correlation ID
    set_correlation_id("MANUAL-CORR-ID-12345")

    logger.info("Processing with manual correlation ID")
    logger.info("All subsequent logs will have this correlation ID")

    # Call another function - it will use the same correlation ID
    example_function_with_logging()


if __name__ == "__main__":
    logger.info("Starting logger examples")

    # Example 1: Default correlation ID from context
    logger.info("=" * 60)
    logger.info("Example 1: Auto-generated correlation ID")
    logger.info("=" * 60)
    example_function_with_logging()

    # Example 2: Manual correlation ID
    logger.info("=" * 60)
    logger.info("Example 2: Manual correlation ID")
    logger.info("=" * 60)
    example_with_manual_correlation_id()

    logger.info("Examples completed")
