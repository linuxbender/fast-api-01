"""Tests for login code service and passwordless authentication."""

from datetime import UTC, datetime, timedelta

import pytest
from app.data.v1.login_code_repository import LoginCodeRepository
from app.data.v1.model.login_code import LoginCode
from app.data.v1.user_repository import UserRepository
from app.service.v1.login_code_service import LoginCodeService


@pytest.fixture
def login_code_repo(mocker):
    """Mock LoginCode repository."""
    return mocker.Mock(spec=LoginCodeRepository)


@pytest.fixture
def user_repo(mocker):
    """Mock User repository."""
    return mocker.Mock(spec=UserRepository)


@pytest.fixture
def login_code_service(login_code_repo, user_repo):
    """Create LoginCodeService with mocked repositories."""
    return LoginCodeService(login_code_repo, user_repo)


class TestLoginCodeGeneration:
    """Tests for login code generation."""

    def test_generate_code_returns_6_digits(self, login_code_service):
        """Test that generated code is 6 digits."""
        code = login_code_service.generate_code()
        assert len(code) == 6
        assert code.isdigit()

    def test_generate_code_is_random(self, login_code_service):
        """Test that generated codes are different."""
        codes = [login_code_service.generate_code() for _ in range(10)]
        assert len(set(codes)) > 1  # At least some should be different

    def test_generate_code_custom_length(self, login_code_service):
        """Test generating codes with custom length."""
        code = login_code_service.generate_code(length=8)
        assert len(code) == 8
        assert code.isdigit()


class TestCreateLoginCode:
    """Tests for creating login codes."""

    def test_create_login_code_success(self, login_code_service, login_code_repo):
        """Test successful login code creation."""
        email = "user@example.com"
        expected_code = LoginCode(
            id=1,
            email=email,
            code="123456",
            expires_at=datetime.now(UTC) + timedelta(minutes=15),
        )
        login_code_repo.create_code.return_value = expected_code
        login_code_repo.delete_expired_codes.return_value = 0

        result = login_code_service.create_login_code(email)

        assert result.email == email
        login_code_repo.delete_expired_codes.assert_called_once_with(email)
        login_code_repo.create_code.assert_called_once()

    def test_create_login_code_invalid_email(self, login_code_service):
        """Test create login code with invalid email."""
        with pytest.raises(ValueError, match="Invalid email"):
            login_code_service.create_login_code("")

        with pytest.raises(ValueError, match="Invalid email"):
            login_code_service.create_login_code("notanemail")

    def test_create_login_code_custom_expiry(self, login_code_service, login_code_repo):
        """Test create login code with custom expiry."""
        email = "user@example.com"
        expected_code = LoginCode(
            id=1,
            email=email,
            code="123456",
            expires_at=datetime.now(UTC) + timedelta(minutes=30),
        )
        login_code_repo.create_code.return_value = expected_code
        login_code_repo.delete_expired_codes.return_value = 0

        login_code_service.create_login_code(email, expires_in_minutes=30)

        login_code_repo.create_code.assert_called_once()
        # Check that 30 minutes was passed
        call_args = login_code_repo.create_code.call_args
        assert call_args[0][2] == 30  # Third argument is expires_in_minutes


class TestVerifyLoginCode:
    """Tests for verifying login codes."""

    def test_verify_valid_code_success(self, login_code_service, login_code_repo, user_repo):
        """Test verifying a valid login code."""
        email = "user@example.com"
        code = "123456"

        # Mock login code
        login_code = LoginCode(
            id=1,
            email=email,
            code=code,
            expires_at=datetime.now(UTC) + timedelta(minutes=15),
            is_used=False,
        )
        login_code_repo.get_active_code.return_value = login_code

        # Mock user
        user = type("User", (), {
            "id": 1,
            "email": email,
            "name": "John",
        })()
        user_repo.get_by_email.return_value = user

        # Mock mark as used
        login_code_repo.mark_as_used.return_value = login_code

        result = login_code_service.verify_login_code(email, code)

        assert result is not None
        assert result["user_id"] == 1
        assert result["email"] == email
        login_code_repo.mark_as_used.assert_called_once()

    def test_verify_invalid_code(self, login_code_service, login_code_repo):
        """Test verifying an invalid code."""
        email = "user@example.com"
        code = "000000"

        login_code_repo.get_active_code.return_value = None

        result = login_code_service.verify_login_code(email, code)

        assert result is None
        login_code_repo.get_active_code.assert_called_once_with(email, code)

    def test_verify_code_user_not_found(self, login_code_service, login_code_repo, user_repo):
        """Test verifying code when user doesn't exist."""
        email = "nonexistent@example.com"
        code = "123456"

        login_code = LoginCode(
            id=1,
            email=email,
            code=code,
            expires_at=datetime.now(UTC) + timedelta(minutes=15),
            is_used=False,
        )
        login_code_repo.get_active_code.return_value = login_code
        user_repo.get_by_email.return_value = None

        with pytest.raises(ValueError, match="User not found"):
            login_code_service.verify_login_code(email, code)

    def test_verify_code_empty_email(self, login_code_service):
        """Test verifying with empty email."""
        result = login_code_service.verify_login_code("", "123456")
        assert result is None

    def test_verify_code_empty_code(self, login_code_service):
        """Test verifying with empty code."""
        result = login_code_service.verify_login_code("user@example.com", "")
        assert result is None


class TestLoginCodeValidity:
    """Tests for login code validity checks."""

    def test_valid_code_is_valid(self, login_code_service):
        """Test that non-expired, unused code is valid."""
        login_code = LoginCode(
            id=1,
            email="user@example.com",
            code="123456",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            is_used=False,
        )
        assert login_code_service.code_is_valid(login_code)

    def test_expired_code_is_invalid(self, login_code_service):
        """Test that expired code is invalid."""
        login_code = LoginCode(
            id=1,
            email="user@example.com",
            code="123456",
            expires_at=datetime.now(UTC) - timedelta(minutes=5),
            is_used=False,
        )
        assert not login_code_service.code_is_valid(login_code)

    def test_used_code_is_invalid(self, login_code_service):
        """Test that used code is invalid."""
        login_code = LoginCode(
            id=1,
            email="user@example.com",
            code="123456",
            expires_at=datetime.now(UTC) + timedelta(minutes=10),
            is_used=True,
        )
        assert not login_code_service.code_is_valid(login_code)

    def test_expiration_time_calculation(self, login_code_service):
        """Test expiration time calculation."""
        expires_at = datetime.now(UTC) + timedelta(seconds=30)
        login_code = LoginCode(
            id=1,
            email="user@example.com",
            code="123456",
            expires_at=expires_at,
            is_used=False,
        )
        remaining = login_code_service.code_expiration_time(login_code)
        assert 25 <= remaining <= 30  # Allow small time drift

    def test_expiration_time_for_expired_code(self, login_code_service):
        """Test expiration time for already expired code."""
        login_code = LoginCode(
            id=1,
            email="user@example.com",
            code="123456",
            expires_at=datetime.now(UTC) - timedelta(minutes=5),
            is_used=False,
        )
        remaining = login_code_service.code_expiration_time(login_code)
        assert remaining == -1
