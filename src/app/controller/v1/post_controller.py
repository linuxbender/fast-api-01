
from fastapi import APIRouter, Depends, HTTPException, status

from app.config.auth_dependencies import get_current_user
from app.config.logger import get_logger
from app.config.routes import get_route_config
from app.controller.v1.base_controller import BaseController
from app.controller.v1.dto.post_dto import PostDto
from app.data.v1.model.post import Post
from app.security.jwt import TokenData
from app.service.v1.post_service import PostService

logger = get_logger(__name__)


class PostController(BaseController[Post, PostDto]):
    """
    Controller for Post entity providing REST API endpoints.

    Inherits from BaseController with Post entity and PostDto DTO.
    Provides standard CRUD operations via HTTP methods.

    Endpoints are defined in central route configuration: app/config/routes.py
    """

    def __init__(self, router: APIRouter, service: PostService):
        """
        Initialize PostController with router and PostService.

        Args:
            router: FastAPI router instance
            service: The PostService instance
        """
        super().__init__(router, service, PostDto)
        self.route_config = get_route_config("posts")
        logger.info(f"PostController initialized with routes: {self.route_config.prefix}")
        self.register_routes()

    def register_routes(self) -> None:
        """Register all CRUD routes for posts using central route configuration."""
        tags = self.route_config.tags

        @self.router.post(
            "/",
            response_model=PostDto,
            status_code=status.HTTP_201_CREATED,
            tags=tags,
            summary="Create Post",
            description="Create a new post (requires authentication)",
        )
        async def create_post(
            dto: PostDto,
            current_user: TokenData = Depends(get_current_user),  # noqa: B008
        ) -> PostDto:
            """Create a new post (requires authentication)."""
            logger.debug(f"Creating post: {dto.title} by user {current_user.user_id}")
            return self.service.create(dto)

        @self.router.get(
            "/{id}",
            response_model=PostDto,
            tags=tags,
            summary="Read Post",
            description="Retrieve a post by ID (no authentication required)",
        )
        async def read_post(id: int) -> PostDto:
            """Read a post by ID."""
            logger.debug(f"Reading post with ID: {id}")
            entity = self.service.read(id)
            if entity is None:
                logger.warning(f"Post not found with ID: {id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {id} not found",
                )
            return entity

        @self.router.get(
            "/",
            response_model=list[PostDto],
            tags=tags,
            summary="Read All Posts",
            description="Retrieve all posts with pagination (no authentication required)",
        )
        async def read_all_posts(skip: int = 0, limit: int = 100) -> list[PostDto]:
            """Read all posts with pagination."""
            logger.debug(f"Reading all posts with skip={skip}, limit={limit}")
            return self.service.read_all(skip, limit)

        @self.router.put(
            "/{id}",
            response_model=PostDto,
            tags=tags,
            summary="Update Post",
            description="Update an existing post (requires authentication)",
        )
        async def update_post(
            id: int,
            dto: PostDto,
            current_user: TokenData = Depends(get_current_user),  # noqa: B008
        ) -> PostDto:
            """Update a post (requires authentication)."""
            logger.debug(f"Updating post with ID: {id} by user {current_user.user_id}")
            entity = self.service.update(id, dto)
            if entity is None:
                logger.warning(f"Post not found with ID: {id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {id} not found",
                )
            return entity

        @self.router.delete(
            "/{id}",
            status_code=status.HTTP_204_NO_CONTENT,
            tags=tags,
            summary="Delete Post",
            description="Delete a post (requires authentication)",
        )
        async def delete_post(
            id: int,
            current_user: TokenData = Depends(get_current_user),  # noqa: B008
        ) -> None:
            """Delete a post (requires authentication)."""
            logger.debug(f"Deleting post with ID: {id} by user {current_user.user_id}")
            success = self.service.delete(id)
            if not success:
                logger.warning(f"Post not found with ID: {id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {id} not found",
                )
