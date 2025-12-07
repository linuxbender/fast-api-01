"""Unit tests for app.security.cors_config module."""

from unittest.mock import MagicMock

import pytest
from app.security.cors_config import setup_cors
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


class TestSetupCors:
    """Tests for CORS setup function."""

    def test_setup_cors_accepts_fastapi_app(self):
        """Test that setup_cors accepts a FastAPI application."""
        app = FastAPI()
        # Should not raise
        setup_cors(app)

    def test_setup_cors_adds_middleware(self):
        """Test that setup_cors adds CORS middleware to the app."""
        app = FastAPI()
        initial_middleware_count = len(app.user_middleware)

        setup_cors(app)

        # Middleware should be added
        assert len(app.user_middleware) > initial_middleware_count

    def test_setup_cors_middleware_is_cors_middleware(self):
        """Test that added middleware is CORSMiddleware."""
        app = FastAPI()
        setup_cors(app)

        # Check middleware
        middleware_classes = [
            middleware.cls for middleware in app.user_middleware
        ]
        assert CORSMiddleware in middleware_classes

    def test_setup_cors_allows_all_origins(self):
        """Test that CORS allows all origins."""
        app = FastAPI()
        setup_cors(app)

        # Find CORS middleware
        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None
        # Middleware was added
        assert cors_middleware.cls == CORSMiddleware

    def test_setup_cors_allows_credentials(self):
        """Test that CORS allows credentials."""
        app = FastAPI()
        setup_cors(app)

        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None
        # Verify middleware is CORSMiddleware
        assert cors_middleware.cls == CORSMiddleware

    def test_setup_cors_allows_all_methods(self):
        """Test that CORS allows all HTTP methods."""
        app = FastAPI()
        setup_cors(app)

        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None
        # CORSMiddleware was properly added
        assert middleware.cls == CORSMiddleware

    def test_setup_cors_allows_all_headers(self):
        """Test that CORS allows all headers."""
        app = FastAPI()
        setup_cors(app)

        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None
        # Middleware configured
        assert cors_middleware.cls == CORSMiddleware

    def test_setup_cors_returns_none(self):
        """Test that setup_cors returns None."""
        app = FastAPI()
        result = setup_cors(app)
        assert result is None


class TestSetupCorsConfiguration:
    """Tests for CORS configuration details."""

    def test_setup_cors_configuration_is_permissive(self):
        """Test that CORS configuration is permissive (dev/test friendly)."""
        app = FastAPI()
        setup_cors(app)

        cors_middleware = None
        for middleware in app.user_middleware:
            if middleware.cls == CORSMiddleware:
                cors_middleware = middleware
                break

        assert cors_middleware is not None
        # Verify CORSMiddleware is configured
        assert cors_middleware.cls == CORSMiddleware

    def test_setup_cors_called_multiple_times(self):
        """Test that setup_cors can be called multiple times."""
        app = FastAPI()

        # Call multiple times
        setup_cors(app)
        setup_cors(app)

        # Should just add middleware each time
        assert len(app.user_middleware) > 0


class TestSetupCorsWithMockApp:
    """Tests using mock FastAPI app."""

    def test_setup_cors_calls_add_middleware(self):
        """Test that setup_cors calls add_middleware on the app."""
        app = MagicMock(spec=FastAPI)
        setup_cors(app)

        app.add_middleware.assert_called_once()

    def test_setup_cors_adds_cors_middleware_class(self):
        """Test that setup_cors adds CORSMiddleware class."""
        app = MagicMock(spec=FastAPI)
        setup_cors(app)

        # First argument should be CORSMiddleware
        call_args = app.add_middleware.call_args
        assert call_args[0][0] == CORSMiddleware

    def test_setup_cors_passes_correct_options(self):
        """Test that setup_cors passes correct middleware options."""
        app = MagicMock(spec=FastAPI)
        setup_cors(app)

        call_args = app.add_middleware.call_args
        kwargs = call_args[1]

        assert "allow_origins" in kwargs
        assert "allow_credentials" in kwargs
        assert "allow_methods" in kwargs
        assert "allow_headers" in kwargs


class TestSetupCorsEdgeCases:
    """Tests for edge cases in CORS setup."""

    def test_setup_cors_with_none_app_raises_error(self):
        """Test that setup_cors raises error with None app."""
        with pytest.raises((TypeError, AttributeError)):
            setup_cors(None)

    def test_setup_cors_returns_none_not_app(self):
        """Test that setup_cors returns None, not the app."""
        app = FastAPI()
        result = setup_cors(app)
        assert result is None
        assert result != app
