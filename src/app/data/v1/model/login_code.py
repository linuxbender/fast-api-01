"""Login code model for passwordless authentication."""

from datetime import datetime

from sqlmodel import Column, Field, SQLModel, String


class LoginCode(SQLModel, table=True):
    """Login code for passwordless authentication.

    Attributes:
        id: Unique identifier
        email: User email address
        code: 6-digit login code
        expires_at: Expiration timestamp (15 minutes from creation)
        created_at: Creation timestamp
        is_used: Whether code has been used
    """

    __tablename__ = "login_codes"

    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(
        sa_column=Column(String(255), index=True, nullable=False),
        description="User email address",
    )
    code: str = Field(
        sa_column=Column(String(6), index=True, nullable=False),
        description="6-digit login code",
    )
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Code expiration timestamp",
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(),
        description="Code creation timestamp",
    )
    is_used: bool = Field(default=False, description="Whether code has been used")

    def is_expired(self) -> bool:
        """Check if code is expired.

        Returns:
            True if code is expired, False otherwise
        """
        # Database stores naive datetimes - always use naive comparison
        return datetime.now() > self.expires_at

    def is_valid(self) -> bool:
        """Check if code is valid (not expired and not used).

        Returns:
            True if code is valid, False otherwise
        """
        return not self.is_expired() and not self.is_used
