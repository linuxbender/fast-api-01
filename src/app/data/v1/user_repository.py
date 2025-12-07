"""User repository for database operations."""

from sqlmodel import Session, select

from app.data.v1.base_repository import BaseRepository
from app.data.v1.model.user import User


class UserRepository(BaseRepository[User]):
    """User repository providing user-specific CRUD operations."""

    def __init__(self, session: Session):
        """Initialize repository with session.

        Args:
            session: SQLModel database session
        """
        super().__init__(session, User)

    def get_by_email(self, email: str) -> User | None:
        """Get user by email.

        Args:
            email: User email address

        Returns:
            User object or None if not found
        """
        statement = select(User).where(User.email == email)
        return self.session.exec(statement).first()

    def get_by_display_name(self, display_name: str) -> User | None:
        """Get user by display name.

        Args:
            display_name: User display name

        Returns:
            User object or None if not found
        """
        statement = select(User).where(User.display_name == display_name)
        return self.session.exec(statement).first()

    def get_active_by_email(self, email: str) -> User | None:
        """Get active user by email.

        Args:
            email: User email address

        Returns:
            Active user object or None if not found or inactive
        """
        statement = select(User).where((User.email == email) & (User.state == "ACTIVE"))
        return self.session.exec(statement).first()
