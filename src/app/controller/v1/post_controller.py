from fastapi import APIRouter, HTTPException, status
from typing import List
from app.controller.v1.base_controller import BaseController
from app.service.v1.post_service import PostService
from app.data.v1.model.post import Post
from app.controller.v1.dto.post_dto import PostDto
from app.config.routes import get_route_config
from app.config.logger import get_logger

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
            description="Create a new post",
        )
        async def create_post(dto: PostDto) -> PostDto:
            """Create a new post."""
            logger.debug(f"Creating post: {dto.title}")
            return self.service.create(dto)

        @self.router.get(
            "/{id}",
            response_model=PostDto,
            tags=tags,
            summary="Read Post",
            description="Retrieve a post by ID",
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
            response_model=List[PostDto],
            tags=tags,
            summary="Read All Posts",
            description="Retrieve all posts with pagination",
        )
        async def read_all_posts(skip: int = 0, limit: int = 100) -> List[PostDto]:
            """Read all posts with pagination."""
            logger.debug(f"Reading all posts with skip={skip}, limit={limit}")
            return self.service.read_all(skip, limit)

        @self.router.put(
            "/{id}",
            response_model=PostDto,
            tags=tags,
            summary="Update Post",
            description="Update an existing post",
        )
        async def update_post(id: int, dto: PostDto) -> PostDto:
            """Update a post."""
            logger.debug(f"Updating post with ID: {id}")
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
            description="Delete a post",
        )
        async def delete_post(id: int) -> None:
            """Delete a post."""
            logger.debug(f"Deleting post with ID: {id}")
            success = self.service.delete(id)
            if not success:
                logger.warning(f"Post not found with ID: {id}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Post with id {id} not found",
                )