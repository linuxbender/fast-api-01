"""Unit tests for User repository."""


import pytest
from app.data.v1.model.user import User, UserState
from app.data.v1.user_repository import UserRepository
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


@pytest.fixture
def session():
    """Create an in-memory SQLite database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def user_repository(session):
    """Create UserRepository with test session."""
    return UserRepository(session)


def test_user_repository_create(user_repository, session):
    """Test creating a user in repository."""
    # Arrange
    user = User(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        state=UserState.ACTIVE,
    )

    # Act
    created_user = user_repository.create(user)

    # Assert
    assert created_user.id is not None
    assert created_user.name == "John"
    assert created_user.email == "john@example.com"

    # Verify in session
    found_user = session.get(User, created_user.id)
    assert found_user is not None
    assert found_user.email == "john@example.com"


def test_user_repository_read(user_repository, session):
    """Test reading a user from repository."""
    # Arrange
    user = User(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        state=UserState.ACTIVE,
    )
    created_user = user_repository.create(user)

    # Act
    found_user = user_repository.read(created_user.id)

    # Assert
    assert found_user is not None
    assert found_user.id == created_user.id
    assert found_user.name == "John"


def test_user_repository_read_not_found(user_repository):
    """Test reading non-existent user returns None."""
    # Act
    result = user_repository.read(999)

    # Assert
    assert result is None


def test_user_repository_get_by_email(user_repository):
    """Test getting user by email."""
    # Arrange
    user = User(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        state=UserState.ACTIVE,
    )
    user_repository.create(user)

    # Act
    found_user = user_repository.get_by_email("john@example.com")

    # Assert
    assert found_user is not None
    assert found_user.email == "john@example.com"
    assert found_user.name == "John"


def test_user_repository_get_by_email_not_found(user_repository):
    """Test getting non-existent user by email returns None."""
    # Act
    result = user_repository.get_by_email("nonexistent@example.com")

    # Assert
    assert result is None


def test_user_repository_get_by_display_name(user_repository):
    """Test getting user by display name."""
    # Arrange
    user = User(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        state=UserState.ACTIVE,
    )
    user_repository.create(user)

    # Act
    found_user = user_repository.get_by_display_name("johndoe")

    # Assert
    assert found_user is not None
    assert found_user.display_name == "johndoe"


def test_user_repository_get_by_display_name_not_found(user_repository):
    """Test getting non-existent user by display name returns None."""
    # Act
    result = user_repository.get_by_display_name("nonexistent")

    # Assert
    assert result is None


def test_user_repository_get_active_by_email(user_repository):
    """Test getting active user by email."""
    # Arrange
    user = User(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        state=UserState.ACTIVE,
    )
    user_repository.create(user)

    # Act
    found_user = user_repository.get_active_by_email("john@example.com")

    # Assert
    assert found_user is not None
    assert found_user.email == "john@example.com"
    assert found_user.state == UserState.ACTIVE


def test_user_repository_get_active_by_email_inactive(user_repository):
    """Test getting inactive user by email returns None."""
    # Arrange
    user = User(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        state=UserState.INACTIVE,
    )
    user_repository.create(user)

    # Act
    result = user_repository.get_active_by_email("john@example.com")

    # Assert
    assert result is None


def test_user_repository_read_all(user_repository):
    """Test reading all users from repository."""
    # Arrange
    user1 = User(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        state=UserState.ACTIVE,
    )
    user2 = User(
        name="Jane",
        vorname="Smith",
        display_name="janesmith",
        email="jane@example.com",
        password_hash="hashed_password",
        state=UserState.ACTIVE,
    )
    user_repository.create(user1)
    user_repository.create(user2)

    # Act
    users = user_repository.read_all()

    # Assert
    assert len(users) == 2
    assert users[0].email in ["john@example.com", "jane@example.com"]


def test_user_repository_update(user_repository):
    """Test updating a user in repository."""
    # Arrange
    user = User(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        state=UserState.ACTIVE,
    )
    created_user = user_repository.create(user)

    # Modify user
    created_user.name = "Jane"
    created_user.state = UserState.INACTIVE

    # Act
    updated_user = user_repository.update(created_user.id, created_user)

    # Assert
    assert updated_user.name == "Jane"
    assert updated_user.state == UserState.INACTIVE


def test_user_repository_delete(user_repository):
    """Test deleting a user from repository."""
    # Arrange
    user = User(
        name="John",
        vorname="Doe",
        display_name="johndoe",
        email="john@example.com",
        password_hash="hashed_password",
        state=UserState.ACTIVE,
    )
    created_user = user_repository.create(user)

    # Act
    result = user_repository.delete(created_user.id)

    # Assert
    assert result is True

    # Verify deletion
    found_user = user_repository.read(created_user.id)
    assert found_user is None
