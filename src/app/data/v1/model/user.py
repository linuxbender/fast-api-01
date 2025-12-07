"""User database model."""

from datetime import UTC, datetime
from enum import Enum

from sqlmodel import Field, SQLModel


class UserState(str, Enum):
    """User account state."""

    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class User(SQLModel, table=True):
    """User database model."""

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(max_length=64, index=True)
    vorname: str = Field(max_length=64)
    display_name: str = Field(max_length=128, unique=True, index=True)
    email: str = Field(max_length=256, unique=True, index=True)
    password_hash: str = Field(max_length=1024)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    changed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_login: datetime | None = Field(default=None)
    state: UserState = Field(default=UserState.ACTIVE)
