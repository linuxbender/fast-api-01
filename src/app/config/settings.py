"""
Environment Configuration Management

Manages application settings from environment variables and .env file.
Supports development, testing, and production environments.

All critical settings (environment, SSL, CORS, log level) MUST be defined in .env files.
No defaults are provided - if a required setting is missing, the application will fail on startup.
Single Source of Truth: .env files are the source for all environment-specific configuration.
"""

from pathlib import Path

from pydantic import ConfigDict, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables and .env file.

    IMPORTANT: All critical settings (environment, SSL, CORS, log level) are REQUIRED.
    Missing values will cause validation errors on startup.
    This ensures no duplicate configuration and enforces .env as Single Source of Truth.
    """

    model_config = ConfigDict(env_file=".env", env_file_encoding="utf-8", case_sensitive=False)

    # Environment (REQUIRED - no default)
    environment: str = Field(..., description="Application Env (development, staging, production)")

    # Server Configuration (practical defaults for local development)
    server_host: str = Field(default="0.0.0.0", description="Server host address")
    server_port: int = Field(default=8000, description="Server port")
    server_reload: bool = Field(default=False, description="Enable server reload on file changes")

    # HTTPS/SSL Configuration (REQUIRED - no defaults)
    ssl_keyfile: str = Field(..., description="Path to SSL private key file")
    ssl_certfile: str = Field(..., description="Path to SSL certificate file")

    # Database (practical default for local development)
    database_url: str = Field(default="sqlite:///app.db", description="Database connection URL")

    # Logging (REQUIRED - no default)
    log_level: str = Field(..., description="Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)")

    # CORS Configuration (REQUIRED - no defaults)
    cors_origins: list[str] = Field(..., description="Allowed CORS origins")
    cors_allow_credentials: bool = Field(..., description="Allow CORS credentials")
    cors_allow_methods: list[str] = Field(..., description="Allowed HTTP methods for CORS")
    cors_allow_headers: list[str] = Field(..., description="Allowed headers for CORS")


# Global settings instance
_settings: Settings | None = None


def get_settings() -> Settings:
    """Get or create global settings instance.

    Returns:
        Application settings
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """Reload settings from environment/file.

    Returns:
        Reloaded application settings
    """
    global _settings
    _settings = Settings()
    return _settings


def get_setting(key: str, default: str | None = None) -> str | None:
    """Get a specific setting value.

    Args:
        key: Setting key name
        default: Default value if not found

    Returns:
        Setting value or default
    """
    settings = get_settings()
    return getattr(settings, key.lower(), default)


def is_development() -> bool:
    """Check if running in development mode.

    Returns:
        True if environment is development
    """
    return get_settings().environment.lower() == "development"


def is_production() -> bool:
    """Check if running in production mode.

    Returns:
        True if environment is production
    """
    return get_settings().environment.lower() == "production"


def is_testing() -> bool:
    """Check if running in testing mode.

    Returns:
        True if environment is testing
    """
    return get_settings().environment.lower() == "testing"


def has_ssl_certificates() -> bool:
    """Check if SSL certificate files exist.

    Returns:
        True if both key and certificate files exist
    """
    settings = get_settings()
    key_exists = Path(settings.ssl_keyfile).exists()
    cert_exists = Path(settings.ssl_certfile).exists()
    return key_exists and cert_exists


if __name__ == "__main__":
    """Display current settings when run as script."""
    settings = get_settings()
    print("📋 Current Settings:")
    print("=" * 50)
    for key, value in settings.dict().items():
        if "password" not in key.lower() and "token" not in key.lower():
            print(f"  {key}: {value}")
    print("=" * 50)
