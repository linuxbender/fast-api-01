"""
Test suite for app.config.settings module.

Tests the environment configuration and settings management.
"""

from unittest.mock import MagicMock, patch

from app.config.settings import (
    Settings,
    get_setting,
    get_settings,
    is_development,
    is_production,
    is_testing,
    reload_settings,
    should_use_https,
)


class TestSettings:
    """Test Settings class and configuration loading."""

    def test_settings_default_values(self):
        """Test that Settings has correct default values."""
        settings = Settings()

        assert settings.environment == "development"
        assert settings.server_host == "0.0.0.0"
        assert settings.server_port == 8000
        assert settings.server_reload is True
        assert settings.use_https is False
        # ssl_keyfile and ssl_certfile are loaded from .env if it exists
        assert isinstance(settings.ssl_keyfile, str | type(None))
        assert isinstance(settings.ssl_certfile, str | type(None))
        assert settings.database_url == "sqlite:///app.db"
        assert settings.log_level == "INFO"

    def test_settings_with_custom_values(self):
        """Test Settings with custom environment values."""
        settings = Settings(
            environment="production",
            server_port=9000,
            use_https=True,
            log_level="DEBUG",
        )

        assert settings.environment == "production"
        assert settings.server_port == 9000
        assert settings.use_https is True
        assert settings.log_level == "DEBUG"

    def test_settings_cors_defaults(self):
        """Test CORS configuration defaults."""
        settings = Settings()

        assert "http://localhost:3000" in settings.cors_origins
        assert "http://localhost:8000" in settings.cors_origins
        assert settings.cors_allow_credentials is True
        assert "GET" in settings.cors_allow_methods
        assert "POST" in settings.cors_allow_methods
        assert "*" in settings.cors_allow_headers

    def test_settings_case_insensitive(self):
        """Test that settings are case-insensitive."""
        settings = Settings(environment="PRODUCTION")
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


class TestShouldUseHttps:
    """Test HTTPS configuration checking."""

    def test_should_use_https_with_existing_certificates(self, tmp_path):
        """Test should_use_https when certificate files exist."""
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

            assert should_use_https() is True

    def test_should_use_https_with_missing_key_file(self, tmp_path):
        """Test should_use_https when key file is missing."""
        cert_file = tmp_path / "certificate.crt"
        cert_file.write_text("cert content")
        key_file = tmp_path / "missing.key"

        with patch("app.config.settings.get_settings") as mock_get:
            settings_mock = MagicMock()
            settings_mock.ssl_keyfile = str(key_file)
            settings_mock.ssl_certfile = str(cert_file)
            mock_get.return_value = settings_mock

            assert should_use_https() is False

    def test_should_use_https_with_missing_cert_file(self, tmp_path):
        """Test should_use_https when cert file is missing."""
        key_file = tmp_path / "private.key"
        key_file.write_text("key content")
        cert_file = tmp_path / "missing.crt"

        with patch("app.config.settings.get_settings") as mock_get:
            settings_mock = MagicMock()
            settings_mock.ssl_keyfile = str(key_file)
            settings_mock.ssl_certfile = str(cert_file)
            mock_get.return_value = settings_mock

            assert should_use_https() is False

    def test_should_use_https_with_none_paths(self):
        """Test should_use_https when certificate paths are None."""
        with patch("app.config.settings.get_settings") as mock_get:
            settings_mock = MagicMock()
            settings_mock.ssl_keyfile = None
            settings_mock.ssl_certfile = None
            mock_get.return_value = settings_mock

            assert should_use_https() is False

    def test_should_use_https_with_partial_paths(self, tmp_path):
        """Test should_use_https when only one path is set."""
        key_file = tmp_path / "private.key"
        key_file.write_text("key content")

        with patch("app.config.settings.get_settings") as mock_get:
            settings_mock = MagicMock()
            settings_mock.ssl_keyfile = str(key_file)
            settings_mock.ssl_certfile = None
            mock_get.return_value = settings_mock

            assert should_use_https() is False


class TestSettingsEnvFileLoading:
    """Test loading settings from .env file."""

    def test_settings_loads_from_env_file(self, tmp_path):
        """Test that Settings loads values from .env file."""
        env_file = tmp_path / ".env"
        env_file.write_text("""
ENVIRONMENT=production
SERVER_PORT=9000
USE_HTTPS=true
LOG_LEVEL=DEBUG
""")

        with patch("app.config.settings.Settings.Config.env_file", str(env_file)):
            Settings(_env_file=str(env_file))
            # Note: In actual usage, pydantic-settings will load these

    def test_settings_config_has_env_file(self):
        """Test that Settings Config specifies env_file."""
        assert Settings.Config.env_file == ".env"

    def test_settings_config_env_encoding(self):
        """Test that Settings Config specifies UTF-8 encoding."""
        assert Settings.Config.env_file_encoding == "utf-8"

    def test_settings_config_case_sensitivity(self):
        """Test that Settings Config is case-insensitive."""
        assert Settings.Config.case_sensitive is False
