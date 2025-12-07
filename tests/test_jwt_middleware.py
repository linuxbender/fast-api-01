"""Tests for JWT validation middleware."""

from datetime import UTC, datetime, timedelta

import pytest
from app.config.jwt_middleware import JWTValidationMiddleware
from app.security.jwt import DEFAULT_ALGORITHM, DEFAULT_SECRET_KEY
from fastapi import FastAPI
from fastapi.testclient import TestClient
from jose import jwt

# Create a test app
test_app = FastAPI()


@test_app.get("/public")
async def public_endpoint():
    """Public endpoint (no JWT required)."""
    return {"message": "public"}


@test_app.get("/protected")
async def protected_endpoint():
    """Protected endpoint (JWT required)."""
    return {"message": "protected"}


@test_app.get("/login")
async def login_endpoint():
    """Login endpoint (excluded from JWT validation)."""
    return {"token": "test-token"}


# Add middleware
test_app.add_middleware(JWTValidationMiddleware)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(test_app)


def create_token(
    data: dict,
    expires_delta: timedelta | None = None,
    is_expired: bool = False,
) -> str:
    """Create a test JWT token.

    Args:
        data: Token payload data
        expires_delta: Token expiration time
        is_expired: If True, create an already expired token

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()

    if is_expired:
        # Create token expired 1 hour ago
        expire = datetime.now(UTC) - timedelta(hours=1)
    elif expires_delta:
        expire = datetime.now(UTC) + expires_delta
    else:
        expire = datetime.now(UTC) + timedelta(hours=1)

    to_encode.update({"exp": expire, "iat": datetime.now(UTC)})

    return jwt.encode(to_encode, DEFAULT_SECRET_KEY, algorithm=DEFAULT_ALGORITHM)


def test_public_endpoint_without_token(client):
    """Test public endpoint works without JWT token."""
    response = client.get("/login")
    assert response.status_code == 200
    assert response.json() == {"token": "test-token"}


def test_protected_endpoint_with_valid_token(client):
    """Test protected endpoint with valid JWT token."""
    token = create_token({"user_id": 1, "email": "test@example.com"})

    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {"message": "protected"}


def test_protected_endpoint_with_expired_token(client):
    """Test protected endpoint with expired JWT token."""
    token = create_token(
        {"user_id": 1, "email": "test@example.com"},
        is_expired=True,
    )

    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "TOKEN_EXPIRED"
    assert data["redirect_to"] == "/login"
    assert data["user_email"] == "test@example.com"


def test_protected_endpoint_with_invalid_token(client):
    """Test protected endpoint with invalid JWT token."""
    response = client.get(
        "/protected",
        headers={"Authorization": "Bearer invalid.token.here"},
    )

    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "INVALID_TOKEN"
    assert data["redirect_to"] == "/login"


def test_protected_endpoint_with_token_in_cookie(client):
    """Test protected endpoint with JWT token in cookie."""
    token = create_token({"user_id": 1, "email": "test@example.com"})

    client.cookies.set("access_token", token)
    response = client.get("/protected")

    assert response.status_code == 200
    assert response.json() == {"message": "protected"}


def test_protected_endpoint_with_expired_token_in_cookie(client):
    """Test protected endpoint with expired JWT token in cookie."""
    token = create_token(
        {"user_id": 1, "email": "test@example.com"},
        is_expired=True,
    )

    client.cookies.set("access_token", token)
    response = client.get("/protected")

    assert response.status_code == 401
    data = response.json()
    assert data["error_code"] == "TOKEN_EXPIRED"
    assert data["redirect_to"] == "/login"


def test_protected_endpoint_with_bearer_prefix_in_cookie(client):
    """Test protected endpoint with bearer prefix in cookie."""
    token = create_token({"user_id": 1, "email": "test@example.com"})

    client.cookies.set("access_token", f"bearer {token}")
    response = client.get("/protected")

    assert response.status_code == 200
    assert response.json() == {"message": "protected"}


def test_excluded_route_without_token(client):
    """Test excluded routes work without JWT token."""
    response = client.get("/login")
    assert response.status_code == 200


def test_excluded_route_with_invalid_token(client):
    """Test excluded routes don't validate token."""
    response = client.get(
        "/login",
        headers={"Authorization": "Bearer invalid.token"},
    )
    assert response.status_code == 200


def test_protected_endpoint_without_token(client):
    """Test protected endpoint without JWT token passes through."""
    # Should not be rejected by middleware, other dependencies will handle auth
    response = client.get("/protected")
    assert response.status_code == 200
