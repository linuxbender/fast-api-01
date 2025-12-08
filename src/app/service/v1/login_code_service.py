"""Service for managing login codes and passwordless authentication."""

import secrets
import string
from datetime import datetime

from app.config.logger import get_logger
from app.data.v1.login_code_repository import LoginCodeRepository
from app.data.v1.model.login_code import LoginCode
from app.data.v1.user_repository import UserRepository

logger = get_logger(__name__)


class LoginCodeService:
    """Service for passwordless login (magic link/OTP) authentication."""

    def __init__(self, login_code_repo: LoginCodeRepository, user_repo: UserRepository):
        """Initialize service.

        Args:
            login_code_repo: LoginCode repository
            user_repo: User repository
        """
        self.login_code_repo = login_code_repo
        self.user_repo = user_repo

    def generate_code(self, length: int = 6) -> str:
        """Generate a random login code.

        Args:
            length: Code length (default: 6)

        Returns:
            Generated code (digits only)
        """
        characters = string.digits
        return "".join(secrets.choice(characters) for _ in range(length))

    def create_login_code(self, email: str, expires_in_minutes: int = 15) -> LoginCode:
        """Create a new login code for email.

        Invalidates any previous active codes for the email.

        Args:
            email: User email address
            expires_in_minutes: Code expiration time in minutes

        Returns:
            Created LoginCode object

        Raises:
            ValueError: If email is invalid
        """
        if not email or "@" not in email:
            raise ValueError("Invalid email address")

        # Delete any previous active codes for this email
        self.login_code_repo.delete_expired_codes(email)

        code = self.generate_code()
        login_code = self.login_code_repo.create_code(email, code, expires_in_minutes)

        logger.info(f"Login code created for email: {email}")
        return login_code

    def verify_login_code(self, email: str, code: str) -> dict | None:
        """Verify login code.

        Args:
            email: User email address
            code: Login code to verify

        Returns:
            Dictionary with user info if valid, None otherwise:
            {
                "user_id": int,
                "email": str,
                "name": str,
            }

        Raises:
            ValueError: If user not found
        """
        if not email or not code:
            logger.warning("Verify attempt with empty email or code")
            return None

        # Get active login code
        login_code = self.login_code_repo.get_active_code(email, code)

        if not login_code:
            logger.warning(f"Invalid or expired login code for email: {email}")
            return None

        # Check if user exists
        user = self.user_repo.get_by_email(email)
        if not user:
            logger.warning(f"User not found during code verification: {email}")
            raise ValueError(f"User not found: {email}")

        # Mark code as used
        self.login_code_repo.mark_as_used(login_code)
        logger.info(f"Login code verified for email: {email}")

        return {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
        }

    def code_is_valid(self, login_code: LoginCode) -> bool:
        """Check if login code is valid.

        Args:
            login_code: LoginCode object

        Returns:
            True if code is valid, False otherwise
        """
        return login_code.is_valid()

    def code_expiration_time(self, login_code: LoginCode) -> int:
        """Get remaining time until code expiration in seconds.

        Args:
            login_code: LoginCode object

        Returns:
            Seconds until expiration, or -1 if already expired
        """
        if login_code.is_expired():
            return -1

        delta = login_code.expires_at - datetime.now()
        return int(delta.total_seconds())
