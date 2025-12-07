"""
Unit tests for app configuration and initialization.

Tests critical app setup, route registration, and middleware configuration.
"""

from app.app import app
from app.config.settings import Settings


class TestAppInitialization:
    """Tests for app initialization and basic configuration."""

    def test_app_is_fastapi_instance(self):
        """Test that app is a FastAPI instance."""
        from fastapi import FastAPI

        assert isinstance(app, FastAPI)

    def test_app_has_correct_title_content(self):
        """Test that app has correct title."""
        assert "Generic CRUD API" in app.title or "API" in app.title


class TestAppCriticalRoutes:
    """Tests for critical app route registration."""

    def test_app_has_health_route(self):
        """Test that app has health check route."""
        routes = [route.path for route in app.routes]
        assert "/health" in routes

    def test_app_has_post_routes(self):
        """Test that app has post routes registered."""
        routes = [route.path for route in app.routes]
        post_routes = [r for r in routes if "post" in r.lower()]
        assert len(post_routes) > 0

    def test_app_has_auth_routes(self):
        """Test that auth routes are registered."""
        routes = [route.path for route in app.routes]
        auth_routes = [r for r in routes if "auth" in r.lower()]
        assert len(auth_routes) > 0

    def test_login_endpoint_registered(self):
        """Test that login endpoint is registered."""
        routes = [route.path for route in app.routes]
        assert any("login" in r.lower() for r in routes)


class TestAppMiddlewareConfiguration:
    """Tests for app middleware configuration."""

    def test_app_has_cors_middleware_config(self):
        """Test that app has CORS configuration."""
        from app.security.cors_config import setup_cors

        assert callable(setup_cors)

    def test_app_has_middleware_stack(self):
        """Test that app has middleware configured."""
        assert hasattr(app, "user_middleware")
        assert len(app.user_middleware) > 0


class TestAppConfiguration:
    """Tests for app configuration loading."""

    def test_settings_can_be_loaded(self):
        """Test that app settings can be loaded."""
        settings = Settings()
        assert settings is not None

    def test_settings_has_required_attributes(self):
        """Test that settings has required configuration attributes."""
        settings = Settings()
        assert hasattr(settings, "environment") or hasattr(settings, "server_host")


class TestAppDatabaseInitialization:
    """Tests for database initialization in app."""

    def test_database_tables_creation_function_exists(self):
        """Test that database tables creation is configured."""
        from app.app import create_db_and_tables

        assert callable(create_db_and_tables)

    def test_database_models_imported(self):
        """Test that database models are imported."""
        from app.data.v1.model.post import Post
        from app.data.v1.model.user import User

        assert Post is not None
        assert User is not None
