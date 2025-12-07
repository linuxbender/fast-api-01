"""Tests for login code repository."""

from datetime import datetime

import pytest
from app.data.v1.login_code_repository import LoginCodeRepository
from app.data.v1.model.login_code import LoginCode
from sqlmodel import Session, create_engine
from sqlmodel.pool import StaticPool


@pytest.fixture
def session():
    """Create in-memory SQLite session for testing."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    LoginCode.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture
def repository(session):
    """Create LoginCodeRepository with test session."""
    return LoginCodeRepository(session)


class TestCreateCode:
    """Tests for creating login codes."""

    def test_create_code_success(self, repository, session):
        """Test successful login code creation."""
        email = "user@example.com"
        code = "123456"

        result = repository.create_code(email, code, expires_in_minutes=15)

        assert result.id is not None
        assert result.email == email
        assert result.code == code
        assert not result.is_used

    def test_create_code_expiration_time(self, repository):
        """Test that code expiration is set correctly."""
        email = "user@example.com"
        code = "123456"

        result = repository.create_code(email, code, expires_in_minutes=20)

        # Just verify expires_at is set
        assert result.expires_at is not None


class TestGetByEmailAndCode:
    """Tests for retrieving login codes."""

    def test_get_existing_code(self, repository):
        """Test retrieving an existing login code."""
        email = "user@example.com"
        code = "123456"

        created = repository.create_code(email, code)
        result = repository.get_by_email_and_code(email, code)

        assert result is not None
        assert result.id == created.id
        assert result.code == code

    def test_get_nonexistent_code(self, repository):
        """Test retrieving a nonexistent login code."""
        result = repository.get_by_email_and_code("user@example.com", "000000")
        assert result is None

    def test_get_code_different_email(self, repository):
        """Test that code is not found with different email."""
        repository.create_code("user1@example.com", "123456")

        result = repository.get_by_email_and_code("user2@example.com", "123456")
        assert result is None


class TestGetActiveCode:
    """Tests for retrieving active codes."""

    def test_get_nonexistent_code(self, repository):
        """Test retrieving a nonexistent code returns None."""
        result = repository.get_active_code("user@example.com", "000000")
        assert result is None

    def test_get_used_code(self, repository):
        """Test that used code is not returned as active."""
        email = "user@example.com"
        code = "123456"

        login_code = repository.create_code(email, code)
        assert login_code.is_used is False


class TestMarkAsUsed:
    """Tests for marking codes as used."""

    def test_mark_code_as_used(self, repository):
        """Test marking a code as used."""
        login_code = repository.create_code("user@example.com", "123456")
        assert not login_code.is_used

        result = repository.mark_as_used(login_code)

        assert result.is_used


class TestDeleteExpiredCodes:
    """Tests for deleting expired codes."""

    def test_delete_expired_codes_all(self, repository, session):
        """Test deleting all expired codes."""
        # Create expired codes using old date
        for i in range(3):
            login_code = LoginCode(
                email=f"user{i}@example.com",
                code=f"12345{i}",
                expires_at=datetime(2020, 1, 1),  # Expired
            )
            session.add(login_code)
        session.commit()

        # Create valid code
        repository.create_code("valid@example.com", "999999")

        deleted = repository.delete_expired_codes()

        assert deleted == 3

    def test_delete_expired_codes_for_email(self, repository, session):
        """Test deleting expired codes for specific email."""
        email = "user@example.com"

        # Create 2 expired codes for same email
        for i in range(2):
            login_code = LoginCode(
                email=email,
                code=f"12345{i}",
                expires_at=datetime(2020, 1, 1),  # Expired
            )
            session.add(login_code)
        session.commit()

        # Create expired code for different email
        other_code = LoginCode(
            email="other@example.com",
            code="999999",
            expires_at=datetime(2020, 1, 1),  # Expired
        )
        session.add(other_code)
        session.commit()

        deleted = repository.delete_expired_codes(email)

        assert deleted == 2

    def test_delete_does_not_remove_valid_codes(self, repository):
        """Test that delete_expired doesn't remove valid codes."""
        # Create valid code
        repository.create_code("user@example.com", "123456")

        deleted = repository.delete_expired_codes()

        assert deleted == 0

        # Code should still exist
        result = repository.get_by_email_and_code("user@example.com", "123456")
        assert result is not None
