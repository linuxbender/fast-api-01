"""
Test suite for app.config.settings module.

Tests the environment configuration and settings management.
"""

from unittest.mock import MagicMock, patch

import pytest

from app.config.settings import (
    Settings,
    get_setting,
    get_settings,
    has_ssl_certificates,
    is_development,
    is_production,
    is_testing,
    reload_settings,
)


class TestSettings:
    """Test Settings class and configuration loading."""

    def test_settings_with_all_required_values(self):
        """Test that Settings requires all CORS, SSL, and LOG_LEVEL values."""
        # Create settings with all required fields explicitly provided
        settings = Settings(
            _env_file=None,
            environment="development",
            server_host="0.0.0.0",
            server_port=8000,
            server_reload=True,
            ssl_keyfile="./certs/private.key",
            ssl_certfile="./certs/certificate.crt",
            database_url="sqlite:///app.db",
            log_level="INFO",
            cors_origins=["https://localhost:3000", "https://localhost:8000"],
            cors_allow_credentials=True,
            cors_allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            cors_allow_headers=["*"],
        )

        assert settings.environment == "development"
        assert settings.server_host == "0.0.0.0"
        assert settings.server_port == 8000
        assert settings.server_reload is True
        # SSL/TLS is required for all environments
        assert settings.ssl_keyfile == "./certs/private.key"
        assert settings.ssl_certfile == "./certs/certificate.crt"
        assert settings.database_url == "sqlite:///app.db"
        assert settings.log_level == "INFO"
        # CORS is required
        assert "https://localhost:3000" in settings.cors_origins
        assert "https://localhost:8000" in settings.cors_origins

    def test_settings_missing_required_cors_origins_raises_error(self):
        """Test that Settings raises ValidationError when CORS origins are missing."""
        from pydantic import ValidationError

        with patch.dict("os.environ", {}, clear=True):
            try:
                Settings(
                    _env_file=None,
                    environment="production",
                    ssl_keyfile="./certs/private.key",
                    ssl_certfile="./certs/certificate.crt",
                    log_level="DEBUG",
                    # Missing CORS fields
                )
                assert False, "Should have raised ValidationError"
            except ValidationError as e:
                # Should complain about missing CORS fields
                error_fields = {error["loc"][0] for error in e.errors()}
                assert "cors_origins" in error_fields
                assert "cors_allow_credentials" in error_fields
                assert "cors_allow_methods" in error_fields
                assert "cors_allow_headers" in error_fields

    def test_settings_missing_required_log_level_raises_error(self):
        """Test that Settings raises ValidationError when LOG_LEVEL is missing."""
        from pydantic import ValidationError

        with patch.dict("os.environ", {}, clear=True):
            try:
                Settings(
                    _env_file=None,
                    environment="production",
                    ssl_keyfile="./certs/private.key",
                    ssl_certfile="./certs/certificate.crt",
                    cors_origins=["https://example.com"],
                    cors_allow_credentials=True,
                    cors_allow_methods=["GET"],
                    cors_allow_headers=["*"],
                    # Missing log_level
                )
                assert False, "Should have raised ValidationError"
            except ValidationError as e:
                error_fields = {error["loc"][0] for error in e.errors()}
                assert "log_level" in error_fields

    def test_settings_case_insensitive(self):
        """Test that settings are case-insensitive."""
        settings = Settings(
            environment="PRODUCTION",
            ssl_keyfile="./certs/private.key",
            ssl_certfile="./certs/certificate.crt",
            log_level="DEBUG",
            cors_origins=["https://example.com"],
            cors_allow_credentials=True,
            cors_allow_methods=["GET"],
            cors_allow_headers=["*"],
        )
        assert settings.environment == "PRODUCTION"


class TestGetSettings:
    """Test global settings instance management."""

    def test_get_settings_returns_singleton(self):
        """Test that get_settings returns the same instance."""
        settings1 = get_settings()
        settings2 = get_settings()

        assert settings1 is settings2

    def test_get_settings_instance_type(self):
        """Test that get_settings returns Settings instance."""
        settings = get_settings()
        assert isinstance(settings, Settings)

    def test_reload_settings_creates_new_instance(self):
        """Test that reload_settings creates a new instance."""
        old_settings = get_settings()
        reloaded = reload_settings()

        # Should be different instances
        assert reloaded is not old_settings

    def test_reload_settings_returns_settings_instance(self):
        """Test that reload_settings returns Settings instance."""
        reloaded = reload_settings()
        assert isinstance(reloaded, Settings)


class TestGetSetting:
    """Test get_setting helper function."""

    def test_get_setting_existing_key(self):
        """Test getting an existing setting."""
        value = get_setting("server_host")
        assert value == "0.0.0.0"

    def test_get_setting_with_default(self):
        """Test get_setting returns default for non-existent key."""
        value = get_setting("nonexistent_key", "default_value")
        assert value == "default_value"

    def test_get_setting_case_insensitive(self):
        """Test that get_setting is case-insensitive."""
        value = get_setting("SERVER_HOST")
        assert value == "0.0.0.0"

    def test_get_setting_returns_none_without_default(self):
        """Test get_setting returns None for non-existent key without default."""
        value = get_setting("nonexistent_key")
        assert value is None


class TestEnvironmentCheckers:
    """Test environment checking functions."""

    def test_is_development(self):
        """Test is_development function."""
        with patch("app.config.settings.get_settings") as mock_get:
            mock_get.return_value.environment = "development"
            assert is_development() is True

            mock_get.return_value.environment = "production"
            assert is_development() is False

    def test_is_production(self):
        """Test is_production function."""
        with patch("app.config.settings.get_settings") as mock_get:
            mock_get.return_value.environment = "production"
            assert is_production() is True

            mock_get.return_value.environment = "development"
            assert is_production() is False

    def test_is_testing(self):
        """Test is_testing function."""
        with patch("app.config.settings.get_settings") as mock_get:
            mock_get.return_value.environment = "testing"
            assert is_testing() is True

            mock_get.return_value.environment = "development"
            assert is_testing() is False

    def test_is_development_case_insensitive(self):
        """Test that environment check is case-insensitive."""
        with patch("app.config.settings.get_settings") as mock_get:
            mock_get.return_value.environment = "DEVELOPMENT"
            assert is_development() is True


class TestSSLCertificates:
    """Test SSL certificate configuration checking."""

    def test_has_ssl_certificates_with_existing_certificates(self, tmp_path):
        """Test has_ssl_certificates when certificate files exist."""
        # Create temporary certificate files
        key_file = tmp_path / "private.key"
        cert_file = tmp_path / "certificate.crt"
        key_file.write_text("key content")
        cert_file.write_text("cert content")

        with patch("app.config.settings.get_settings") as mock_get:
            settings_mock = MagicMock()
            settings_mock.ssl_keyfile = str(key_file)
            settings_mock.ssl_certfile = str(cert_file)
            mock_get.return_value = settings_mock

            assert has_ssl_certificates() is True

    def test_has_ssl_certificates_with_missing_key_file(self, tmp_path):
        """Test has_ssl_certificates when key file is missing."""
        cert_file = tmp_path / "certificate.crt"
        cert_file.write_text("cert content")
        key_file = tmp_path / "missing.key"

        with patch("app.config.settings.get_settings") as mock_get:
            settings_mock = MagicMock()
            settings_mock.ssl_keyfile = str(key_file)
            settings_mock.ssl_certfile = str(cert_file)
            mock_get.return_value = settings_mock

            assert has_ssl_certificates() is False

    def test_has_ssl_certificates_with_missing_cert_file(self, tmp_path):
        """Test has_ssl_certificates when cert file is missing."""
        key_file = tmp_path / "private.key"
        key_file.write_text("key content")
        cert_file = tmp_path / "missing.crt"

        with patch("app.config.settings.get_settings") as mock_get:
            settings_mock = MagicMock()
            settings_mock.ssl_keyfile = str(key_file)
            settings_mock.ssl_certfile = str(cert_file)
            mock_get.return_value = settings_mock

            assert has_ssl_certificates() is False


class TestSettingsEnvFileLoading:
    """Test loading settings from .env file."""

    def test_settings_requires_all_env_variables(self, tmp_path):
        """Test that Settings raises error when required ENV variables are missing."""
        from pydantic import ValidationError

        env_file = tmp_path / ".env"
        env_file.write_text("""
ENVIRONMENT=production
SERVER_PORT=9000
LOG_LEVEL=DEBUG
SSL_KEYFILE=./certs/private.key
SSL_CERTFILE=./certs/certificate.crt
""")

        # Attempting to load with incomplete .env should fail
        with patch.dict("os.environ", {}, clear=True):
            with pytest.raises(ValidationError) as exc_info:
                Settings(_env_file=str(env_file))

            # Should complain about missing CORS fields
            error_fields = {error["loc"][0] for error in exc_info.value.errors()}
            assert "cors_origins" in error_fields
            assert "cors_allow_credentials" in error_fields

    def test_settings_loads_from_complete_env_file(self, tmp_path):
        """Test that Settings loads successfully with complete .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
ENVIRONMENT=production
SERVER_PORT=9000
LOG_LEVEL=DEBUG
SSL_KEYFILE=./certs/private.key
SSL_CERTFILE=./certs/certificate.crt
CORS_ORIGINS=["https://example.com"]
CORS_ALLOW_CREDENTIALS=true
CORS_ALLOW_METHODS=["GET","POST"]
CORS_ALLOW_HEADERS=["*"]
""")

        with patch.dict("os.environ", {}, clear=True):
            settings = Settings(_env_file=str(env_file))
            assert settings.environment == "production"
            assert settings.server_port == 9000
            assert settings.log_level == "DEBUG"

    def test_settings_config_has_env_file(self):
        """Test that Settings model_config specifies env_file."""
        assert Settings.model_config["env_file"] == ".env"

    def test_settings_config_env_encoding(self):
        """Test that Settings model_config specifies UTF-8 encoding."""
        assert Settings.model_config["env_file_encoding"] == "utf-8"

    def test_settings_config_case_sensitivity(self):
        """Test that Settings model_config is case-insensitive."""
        assert Settings.model_config["case_sensitive"] is False
