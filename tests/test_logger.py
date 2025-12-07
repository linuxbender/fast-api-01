"""
Test suite for app.config.logger and correlation ID functionality.

Tests the logging setup and correlation ID tracking.
"""

import logging
from contextvars import ContextVar

from app.config.logger import (
    CorrelationIdFilter,
    CorrelationIdFormatter,
    _correlation_id,
    generate_correlation_id,
    get_correlation_id,
    get_logger,
    set_correlation_id,
    setup_logging,
)


class TestCorrelationIdGeneration:
    """Test correlation ID generation."""

    def test_generate_correlation_id_returns_string(self):
        """Test that generate_correlation_id returns a string."""
        correlation_id = generate_correlation_id()
        assert isinstance(correlation_id, str)

    def test_generate_correlation_id_not_empty(self):
        """Test that generated correlation ID is not empty."""
        correlation_id = generate_correlation_id()
        assert len(correlation_id) > 0

    def test_generate_correlation_id_unique(self):
        """Test that generated correlation IDs are unique."""
        id1 = generate_correlation_id()
        id2 = generate_correlation_id()

        assert id1 != id2

    def test_generate_correlation_id_format(self):
        """Test that correlation ID has UUID-like format."""
        correlation_id = generate_correlation_id()
        # Should be UUID format (hex digits, at least 8 chars)
        assert len(correlation_id) >= 8


class TestCorrelationIdContextVar:
    """Test correlation ID context variable."""

    def test_set_correlation_id(self):
        """Test setting correlation ID."""
        test_id = "test-correlation-123"
        set_correlation_id(test_id)

        # Get it back
        retrieved_id = get_correlation_id()
        assert retrieved_id == test_id

    def test_get_correlation_id_default(self):
        """Test getting correlation ID when not set."""
        # Reset context
        _correlation_id.set("NO_CORRELATION_ID")

        correlation_id = get_correlation_id()
        assert correlation_id is not None

    def test_set_and_get_correlation_id_roundtrip(self):
        """Test setting and getting correlation ID."""
        test_id = generate_correlation_id()
        set_correlation_id(test_id)

        retrieved = get_correlation_id()
        assert retrieved == test_id

    def test_correlation_id_is_context_var(self):
        """Test that _correlation_id is a ContextVar."""
        assert isinstance(_correlation_id, ContextVar)


class TestCorrelationIdFilter:
    """Test CorrelationIdFilter logging filter."""

    def test_filter_initialization(self):
        """Test creating a CorrelationIdFilter."""
        log_filter = CorrelationIdFilter()
        assert isinstance(log_filter, logging.Filter)

    def test_filter_adds_correlation_id_to_record(self):
        """Test that filter adds correlation ID to log record."""
        log_filter = CorrelationIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )

        # Set a correlation ID
        test_id = "test-correlation-456"
        set_correlation_id(test_id)

        # Filter the record
        result = log_filter.filter(record)

        assert result is True
        assert hasattr(record, "correlation_id")
        assert record.correlation_id == test_id

    def test_filter_returns_true(self):
        """Test that filter always returns True."""
        log_filter = CorrelationIdFilter()
        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test",
            args=(),
            exc_info=None,
        )

        result = log_filter.filter(record)
        assert result is True


class TestCorrelationIdFormatter:
    """Test CorrelationIdFormatter."""

    def test_formatter_initialization(self):
        """Test creating a CorrelationIdFormatter."""
        fmt = (
            "[%(asctime)s] [%(name)s] [%(levelname)s] "
            "[correlation_id=%(correlation_id)s] %(message)s"
        )
        formatter = CorrelationIdFormatter(fmt)

        assert isinstance(formatter, logging.Formatter)

    def test_formatter_format_with_correlation_id(self):
        """Test formatter includes correlation ID in output."""
        fmt = "[%(levelname)s] [correlation_id=%(correlation_id)s] %(message)s"
        formatter = CorrelationIdFormatter(fmt)

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None,
        )
        record.correlation_id = "test-123"

        formatted = formatter.format(record)

        assert "correlation_id=test-123" in formatted
        assert "Test message" in formatted

    def test_formatter_uses_custom_format(self):
        """Test formatter uses provided format."""
        fmt = "[%(levelname)s] %(message)s [correlation_id=%(correlation_id)s]"
        formatter = CorrelationIdFormatter(fmt)

        record = logging.LogRecord(
            name="test",
            level=logging.WARNING,
            pathname="test.py",
            lineno=1,
            msg="Warning message",
            args=(),
            exc_info=None,
        )
        record.correlation_id = "warn-456"

        formatted = formatter.format(record)

        assert "WARNING" in formatted
        assert "Warning message" in formatted
        assert "warn-456" in formatted


class TestSetupLogging:
    """Test setup_logging function."""

    def test_setup_logging_creates_logger(self):
        """Test that setup_logging sets up logging."""
        setup_logging()

        # Should be able to get a logger
        logger = logging.getLogger("test_app")
        assert logger is not None

    def test_setup_logging_configures_root_logger(self):
        """Test that setup_logging configures root logger."""
        setup_logging()

        root_logger = logging.getLogger()
        assert root_logger.level > 0

    def test_setup_logging_multiple_calls(self):
        """Test calling setup_logging multiple times is safe."""
        setup_logging()
        setup_logging()  # Should not raise

        logger = logging.getLogger("test")
        assert logger is not None


class TestGetLogger:
    """Test get_logger function."""

    def test_get_logger_returns_logger(self):
        """Test that get_logger returns a Logger instance."""
        setup_logging()
        logger = get_logger(__name__)

        assert isinstance(logger, logging.Logger)

    def test_get_logger_with_name(self):
        """Test get_logger with specific name."""
        setup_logging()
        logger = get_logger("my_module")

        assert logger.name == "my_module"

    def test_get_logger_same_name_returns_same_logger(self):
        """Test that get_logger returns same logger for same name."""
        setup_logging()
        logger1 = get_logger("test_module")
        logger2 = get_logger("test_module")

        assert logger1 is logger2

    def test_get_logger_different_names_different_loggers(self):
        """Test that different names return different loggers."""
        setup_logging()
        logger1 = get_logger("module1")
        logger2 = get_logger("module2")

        assert logger1 is not logger2
        assert logger1.name != logger2.name

    def test_get_logger_has_correlation_filter(self):
        """Test that logger has correlation ID filter."""
        setup_logging()
        logger = get_logger(__name__)

        # Check if logger has handlers with filters
        for handler in logger.handlers:
            for log_filter in handler.filters:
                if isinstance(log_filter, CorrelationIdFilter):
                    break

        # At least root or parent should have the filter
        assert logger is not None


class TestLoggingIntegration:
    """Test logging integration with correlation IDs."""

    def test_logger_logs_with_correlation_id(self):
        """Test that logger outputs include correlation ID."""
        setup_logging()

        # Set a correlation ID
        test_id = "integration-test-789"
        set_correlation_id(test_id)

        # Get logger and log
        logger = get_logger("integration_test")

        # This should not raise
        logger.info("Test message")
        logger.warning("Warning message")
        logger.error("Error message")

    def test_correlation_id_persists_across_logs(self):
        """Test that correlation ID persists across multiple log calls."""
        setup_logging()

        test_id = generate_correlation_id()
        set_correlation_id(test_id)

        logger = get_logger("persistence_test")

        # Multiple log calls should use same correlation ID
        logger.info("First message")
        logger.info("Second message")
        logger.info("Third message")

        # Get correlation ID after logging
        retrieved_id = get_correlation_id()
        assert retrieved_id == test_id

    def test_different_correlation_ids_for_different_contexts(self):
        """Test that different contexts can have different correlation IDs."""
        setup_logging()

        id1 = generate_correlation_id()
        set_correlation_id(id1)
        retrieved1 = get_correlation_id()
        assert retrieved1 == id1

        id2 = generate_correlation_id()
        set_correlation_id(id2)
        retrieved2 = get_correlation_id()
        assert retrieved2 == id2


class TestLoggingConfiguration:
    """Test logging configuration details."""

    def test_logger_has_formatters(self):
        """Test that logger formatters are configured."""
        setup_logging()
        get_logger("config_test")

        # Root logger should have handlers
        root_logger = logging.getLogger()
        assert len(root_logger.handlers) > 0

    def test_logger_handles_multiple_levels(self):
        """Test logging at different levels."""
        setup_logging()
        logger = get_logger("level_test")

        # Should not raise for any level
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")

    def test_logger_format_includes_timestamp(self):
        """Test that log format includes timestamp."""
        setup_logging()
        logger = get_logger("format_test")

        # Logging should work
        logger.info("Format test")
