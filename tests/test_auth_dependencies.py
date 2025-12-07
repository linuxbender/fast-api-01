"""Unit tests for authentication dependencies.

Tests the auth dependency injection layer for JWT token verification
and user authentication from both Bearer tokens and HTTP-Only cookies.
"""

from datetime import timedelta

import pytest
from app.config.auth_dependencies import (
    get_current_user,
    get_current_user_optional,
)
from app.security.jwt import TokenData, create_access_token
from fastapi import HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials


@pytest.fixture
def valid_token_data():
    """Create valid token data."""
    return {
        "user_id": 1,
        "email": "test@example.com",
        "rights": ["READ", "EDIT"],
        "groups": ["ACTIVE_USER"],
    }


@pytest.fixture
def valid_token(valid_token_data):
    """Create a valid JWT token."""
    return create_access_token(
        data=valid_token_data,
        expires_delta=timedelta(minutes=30),
    )


@pytest.fixture
def expired_token():
    """Create an expired JWT token."""
    return create_access_token(
        data={
            "user_id": 1,
            "email": "test@example.com",
            "rights": ["READ", "EDIT"],
            "groups": ["ACTIVE_USER"],
        },
        expires_delta=timedelta(minutes=-1),
    )


@pytest.fixture
def mock_bearer_credentials(valid_token):
    """Create mock Bearer credentials."""
    return HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=valid_token
    )


class TestGetCurrentUser:
    """Tests for get_current_user dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_bearer_token(
        self, mocker, mock_bearer_credentials, valid_token_data
    ):
        """Test get_current_user with valid Bearer token."""
        # Arrange
        mocker.patch("app.config.auth_dependencies.verify_access_token")
        mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=TokenData(
                user_id=valid_token_data["user_id"],
                email=valid_token_data["email"],
                rights=valid_token_data["rights"],
                groups=valid_token_data["groups"],
            ),
        )

        # Act
        result = await get_current_user(
            credentials=mock_bearer_credentials, access_token=None
        )

        # Assert
        assert result is not None
        assert result.user_id == valid_token_data["user_id"]
        assert result.email == valid_token_data["email"]

    @pytest.mark.asyncio
    async def test_get_current_user_with_valid_cookie_token(
        self, mocker, valid_token, valid_token_data
    ):
        """Test get_current_user with valid cookie token."""
        # Arrange
        mock_token_data = TokenData(
            user_id=valid_token_data["user_id"],
            email=valid_token_data["email"],
            rights=valid_token_data["rights"],
            groups=valid_token_data["groups"],
        )
        mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=mock_token_data,
        )

        cookie_token = f"bearer {valid_token}"

        # Act
        result = await get_current_user(
            credentials=None, access_token=cookie_token
        )

        # Assert
        assert result is not None
        assert result.user_id == valid_token_data["user_id"]
        assert result.email == valid_token_data["email"]

    @pytest.mark.asyncio
    async def test_get_current_user_with_no_credentials_raises_exception(
        self,
    ):
        """Test get_current_user raises HTTPException when no credentials."""
        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(credentials=None, access_token=None)

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Not authenticated" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_with_invalid_token_raises_exception(
        self, mocker, mock_bearer_credentials
    ):
        """Test get_current_user raises HTTPException with invalid token."""
        # Arrange
        mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=None,
        )

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_current_user(
                credentials=mock_bearer_credentials, access_token=None
            )

        assert exc_info.value.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid or expired token" in exc_info.value.detail

    @pytest.mark.asyncio
    async def test_get_current_user_bearer_takes_precedence(
        self, mocker, mock_bearer_credentials, valid_token, valid_token_data
    ):
        """Test that Bearer token takes precedence over cookie token."""
        # Arrange
        mock_token_data = TokenData(
            user_id=valid_token_data["user_id"],
            email=valid_token_data["email"],
            rights=valid_token_data["rights"],
            groups=valid_token_data["groups"],
        )
        mock_verify = mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=mock_token_data,
        )

        # Act
        await get_current_user(
            credentials=mock_bearer_credentials,
            access_token=f"bearer {valid_token}",
        )

        # Assert
        mock_verify.assert_called_once_with(
            mock_bearer_credentials.credentials
        )

    @pytest.mark.asyncio
    async def test_get_current_user_with_cookie_token_without_prefix(
        self, mocker, valid_token, valid_token_data
    ):
        """Test get_current_user with cookie without 'bearer' prefix."""
        # Arrange
        mock_token_data = TokenData(
            user_id=valid_token_data["user_id"],
            email=valid_token_data["email"],
            rights=valid_token_data["rights"],
            groups=valid_token_data["groups"],
        )
        mock_verify = mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=mock_token_data,
        )

        # Act
        result = await get_current_user(
            credentials=None, access_token=valid_token
        )

        # Assert
        assert result is not None
        mock_verify.assert_called_once_with(valid_token)


class TestGetCurrentUserOptional:
    """Tests for get_current_user_optional dependency."""

    @pytest.mark.asyncio
    async def test_get_current_user_optional_with_valid_bearer_token(
        self, mocker, mock_bearer_credentials, valid_token_data
    ):
        """Test get_current_user_optional with valid Bearer token."""
        # Arrange
        mock_token_data = TokenData(
            user_id=valid_token_data["user_id"],
            email=valid_token_data["email"],
            rights=valid_token_data["rights"],
            groups=valid_token_data["groups"],
        )
        mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=mock_token_data,
        )

        # Act
        result = await get_current_user_optional(
            credentials=mock_bearer_credentials, access_token=None
        )

        # Assert
        assert result is not None
        assert result.user_id == valid_token_data["user_id"]

    @pytest.mark.asyncio
    async def test_get_current_user_optional_with_valid_cookie_token(
        self, mocker, valid_token, valid_token_data
    ):
        """Test get_current_user_optional with valid cookie token."""
        # Arrange
        mock_token_data = TokenData(
            user_id=valid_token_data["user_id"],
            email=valid_token_data["email"],
            rights=valid_token_data["rights"],
            groups=valid_token_data["groups"],
        )
        mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=mock_token_data,
        )

        # Act
        result = await get_current_user_optional(
            credentials=None, access_token=f"bearer {valid_token}"
        )

        # Assert
        assert result is not None
        assert result.user_id == valid_token_data["user_id"]

    @pytest.mark.asyncio
    async def test_get_current_user_optional_with_no_credentials_returns_none(
        self,
    ):
        """Test get_current_user_optional returns None no credentials."""
        # Act
        result = await get_current_user_optional(
            credentials=None, access_token=None
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_with_invalid_token_returns_none(
        self, mocker, mock_bearer_credentials
    ):
        """Test get_current_user_optional returns None with invalid token."""
        # Arrange
        mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=None,
        )

        # Act
        result = await get_current_user_optional(
            credentials=mock_bearer_credentials, access_token=None
        )

        # Assert
        assert result is None

    @pytest.mark.asyncio
    async def test_get_current_user_optional_bearer_takes_precedence(
        self, mocker, mock_bearer_credentials, valid_token, valid_token_data
    ):
        """Test that Bearer token takes precedence in optional auth."""
        # Arrange
        mock_token_data = TokenData(
            user_id=valid_token_data["user_id"],
            email=valid_token_data["email"],
            rights=valid_token_data["rights"],
            groups=valid_token_data["groups"],
        )
        mock_verify = mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=mock_token_data,
        )

        # Act
        await get_current_user_optional(
            credentials=mock_bearer_credentials,
            access_token=f"bearer {valid_token}",
        )

        # Assert
        assert mock_verify.call_count == 1
        mock_verify.assert_called_with(mock_bearer_credentials.credentials)

    @pytest.mark.asyncio
    async def test_get_current_user_optional_with_cookie_without_prefix(
        self, mocker, valid_token, valid_token_data
    ):
        """Test get_current_user_optional with cookie without prefix."""
        # Arrange
        mock_token_data = TokenData(
            user_id=valid_token_data["user_id"],
            email=valid_token_data["email"],
            rights=valid_token_data["rights"],
            groups=valid_token_data["groups"],
        )
        mock_verify = mocker.patch(
            "app.config.auth_dependencies.verify_access_token",
            return_value=mock_token_data,
        )

        # Act
        result = await get_current_user_optional(
            credentials=None, access_token=valid_token
        )

        # Assert
        assert result is not None
        mock_verify.assert_called_once_with(valid_token)
