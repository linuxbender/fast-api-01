"""
Environment Configuration Management

Manages application settings from environment variables and .env file.
Supports development, testing, and production environments.
"""

from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings from environment variables."""

    # Environment
    environment: str = "development"

    # Server Configuration
    server_host: str = "0.0.0.0"
    server_port: int = 8000
    server_reload: bool = True

    # HTTPS/SSL Configuration
    use_https: bool = False
    ssl_keyfile: str | None = None
    ssl_certfile: str | None = None

    # Database
    database_url: str = "sqlite:///app.db"

    # Logging
    log_level: str = "INFO"

    # CORS Configuration
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    cors_allow_headers: list[str] = ["*"]

    class Config:
        """Pydantic settings configuration."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


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


def should_use_https() -> bool:
    """Check if HTTPS should be used.

    Returns:
        True if certificate files exist
    """
    settings = get_settings()

    # Check if certificate files exist
    if settings.ssl_keyfile and settings.ssl_certfile:
        key_exists = Path(settings.ssl_keyfile).exists()
        cert_exists = Path(settings.ssl_certfile).exists()
        return key_exists and cert_exists

    return False


if __name__ == "__main__":
    """Display current settings when run as script."""
    settings = get_settings()
    print("📋 Current Settings:")
    print("=" * 50)
    for key, value in settings.dict().items():
        if "password" not in key.lower() and "token" not in key.lower():
            print(f"  {key}: {value}")
    print("=" * 50)
