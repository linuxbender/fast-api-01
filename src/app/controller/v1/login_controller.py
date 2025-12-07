"""Login controller for authentication endpoints."""

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlmodel import Session

from app.config.auth_dependencies import get_current_user
from app.config.logger import get_logger
from app.controller.v1.dto.user_dto import (
    LoginRequestDto,
    LoginResponseDto,
    MeResponseDto,
    UserCreateDto,
    UserResponseDto,
)
from app.data.database import get_session
from app.data.v1.user_repository import UserRepository
from app.security.jwt import TokenData, create_access_token
from app.service.v1.user_service import UserService

logger = get_logger(__name__)


class LoginController:
    """Login controller handling authentication endpoints."""

    def __init__(self, router: APIRouter):
        """Initialize controller with router.

        Args:
            router: FastAPI router instance
        """
        self.router = router
        self.register_routes()

    def register_routes(self) -> None:
        """Register all authentication routes."""

        @self.router.post(
            "/login",
            response_model=LoginResponseDto,
            status_code=status.HTTP_200_OK,
            summary="Login",
            description="Login with email and password",
        )
        async def login(
            request: LoginRequestDto,
            response: Response,
            session: Session = Depends(get_session),  # noqa: B008
        ) -> LoginResponseDto:
            """Login with email and password."""
            logger.debug(f"Login attempt for email: {request.email}")
            user_repo = UserRepository(session)
            user_service = UserService(user_repo)

            # Authenticate user
            user = user_service.authenticate_user(request.email, request.password)
            if not user:
                logger.warning(f"Failed login attempt for email: {request.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password",
                )

            # Create access token
            token_data = {
                "user_id": user.id,
                "email": user.email,
                "rights": ["READ", "EDIT"],
                "groups": ["ACTIVE_USER"],
            }
            access_token = create_access_token(
                data=token_data,
                expires_delta=timedelta(minutes=30),
            )

            # Set HTTP-Only Cookie with token
            response.set_cookie(
                key="access_token",
                value=f"bearer {access_token}",
                max_age=30 * 60,  # 30 minutes
                expires=30 * 60,
                httponly=True,
                secure=True,  # HTTPS only
                samesite="strict",
            )

            # Convert user to DTO
            user_dto = user_service.get_user_by_id(user.id)

            return LoginResponseDto(
                access_token=access_token,
                token_type="bearer",
                user=user_dto,
            )

        @self.router.post(
            "/register",
            response_model=UserResponseDto,
            status_code=status.HTTP_201_CREATED,
            summary="Register",
            description="Register a new user",
        )
        async def register(
            request: UserCreateDto,
            session: Session = Depends(get_session),  # noqa: B008
        ) -> UserResponseDto:
            """Register a new user."""
            logger.debug(f"Registration attempt for email: {request.email}")
            user_repo = UserRepository(session)
            user_service = UserService(user_repo)

            try:
                user_dto = user_service.create_user(request)
                logger.info(f"New user registered: {request.email}")
                return user_dto
            except ValueError as e:
                logger.warning(f"Registration failed for {request.email}: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e),
                ) from e

        @self.router.post(
            "/reset-password",
            response_model=UserResponseDto,
            status_code=status.HTTP_200_OK,
            summary="Reset Password",
            description="Reset password for authenticated user",
        )
        async def reset_password(
            user_id: int,
            new_password: str,
            current_user: TokenData = Depends(get_current_user),  # noqa: B008
            session: Session = Depends(get_session),  # noqa: B008
        ) -> UserResponseDto:
            """Reset password for a user."""
            # Only allow users to reset their own password
            if current_user.user_id != user_id:
                logger.warning(
                    f"Unauthorized password reset attempt: user {current_user.user_id} "
                    f"tried to reset password for user {user_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only reset your own password",
                )

            user_repo = UserRepository(session)
            user_service = UserService(user_repo)

            updated_user = user_service.reset_password(user_id, new_password)
            if not updated_user:
                logger.warning(f"User not found for password reset: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            logger.info(f"Password reset for user: {user_id}")
            return updated_user

        @self.router.post(
            "/deactivate",
            response_model=UserResponseDto,
            status_code=status.HTTP_200_OK,
            summary="Deactivate",
            description="Deactivate user profile",
        )
        async def deactivate(
            user_id: int,
            current_user: TokenData = Depends(get_current_user),  # noqa: B008
            session: Session = Depends(get_session),  # noqa: B008
        ) -> UserResponseDto:
            """Deactivate user profile."""
            # Only allow users to deactivate their own account
            if current_user.user_id != user_id:
                logger.warning(
                    f"Unauthorized deactivation attempt: user {current_user.user_id} "
                    f"tried to deactivate user {user_id}"
                )
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only deactivate your own account",
                )

            user_repo = UserRepository(session)
            user_service = UserService(user_repo)

            updated_user = user_service.deactivate_user(user_id)
            if not updated_user:
                logger.warning(f"User not found for deactivation: {user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            logger.info(f"User deactivated: {user_id}")
            return updated_user

        @self.router.get(
            "/me",
            response_model=MeResponseDto,
            status_code=status.HTTP_200_OK,
            summary="Get Current User",
            description="Get current user information and rights",
        )
        async def me(
            current_user: TokenData = Depends(get_current_user),  # noqa: B008
            session: Session = Depends(get_session),  # noqa: B008
        ) -> MeResponseDto:
            """Get current user information and rights."""
            user_repo = UserRepository(session)
            user_service = UserService(user_repo)

            user_dto = user_service.get_user_by_id(current_user.user_id)
            if not user_dto:
                logger.warning(f"User not found in /me endpoint: {current_user.user_id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found",
                )

            return MeResponseDto(
                id=user_dto.id,
                name=user_dto.name,
                vorname=user_dto.vorname,
                display_name=user_dto.display_name,
                email=user_dto.email,
                state=user_dto.state,
                rights=current_user.rights,
                groups=current_user.groups,
            )

        @self.router.post(
            "/logout",
            status_code=status.HTTP_200_OK,
            summary="Logout",
            description="Logout and invalidate JWT token",
        )
        async def logout(
            response: Response,
            current_user: TokenData = Depends(get_current_user),  # noqa: B008
        ) -> dict:
            """Logout by clearing the access token cookie."""
            logger.info(f"User logged out: {current_user.email}")

            # Delete the access_token cookie
            response.delete_cookie(
                key="access_token",
                path="/",
                domain=None,
            )

            return {"message": "Successfully logged out"}

