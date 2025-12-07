"""Unit tests for User service."""

from datetime import UTC, datetime
from unittest.mock import Mock

import pytest
from app.controller.v1.dto.user_dto import UserCreateDto
from app.data.v1.model.user import User, UserState
from app.data.v1.user_repository import UserRepository
from app.service.v1.user_service import UserService


@pytest.fixture
def mock_repository():
    """Create a mock repository."""
    return Mock(spec=UserRepository)


@pytest.fixture
def user_service(mock_repository):
    """Create UserService with mock repository."""
    return UserService(mock_repository)


@pytest.fixture
def sample_user():
    """Create a sample user for testing."""
    return User(
        id=1,
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        created_at=datetime.now(UTC),
        changed_at=datetime.now(UTC),
        state=UserState.ACTIVE,
    )


def test_hash_password_returns_different_hash(user_service):
    """Test that hash_password returns a hashed password."""
    password = "TestPassword123!@#"
    hashed = user_service.hash_password(password)

    assert hashed != password
    assert len(hashed) > 0
    assert isinstance(hashed, str)


def test_verify_password_with_correct_password(user_service):
    """Test verify_password with correct password."""
    password = "TestPassword123!@#"
    hashed = user_service.hash_password(password)

    assert user_service.verify_password(password, hashed) is True


def test_verify_password_with_incorrect_password(user_service):
    """Test verify_password with incorrect password."""
    password = "TestPassword123!@#"
    hashed = user_service.hash_password(password)
    wrong_password = "WrongPassword123!@#"

    assert user_service.verify_password(wrong_password, hashed) is False


def test_create_user_success(user_service, mock_repository, sample_user):
    """Test create_user successfully creates a new user."""
    # Arrange
    mock_repository.get_by_email.return_value = None
    mock_repository.get_by_display_name.return_value = None
    mock_repository.create.return_value = sample_user

    dto = UserCreateDto(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        re_email="john@example.com",
        password="TestPassword123!@#",
        re_password="TestPassword123!@#",
    )

    # Act
    result = user_service.create_user(dto)

    # Assert
    assert result.id == 1
    assert result.name == "John"
    assert result.email == "john@example.com"
    mock_repository.get_by_email.assert_called_once_with("john@example.com")
    mock_repository.get_by_display_name.assert_called_once_with("johndoe")
    mock_repository.create.assert_called_once()


def test_create_user_email_exists(user_service, mock_repository, sample_user):
    """Test create_user raises error when email already exists."""
    # Arrange
    mock_repository.get_by_email.return_value = sample_user

    dto = UserCreateDto(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        re_email="john@example.com",
        password="TestPassword123!@#",
        re_password="TestPassword123!@#",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Email .* is already registered"):
        user_service.create_user(dto)


def test_create_user_display_name_exists(user_service, mock_repository, sample_user):
    """Test create_user raises error when display_name already exists."""
    # Arrange
    mock_repository.get_by_email.return_value = None
    mock_repository.get_by_display_name.return_value = sample_user

    dto = UserCreateDto(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        re_email="john@example.com",
        password="TestPassword123!@#",
        re_password="TestPassword123!@#",
    )

    # Act & Assert
    with pytest.raises(ValueError, match="Display name .* is already taken"):
        user_service.create_user(dto)


def test_authenticate_user_success(user_service, mock_repository, sample_user):
    """Test authenticate_user with correct credentials."""
    # Arrange
    password = "TestPassword123!@#"
    sample_user.password_hash = user_service.hash_password(password)
    mock_repository.get_active_by_email.return_value = sample_user
    mock_repository.update.return_value = sample_user

    # Act
    result = user_service.authenticate_user(sample_user.email, password)

    # Assert
    assert result is not None
    assert result.id == sample_user.id
    mock_repository.get_active_by_email.assert_called_once_with(sample_user.email)


def test_authenticate_user_not_found(user_service, mock_repository):
    """Test authenticate_user when user not found."""
    # Arrange
    mock_repository.get_active_by_email.return_value = None

    # Act
    result = user_service.authenticate_user("nonexistent@example.com", "password")

    # Assert
    assert result is None


def test_authenticate_user_wrong_password(user_service, mock_repository, sample_user):
    """Test authenticate_user with wrong password."""
    # Arrange
    sample_user.password_hash = user_service.hash_password("CorrectPassword123!@#")
    mock_repository.get_active_by_email.return_value = sample_user

    # Act
    result = user_service.authenticate_user(sample_user.email, "WrongPassword123!@#")

    # Assert
    assert result is None


def test_get_user_by_id_found(user_service, mock_repository, sample_user):
    """Test get_user_by_id when user is found."""
    # Arrange
    mock_repository.read.return_value = sample_user

    # Act
    result = user_service.get_user_by_id(1)

    # Assert
    assert result is not None
    assert result.id == 1
    assert result.email == "john@example.com"
    mock_repository.read.assert_called_once_with(1)


def test_get_user_by_id_not_found(user_service, mock_repository):
    """Test get_user_by_id when user is not found."""
    # Arrange
    mock_repository.read.return_value = None

    # Act
    result = user_service.get_user_by_id(999)

    # Assert
    assert result is None


def test_get_user_by_email_found(user_service, mock_repository, sample_user):
    """Test get_user_by_email when user is found."""
    # Arrange
    mock_repository.get_by_email.return_value = sample_user

    # Act
    result = user_service.get_user_by_email(sample_user.email)

    # Assert
    assert result is not None
    assert result.email == sample_user.email
    mock_repository.get_by_email.assert_called_once_with(sample_user.email)


def test_deactivate_user_success(user_service, mock_repository, sample_user):
    """Test deactivate_user successfully deactivates a user."""
    # Arrange
    sample_user.state = UserState.ACTIVE
    inactive_user = User(
        id=sample_user.id,
        name=sample_user.name,
        vorname=sample_user.vorname,
        display_name=sample_user.display_name,
        email=sample_user.email,
        password_hash=sample_user.password_hash,
        state=UserState.INACTIVE,
    )

    mock_repository.read.return_value = sample_user
    mock_repository.update.return_value = inactive_user

    # Act
    result = user_service.deactivate_user(1)

    # Assert
    assert result is not None
    assert result.state == "INACTIVE"
    mock_repository.read.assert_called_once_with(1)
    mock_repository.update.assert_called_once()


def test_deactivate_user_not_found(user_service, mock_repository):
    """Test deactivate_user when user not found."""
    # Arrange
    mock_repository.read.return_value = None

    # Act
    result = user_service.deactivate_user(999)

    # Assert
    assert result is None


def test_reset_password_success(user_service, mock_repository, sample_user):
    """Test reset_password successfully resets password."""
    # Arrange
    new_password = "NewPassword123!@#"
    updated_user = User(
        id=sample_user.id,
        name=sample_user.name,
        vorname=sample_user.vorname,
        display_name=sample_user.display_name,
        email=sample_user.email,
        password_hash=user_service.hash_password(new_password),
        state=sample_user.state,
    )

    mock_repository.read.return_value = sample_user
    mock_repository.update.return_value = updated_user

    # Act
    result = user_service.reset_password(1, new_password)

    # Assert
    assert result is not None
    assert result.email == sample_user.email
    mock_repository.read.assert_called_once_with(1)
    mock_repository.update.assert_called_once()


def test_reset_password_not_found(user_service, mock_repository):
    """Test reset_password when user not found."""
    # Arrange
    mock_repository.read.return_value = None

    # Act
    result = user_service.reset_password(999, "NewPassword123!@#")

    # Assert
    assert result is None
