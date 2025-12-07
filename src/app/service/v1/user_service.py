"""User service for business logic."""

from datetime import UTC, datetime

import bcrypt

from app.controller.v1.dto.user_dto import UserCreateDto, UserResponseDto
from app.data.v1.model.user import User, UserState
from app.data.v1.user_repository import UserRepository


class UserService:
    """User service providing business logic for user operations."""

    def __init__(self, repository: UserRepository):
        """Initialize service with repository.

        Args:
            repository: The user repository instance
        """
        self.repository = repository

    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt.

        Args:
            password: Plain text password

        Returns:
            Hashed password
        """
        salt = bcrypt.gensalt(rounds=12)
        return bcrypt.hashpw(password.encode(), salt).decode()

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash.

        Args:
            password: Plain text password
            password_hash: Hashed password

        Returns:
            True if password matches, False otherwise
        """
        return bcrypt.checkpw(password.encode(), password_hash.encode())

    def create_user(self, dto: UserCreateDto) -> UserResponseDto:
        """Create a new user.

        Args:
            dto: User creation DTO

        Returns:
            Created user as response DTO

        Raises:
            ValueError: If email or display_name already exists
        """
        # Check if email exists
        if self.repository.get_by_email(dto.email):
            raise ValueError(f"Email {dto.email} is already registered")

        # Check if display_name exists
        if self.repository.get_by_display_name(dto.display_name):
            raise ValueError(f"Display name {dto.display_name} is already taken")

        # Create user entity
        user = User(
            name=dto.name,
            vorname=dto.vorname,
            display_name=dto.display_name,
            email=dto.email,
            password_hash=self.hash_password(dto.password),
            state=UserState.ACTIVE,
        )

        # Save to database
        created_user = self.repository.create(user)

        return self._user_to_dto(created_user)

    def authenticate_user(self, email: str, password: str) -> User | None:
        """Authenticate user by email and password.

        Args:
            email: User email
            password: Plain text password

        Returns:
            User object if authentication succeeds, None otherwise
        """
        user = self.repository.get_active_by_email(email)
        if not user:
            return None

        if not self.verify_password(password, user.password_hash):
            return None

        # Update last_login
        user.last_login = datetime.now(UTC)
        self.repository.update(user.id, user)

        return user

    def get_user_by_id(self, user_id: int) -> UserResponseDto | None:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User response DTO or None if not found
        """
        user = self.repository.read(user_id)
        if not user:
            return None
        return self._user_to_dto(user)

    def get_user_by_email(self, email: str) -> UserResponseDto | None:
        """Get user by email.

        Args:
            email: User email

        Returns:
            User response DTO or None if not found
        """
        user = self.repository.get_by_email(email)
        if not user:
            return None
        return self._user_to_dto(user)

    def deactivate_user(self, user_id: int) -> UserResponseDto | None:
        """Deactivate user account.

        Args:
            user_id: User ID

        Returns:
            Updated user response DTO or None if not found
        """
        user = self.repository.read(user_id)
        if not user:
            return None

        user.state = UserState.INACTIVE
        user.changed_at = datetime.now(UTC)
        updated_user = self.repository.update(user_id, user)

        return self._user_to_dto(updated_user)

    def reset_password(self, user_id: int, new_password: str) -> UserResponseDto | None:
        """Reset user password.

        Args:
            user_id: User ID
            new_password: New password (must meet strength requirements)

        Returns:
            Updated user response DTO or None if not found
        """
        user = self.repository.read(user_id)
        if not user:
            return None

        user.password_hash = self.hash_password(new_password)
        user.changed_at = datetime.now(UTC)
        updated_user = self.repository.update(user_id, user)

        return self._user_to_dto(updated_user)

    @staticmethod
    def _user_to_dto(user: User) -> UserResponseDto:
        """Convert User entity to UserResponseDto.

        Args:
            user: User entity

        Returns:
            User response DTO
        """
        return UserResponseDto(
            id=user.id,
            name=user.name,
            vorname=user.vorname,
            display_name=user.display_name,
            email=user.email,
            state=user.state.value,
        )
