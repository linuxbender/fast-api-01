"""Repository for login codes."""

from datetime import UTC, datetime, timedelta

from sqlmodel import Session, select

from app.data.v1.base_repository import BaseRepository
from app.data.v1.model.login_code import LoginCode


class LoginCodeRepository(BaseRepository[LoginCode]):
    """Repository for managing login codes."""

    def __init__(self, session: Session):
        """Initialize repository.

        Args:
            session: Database session
        """
        super().__init__(session, LoginCode)

    def create_code(self, email: str, code: str, expires_in_minutes: int = 15) -> LoginCode:
        """Create a new login code.

        Args:
            email: User email address
            code: Login code
            expires_in_minutes: Code expiration time in minutes (default: 15)

        Returns:
            Created LoginCode object
        """
        login_code = LoginCode(
            email=email,
            code=code,
            expires_at=datetime.now(UTC) + timedelta(minutes=expires_in_minutes),
        )
        return self.add(login_code)

    def add(self, login_code: LoginCode) -> LoginCode:
        """Add a login code to database.

        Args:
            login_code: LoginCode object to add

        Returns:
            Added LoginCode object with ID
        """
        self.session.add(login_code)
        self.session.commit()
        self.session.refresh(login_code)
        return login_code

    def update_entity(self, login_code: LoginCode) -> LoginCode:
        """Update a login code entity.

        Args:
            login_code: LoginCode object to update

        Returns:
            Updated LoginCode object
        """
        self.session.add(login_code)
        self.session.commit()
        self.session.refresh(login_code)
        return login_code

    def get_by_email_and_code(self, email: str, code: str) -> LoginCode | None:
        """Get login code by email and code.

        Args:
            email: User email address
            code: Login code

        Returns:
            LoginCode object or None if not found
        """
        statement = select(LoginCode).where(
            LoginCode.email == email,
            LoginCode.code == code,
        )
        return self.session.exec(statement).first()

    def get_active_code(self, email: str, code: str) -> LoginCode | None:
        """Get active (valid) login code by email and code.

        Args:
            email: User email address
            code: Login code

        Returns:
            Valid LoginCode object or None if not found or invalid
        """
        login_code = self.get_by_email_and_code(email, code)
        if login_code and login_code.is_valid():
            return login_code
        return None

    def mark_as_used(self, login_code: LoginCode) -> LoginCode:
        """Mark login code as used.

        Args:
            login_code: LoginCode object to mark as used

        Returns:
            Updated LoginCode object
        """
        login_code.is_used = True
        return self.update_entity(login_code)

    def delete_expired_codes(self, email: str | None = None) -> int:
        """Delete expired login codes.

        Args:
            email: Optional email to filter by

        Returns:
            Number of deleted codes
        """
        if email:
            statement = select(LoginCode).where(
                LoginCode.email == email,
                LoginCode.expires_at < datetime.now(UTC),
            )
        else:
            statement = select(LoginCode).where(
                LoginCode.expires_at < datetime.now(UTC),
            )

        codes = self.session.exec(statement).all()
        for code in codes:
            self.session.delete(code)
        self.session.commit()
        return len(codes)
