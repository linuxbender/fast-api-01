"""Unit tests for JWT functionality."""

from datetime import UTC, datetime, timedelta

from app.security.jwt import TokenData, create_access_token, verify_access_token


def test_create_access_token_creates_valid_token():
    """Test creating an access token."""
    # Arrange
    data = {
        "user_id": 1,
        "email": "test@example.com",
        "rights": ["READ", "EDIT"],
        "groups": ["ACTIVE_USER"],
    }

    # Act
    token = create_access_token(data)

    # Assert
    assert token is not None
    assert isinstance(token, str)
    assert len(token) > 0


def test_verify_access_token_with_valid_token():
    """Test verifying a valid access token."""
    # Arrange
    data = {
        "user_id": 1,
        "email": "test@example.com",
        "rights": ["READ", "EDIT"],
        "groups": ["ACTIVE_USER"],
    }
    token = create_access_token(data)

    # Act
    result = verify_access_token(token)

    # Assert
    assert result is not None
    assert isinstance(result, TokenData)
    assert result.user_id == 1
    assert result.email == "test@example.com"
    assert result.rights == ["READ", "EDIT"]
    assert result.groups == ["ACTIVE_USER"]


def test_verify_access_token_with_invalid_token():
    """Test verifying an invalid access token."""
    # Act
    result = verify_access_token("invalid.token.here")

    # Assert
    assert result is None


def test_verify_access_token_with_empty_token():
    """Test verifying an empty token."""
    # Act
    result = verify_access_token("")

    # Assert
    assert result is None


def test_verify_access_token_with_missing_user_id():
    """Test verifying token with missing user_id."""
    # Arrange
    from jose import jwt

    secret_key = "your-secret-key-change-in-production"
    payload = {
        "email": "test@example.com",
        "exp": datetime.now(UTC) + timedelta(minutes=30),
    }
    token = jwt.encode(payload, secret_key, algorithm="HS256")

    # Act
    result = verify_access_token(token)

    # Assert
    assert result is None


def test_token_expiration():
    """Test that token can be expired."""
    # Arrange
    data = {
        "user_id": 1,
        "email": "test@example.com",
    }
    # Create token that expires immediately
    token = create_access_token(data, expires_delta=timedelta(seconds=-1))

    # Act
    result = verify_access_token(token)

    # Assert - should be None due to expiration
    assert result is None


def test_token_with_custom_expiration():
    """Test creating token with custom expiration."""
    # Arrange
    data = {
        "user_id": 1,
        "email": "test@example.com",
    }

    # Act
    token = create_access_token(data, expires_delta=timedelta(minutes=60))
    result = verify_access_token(token)

    # Assert
    assert result is not None
    assert result.user_id == 1
