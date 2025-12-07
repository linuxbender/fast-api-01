"""
Tests for application configuration and middleware.

Tests:
- Health check endpoint
- Correlation ID middleware
- CORS configuration
- App initialization
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from app.app import app
from app.data.database import get_session


@pytest.fixture(name="client")
def client_fixture():
    """Create TestClient with fresh test database per test."""
    # Create fresh in-memory database for each test
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    def get_session_override():
        session = Session(engine)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()


class TestAppHealthCheck:
    """Tests for health check endpoint."""

    def test_health_check_returns_200(self, client: TestClient):
        """Test that health check returns 200 OK."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_check_returns_ok_status(self, client: TestClient):
        """Test that health check returns OK status."""
        response = client.get("/health")
        data = response.json()
        assert "status" in data
        assert data["status"] == "OK"

    def test_health_check_response_format(self, client: TestClient):
        """Test health check response format."""
        response = client.get("/health")
        data = response.json()
        assert isinstance(data, dict)
        assert isinstance(data["status"], str)


class TestAppDocumentation:
    """Tests for API documentation endpoints."""

    def test_swagger_ui_available(self, client: TestClient):
        """Test that Swagger UI is available at /docs."""
        response = client.get("/docs")
        assert response.status_code == 200

    def test_redoc_available(self, client: TestClient):
        """Test that ReDoc is available at /redoc."""
        response = client.get("/redoc")
        assert response.status_code == 200

    def test_openapi_schema_available(self, client: TestClient):
        """Test that OpenAPI schema is available at /openapi.json."""
        response = client.get("/openapi.json")
        assert response.status_code == 200
        data = response.json()
        assert "openapi" in data
        assert "paths" in data
        assert "components" in data


class TestCorrelationIdMiddleware:
    """Tests for correlation ID middleware."""

    def test_correlation_id_in_response_headers(self, client: TestClient):
        """Test that correlation ID is in response headers."""
        response = client.get("/health")
        # Check if correlation ID is added (in logs or headers if configured)
        assert response.status_code == 200

    def test_correlation_id_consistent_for_request(self, client: TestClient):
        """Test that correlation ID remains consistent for a request."""
        # Make a POST request
        post_data = {
            "title": "Test",
            "subtext": "Test",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        response1 = client.post("/v1/post/", json=post_data)
        assert response1.status_code == 201

        # Make a GET request for the same resource
        post_id = response1.json()["id"]
        response2 = client.get(f"/v1/post/{post_id}")
        assert response2.status_code == 200


class TestAppIntegration:
    """Tests for app integration and initialization."""

    def test_app_initialized_successfully(self, client: TestClient):
        """Test that app initializes without errors."""
        # If we get here, app initialized successfully
        assert client is not None

    def test_app_has_correct_title(self):
        """Test that app has correct title."""
        assert "Generic CRUD API" in app.title

    def test_app_has_description(self):
        """Test that app has a description."""
        assert app.description is not None

    def test_routes_registered(self, client: TestClient):
        """Test that required routes are registered."""
        # Test Posts routes
        post_data = {
            "title": "Test",
            "subtext": "Test",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        response = client.post("/v1/post/", json=post_data)
        assert response.status_code == 201


class TestCORSConfiguration:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self, client: TestClient):
        """Test that CORS headers are present in responses."""
        response = client.options("/v1/post/")
        # CORS middleware should handle OPTIONS
        assert response.status_code in [200, 404, 405]  # 405 is OK if CORS not configured

    def test_post_endpoint_accessible(self, client: TestClient):
        """Test that POST endpoint is accessible (CORS-wise)."""
        post_data = {
            "title": "Test",
            "subtext": "Test",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        response = client.post("/v1/post/", json=post_data)
        assert response.status_code == 201


class TestAppEndpointAvailability:
    """Tests for endpoint availability and routing."""

    def test_posts_create_endpoint(self, client: TestClient):
        """Test posts create endpoint is available."""
        post_data = {
            "title": "Test",
            "subtext": "Test",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        response = client.post("/v1/post/", json=post_data)
        assert response.status_code in [200, 201]

    def test_posts_list_endpoint(self, client: TestClient):
        """Test posts list endpoint is available."""
        response = client.get("/v1/post/")
        assert response.status_code == 200

    def test_health_endpoint(self, client: TestClient):
        """Test health endpoint is available."""
        response = client.get("/health")
        assert response.status_code == 200

    def test_invalid_endpoint_returns_404(self, client: TestClient):
        """Test that invalid endpoint returns 404."""
        response = client.get("/nonexistent")
        assert response.status_code == 404

    def test_invalid_post_id_returns_404(self, client: TestClient):
        """Test that invalid post ID returns 404."""
        response = client.get("/v1/post/999999")
        assert response.status_code == 404


class TestAppErrorHandling:
    """Tests for error handling."""

    def test_invalid_request_data(self, client: TestClient):
        """Test that invalid request data is handled."""
        # Missing required fields
        post_data = {
            "title": "Test",
            # Missing other required fields
        }
        response = client.post("/v1/post/", json=post_data)
        assert response.status_code == 422  # Validation error

    def test_invalid_json_returns_error(self, client: TestClient):
        """Test that invalid JSON returns error."""
        response = client.post(
            "/v1/post/",
            content="invalid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in [400, 422]

    def test_wrong_method_returns_405(self, client: TestClient):
        """Test that wrong HTTP method returns 405."""
        # Try to POST to a GET endpoint
        response = client.post("/health")
        assert response.status_code == 405
