"""
Unit tests for MailService with fastapi-mail integration.

Tests email sending functionality in isolation by mocking FastMail and Settings.
Only mocked unit tests - no real SMTP connections.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from app.service.mail_service import MailService


@pytest.fixture
def mock_settings(mocker):
    """Create mocked settings for mail configuration."""
    settings = MagicMock()
    settings.mail_from = "noreply@example.com"
    settings.mail_server = "smtp.gmail.com"
    settings.mail_port = 587
    settings.mail_username = "test@gmail.com"
    settings.mail_password = "app_password_123"
    settings.mail_starttls = True
    settings.mail_ssl = False
    settings.login_code_expiry_minutes = 15
    return settings


@pytest.fixture
def mail_service(mocker, mock_settings):
    """Create MailService with mocked settings."""
    mocker.patch("app.service.mail_service.get_settings", return_value=mock_settings)
    mocker.patch("app.service.mail_service.logger")
    return MailService()


class TestMailServiceInitialization:
    """Tests for MailService initialization."""

    def test_mail_service_initialization(self, mail_service, mock_settings):
        """Test MailService initializes with settings."""
        # Assert
        assert mail_service.settings == mock_settings
        assert mail_service._mail_config is None  # Lazy loading

    def test_mail_config_lazy_initialization(self, mail_service, mocker):
        """Test mail config is lazily initialized on first use."""
        # Arrange
        mock_connection_config = MagicMock()
        mocker.patch(
            "app.service.mail_service.ConnectionConfig",
            return_value=mock_connection_config,
        )

        # Act
        config = mail_service._get_mail_config()

        # Assert
        assert config is mock_connection_config
        assert mail_service._mail_config is mock_connection_config


class TestLoginCodeEmailGeneration:
    """Tests for login code email body generation."""

    def test_plain_text_body_contains_code(self, mail_service):
        """Test plain text body contains the login code."""
        # Arrange
        code = "123456"

        # Act
        body = mail_service._generate_login_code_body(code)

        # Assert
        assert code in body
        assert "Login Code" in body
        assert "do not share" in body.lower()

    def test_plain_text_body_contains_expiry_info(self, mail_service, mock_settings):
        """Test plain text body contains expiry information."""
        # Arrange
        code = "789012"
        mock_settings.login_code_expiry_minutes = 20

        # Act
        body = mail_service._generate_login_code_body(code)

        # Assert
        assert "20 minutes" in body

    def test_html_body_contains_code(self, mail_service):
        """Test HTML body contains the login code."""
        # Arrange
        code = "654321"

        # Act
        html = mail_service._generate_login_code_html(code)

        # Assert
        assert code in html
        assert "<html>" in html
        assert "</html>" in html
        assert "Login Code" in html

    def test_html_body_contains_expiry_info(self, mail_service, mock_settings):
        """Test HTML body contains expiry information."""
        # Arrange
        code = "555555"
        mock_settings.login_code_expiry_minutes = 10

        # Act
        html = mail_service._generate_login_code_html(code)

        # Assert
        # Check for expiry info (may be split across lines after formatting)
        assert "10" in html and "minutes" in html

    def test_html_body_has_styling(self, mail_service):
        """Test HTML body includes styling."""
        # Arrange
        code = "111111"

        # Act
        html = mail_service._generate_login_code_html(code)

        # Assert
        assert "style=" in html
        assert "font-family" in html
        assert "color:" in html


@pytest.mark.asyncio
class TestSendLoginCodeEmail:
    """Tests for sending login code emails."""

    async def test_send_login_code_email_success(self, mocker, mail_service):
        """Test successful login code email sending."""
        # Arrange
        email = "user@example.com"
        code = "123456"
        mock_fastmail = AsyncMock()
        mock_connection_config = MagicMock()
        mocker.patch(
            "app.service.mail_service.ConnectionConfig",
            return_value=mock_connection_config,
        )
        mocker.patch(
            "app.service.mail_service.FastMail", return_value=mock_fastmail
        )

        # Act
        result = await mail_service.send_login_code_email(email, code)

        # Assert
        assert result is True
        mock_fastmail.send_message.assert_called_once()

    async def test_send_login_code_email_handles_exception(self, mocker, mail_service):
        """Test login code email sending handles exceptions gracefully."""
        # Arrange
        email = "user@example.com"
        code = "123456"
        mock_fastmail = AsyncMock()
        mock_fastmail.send_message.side_effect = Exception("SMTP Error")
        mock_connection_config = MagicMock()
        mocker.patch(
            "app.service.mail_service.ConnectionConfig",
            return_value=mock_connection_config,
        )
        mocker.patch(
            "app.service.mail_service.FastMail", return_value=mock_fastmail
        )

        # Act
        result = await mail_service.send_login_code_email(email, code)

        # Assert
        assert result is False


@pytest.mark.asyncio
class TestSendGenericEmail:
    """Tests for sending generic emails."""

    async def test_send_email_success(self, mocker, mail_service):
        """Test successful generic email sending."""
        # Arrange
        email = "recipient@example.com"
        subject = "Test Subject"
        body = "Test email body"
        mock_fastmail = AsyncMock()
        mock_connection_config = MagicMock()
        mocker.patch(
            "app.service.mail_service.ConnectionConfig",
            return_value=mock_connection_config,
        )
        mocker.patch(
            "app.service.mail_service.FastMail", return_value=mock_fastmail
        )

        # Act
        result = await mail_service.send_email(email, subject, body)

        # Assert
        assert result is True
        mock_fastmail.send_message.assert_called_once()

    async def test_send_email_with_html(self, mocker, mail_service):
        """Test email sending with HTML content."""
        # Arrange
        email = "recipient@example.com"
        subject = "HTML Email"
        body = "Plain text version"
        html = "<html><body>HTML version</body></html>"
        mock_fastmail = AsyncMock()
        mock_connection_config = MagicMock()
        mocker.patch(
            "app.service.mail_service.ConnectionConfig",
            return_value=mock_connection_config,
        )
        mocker.patch(
            "app.service.mail_service.FastMail", return_value=mock_fastmail
        )

        # Act
        result = await mail_service.send_email(email, subject, body, html=html)

        # Assert
        assert result is True

    async def test_send_email_no_credentials_returns_false(
        self, mocker, mock_settings
    ):
        """Test email sending fails gracefully when credentials not configured."""
        # Arrange
        mock_settings.mail_username = ""  # No credentials
        mocker.patch("app.service.mail_service.get_settings", return_value=mock_settings)
        mock_logger = mocker.patch("app.service.mail_service.logger")
        service = MailService()

        # Act
        result = await service.send_email(
            "recipient@example.com", "Subject", "Body"
        )

        # Assert
        assert result is False
        mock_logger.warning.assert_called_once()

    async def test_send_email_handles_exception(self, mocker, mail_service):
        """Test email sending handles exceptions gracefully."""
        # Arrange
        mock_fastmail = AsyncMock()
        mock_fastmail.send_message.side_effect = Exception("SMTP Connection Error")
        mock_connection_config = MagicMock()
        mocker.patch(
            "app.service.mail_service.ConnectionConfig",
            return_value=mock_connection_config,
        )
        mocker.patch(
            "app.service.mail_service.FastMail", return_value=mock_fastmail
        )

        # Act
        result = await mail_service.send_email(
            "user@example.com", "Subject", "Body"
        )

        # Assert
        assert result is False


@pytest.mark.asyncio
class TestMailConfigurationMappings:
    """Tests for fastapi-mail ConnectionConfig parameter mappings."""

    async def test_connection_config_receives_uppercase_parameters(
        self, mocker, mail_service
    ):
        """Test that ConnectionConfig is called with uppercase mail parameters."""
        # Arrange
        mock_connection_config = MagicMock()
        mock_config_class = mocker.patch(
            "app.service.mail_service.ConnectionConfig",
            return_value=mock_connection_config,
        )

        # Act
        mail_service._get_mail_config()

        # Assert - Verify ConnectionConfig was called with uppercase params
        mock_config_class.assert_called_once()
        call_kwargs = mock_config_class.call_args[1]
        assert call_kwargs["MAIL_USERNAME"] == "test@gmail.com"
        assert call_kwargs["MAIL_PASSWORD"] == "app_password_123"
        assert call_kwargs["MAIL_FROM"] == "noreply@example.com"
        assert call_kwargs["MAIL_PORT"] == 587
        assert call_kwargs["MAIL_SERVER"] == "smtp.gmail.com"
        assert call_kwargs["MAIL_STARTTLS"] is True
        assert call_kwargs["MAIL_SSL_TLS"] is False


class TestEmailGeneration:
    """Tests for email template generation logic."""

    def test_code_appears_in_both_plain_and_html(self, mail_service):
        """Test that code appears in both plain text and HTML versions."""
        # Arrange
        code = "999999"

        # Act
        plain = mail_service._generate_login_code_body(code)
        html = mail_service._generate_login_code_html(code)

        # Assert
        assert code in plain
        assert code in html
        assert len(plain) > 0
        assert len(html) > 0

    def test_expiry_minutes_matches_settings(self, mail_service, mock_settings):
        """Test that expiry minutes in email matches settings."""
        # Arrange
        code = "111111"
        mock_settings.login_code_expiry_minutes = 30

        # Act
        plain = mail_service._generate_login_code_body(code)
        html = mail_service._generate_login_code_html(code)

        # Assert
        assert "30 minutes" in plain
        # Check for expiry info in HTML (may be split across lines after formatting)
        assert "30" in html and "minutes" in html

