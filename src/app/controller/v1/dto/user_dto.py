"""User Data Transfer Objects (DTOs)."""

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator


class UserCreateDto(BaseModel):
    """DTO for user creation."""

    name: str
    vorname: str
    display_name: str
    email: EmailStr
    re_email: EmailStr
    password: str
    re_password: str

    @field_validator("name", "vorname", "display_name")
    @classmethod
    def validate_string_length(cls, value: str) -> str:
        """Validate string length."""
        if not value or len(value) > 64:
            raise ValueError("Length must be between 1 and 64 characters")
        return value.strip()

    @field_validator("display_name")
    @classmethod
    def validate_display_name_format(cls, value: str) -> str:
        """Validate display_name format."""
        if not value or len(value) > 128:
            raise ValueError("Display name length must be between 1 and 128 characters")
        return value.strip()

    @field_validator("email", "re_email")
    @classmethod
    def validate_email(cls, value: EmailStr) -> EmailStr:
        """Validate email format."""
        return value

    @field_validator("password", "re_password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        """Validate password strength and format."""
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters long")

        # Check for at least one uppercase letter
        if not any(c.isupper() for c in value):
            raise ValueError("Password must contain at least one uppercase letter [A-Z]")

        # Check for at least one lowercase letter
        if not any(c.islower() for c in value):
            raise ValueError("Password must contain at least one lowercase letter [a-z]")

        # Check for at least one digit
        if not any(c.isdigit() for c in value):
            raise ValueError("Password must contain at least one digit [0-9]")

        # Check for at least one special character
        special_chars = "@!$#-_?+%^&*()"
        if not any(c in special_chars for c in value):
            raise ValueError(
                f"Password must contain at least one special character {special_chars}"
            )

        return value

    def model_post_init(self, __context) -> None:
        """Validate that email and re_email match."""
        if self.email != self.re_email:
            raise ValueError("Email and Re-Email must match")

        if self.password != self.re_password:
            raise ValueError("Password and Re-Password must match")


class UserResponseDto(BaseModel):
    """DTO for user response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    vorname: str
    display_name: str
    email: str
    state: str


class LoginRequestDto(BaseModel):
    """DTO for login request."""

    email: EmailStr
    password: str


class LoginResponseDto(BaseModel):
    """DTO for login response."""

    access_token: str
    token_type: str
    user: UserResponseDto


class MeResponseDto(BaseModel):
    """DTO for /me endpoint response."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    vorname: str
    display_name: str
    email: str
    state: str
    rights: list[str]
    groups: list[str]
