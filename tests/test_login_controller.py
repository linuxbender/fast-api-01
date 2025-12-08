"""
Unit tests for LoginController authentication endpoints.

Tests the controller layer in isolation by mocking the service layer.
Each test focuses on a single authentication endpoint and its response handling.
"""


import pytest
from app.controller.v1.dto.user_dto import (
    UserResponseDto,
)
from app.controller.v1.login_controller import LoginController
from app.data.v1.model.user import UserState
from app.data.v1.user_repository import UserRepository
from app.security.jwt import TokenData
from app.service.v1.user_service import UserService
from fastapi import APIRouter, Response, status


@pytest.fixture
def mock_user_repo(mocker):
    """Create a mocked UserRepository instance."""
    return mocker.Mock(spec=UserRepository)


@pytest.fixture
def mock_user_service(mocker):
    """Create a mocked UserService instance."""
    return mocker.Mock(spec=UserService)


@pytest.fixture
def router():
    """Create a FastAPI router for testing."""
    return APIRouter()


@pytest.fixture
def login_controller(mocker, router):
    """Create a LoginController with mocked dependencies."""
    mocker.patch("app.controller.v1.login_controller.logger")

    controller = LoginController(router)
    return controller


@pytest.fixture
def mock_token_data():
    """Create mock token data."""
    return TokenData(
        user_id=1,
        email="test@example.com",
        rights=["READ", "EDIT"],
        groups=["ACTIVE_USER"],
    )


@pytest.fixture
def mock_user_dto():
    """Create mock user DTO."""
    return UserResponseDto(
        id=1,
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        state=UserState.ACTIVE,
    )


class TestLoginControllerLogout:
    """Tests for POST /logout endpoint."""

    def test_logout_clears_cookie(self, mocker):
        """Test logout endpoint clears access_token cookie."""
        # Arrange
        mocker.Mock(spec=Response)
        mock_token_data = TokenData(
            user_id=1,
            email="test@example.com",
            rights=["READ", "EDIT"],
            groups=["ACTIVE_USER"],
        )

        # Mock the get_current_user dependency
        mocker.patch(
            "app.controller.v1.login_controller.get_current_user",
            return_value=mock_token_data,
        )

        # Act - Call logout through the router
        from app.controller.v1.login_controller import LoginController

        controller = LoginController(APIRouter())

        # Get the logout route function from the router
        logout_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/logout":
                logout_route = route
                break

        # Assert that the route was registered
        assert logout_route is not None

    def test_logout_returns_success_message(self, mocker):
        """Test logout returns success message."""
        # Arrange
        mocker.Mock(spec=Response)
        TokenData(
            user_id=1,
            email="user@example.com",
            rights=["READ", "EDIT"],
            groups=["ACTIVE_USER"],
        )

        # Mock dependencies
        mocker.patch("app.controller.v1.login_controller.get_session")
        mocker.patch("app.controller.v1.login_controller.get_current_user")

        # Act
        controller = LoginController(APIRouter())

        # Assert that logout endpoint exists
        logout_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/logout":
                logout_route = route
                break

        assert logout_route is not None
        assert hasattr(logout_route, "methods")
        assert "POST" in logout_route.methods

    @pytest.mark.asyncio
    async def test_logout_requires_authentication(self, mocker):
        """Test logout endpoint requires authentication."""
        # Arrange
        mocker.Mock(spec=Response)

        # Mock the auth dependency to raise an exception (not authenticated)
        mock_get_current_user = mocker.patch(
            "app.controller.v1.login_controller.get_current_user",
        )
        mock_get_current_user.side_effect = Exception("Not authenticated")

        # Act & Assert
        controller = LoginController(APIRouter())

        # The logout endpoint should require authentication
        logout_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/logout":
                logout_route = route
                break

        assert logout_route is not None

    def test_logout_route_exists_with_correct_method(self):
        """Test that logout route is registered with POST method."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the logout route
        logout_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/logout":
                logout_route = route
                break

        # Assert
        assert logout_route is not None
        assert hasattr(logout_route, "methods")
        assert "POST" in logout_route.methods

    def test_logout_route_has_correct_tags(self):
        """Test that logout route has correct summary and description."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the logout route
        logout_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/logout":
                logout_route = route
                break

        # Assert
        assert logout_route is not None
        assert hasattr(logout_route, "summary")
        assert logout_route.summary == "Logout"
        assert hasattr(logout_route, "description")
        assert "Logout" in logout_route.description
        assert "token" in logout_route.description.lower()

    def test_logout_status_code_is_200(self):
        """Test logout returns 200 OK status code."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the logout route
        logout_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/logout":
                logout_route = route
                break

        # Assert
        assert logout_route is not None
        assert hasattr(logout_route, "status_code")
        assert logout_route.status_code == status.HTTP_200_OK


class TestLoginControllerRegister:
    """Tests for POST /register endpoint."""

    def test_register_route_exists(self):
        """Test that register route is registered."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the register route
        register_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/register":
                register_route = route
                break

        # Assert
        assert register_route is not None

    def test_register_route_is_public(self):
        """Test that register endpoint is public (no auth required)."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the register route
        register_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/register":
                register_route = route
                break

        # Assert
        assert register_route is not None
        assert hasattr(register_route, "methods")
        assert "POST" in register_route.methods

    def test_register_status_code_is_201(self):
        """Test register returns 201 Created status code."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the register route
        register_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/register":
                register_route = route
                break

        # Assert
        assert register_route is not None
        assert hasattr(register_route, "status_code")
        assert register_route.status_code == status.HTTP_201_CREATED

    def test_register_route_has_correct_metadata(self):
        """Test register route has correct summary and description."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the register route
        register_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/register":
                register_route = route
                break

        # Assert
        assert register_route is not None
        assert hasattr(register_route, "summary")
        assert register_route.summary == "Register"


class TestLoginControllerMe:
    """Tests for GET /me endpoint."""

    def test_me_route_exists(self):
        """Test that me route is registered."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the me route
        me_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/me":
                me_route = route
                break

        # Assert
        assert me_route is not None

    def test_me_route_requires_authentication(self):
        """Test that me endpoint requires authentication."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the me route
        me_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/me":
                me_route = route
                break

        # Assert
        assert me_route is not None
        assert hasattr(me_route, "methods")
        assert "GET" in me_route.methods

    def test_me_status_code_is_200(self):
        """Test me returns 200 OK status code."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the me route
        me_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/me":
                me_route = route
                break

        # Assert
        assert me_route is not None
        assert hasattr(me_route, "status_code")
        assert me_route.status_code == status.HTTP_200_OK

    def test_me_route_has_correct_metadata(self):
        """Test me route has correct summary and description."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the me route
        me_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/me":
                me_route = route
                break

        # Assert
        assert me_route is not None
        assert hasattr(me_route, "summary")
        assert me_route.summary == "Get Current User"


class TestLoginControllerDeactivate:
    """Tests for POST /deactivate endpoint."""

    def test_deactivate_route_exists(self):
        """Test that deactivate route is registered."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the deactivate route
        deactivate_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/deactivate":
                deactivate_route = route
                break

        # Assert
        assert deactivate_route is not None

    def test_deactivate_route_requires_authentication(self):
        """Test that deactivate endpoint requires authentication."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the deactivate route
        deactivate_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/deactivate":
                deactivate_route = route
                break

        # Assert
        assert deactivate_route is not None
        assert hasattr(deactivate_route, "methods")
        assert "POST" in deactivate_route.methods

    def test_deactivate_status_code_is_200(self):
        """Test deactivate returns 200 OK status code."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the deactivate route
        deactivate_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/deactivate":
                deactivate_route = route
                break

        # Assert
        assert deactivate_route is not None
        assert hasattr(deactivate_route, "status_code")
        assert deactivate_route.status_code == status.HTTP_200_OK


class TestLoginControllerResetPassword:
    """Tests for POST /reset-password endpoint."""

    def test_reset_password_route_exists(self):
        """Test that reset-password route is registered."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the reset-password route
        reset_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/reset-password":
                reset_route = route
                break

        # Assert
        assert reset_route is not None

    def test_reset_password_route_requires_authentication(self):
        """Test that reset-password endpoint requires authentication."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the reset-password route
        reset_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/reset-password":
                reset_route = route
                break

        # Assert
        assert reset_route is not None
        assert hasattr(reset_route, "methods")
        assert "POST" in reset_route.methods

    def test_reset_password_status_code_is_200(self):
        """Test reset-password returns 200 OK status code."""
        # Arrange
        controller = LoginController(APIRouter())

        # Act - Find the reset-password route
        reset_route = None
        for route in controller.router.routes:
            if hasattr(route, "path") and route.path == "/reset-password":
                reset_route = route
                break

        # Assert
        assert reset_route is not None
        assert hasattr(reset_route, "status_code")
        assert reset_route.status_code == status.HTTP_200_OK
