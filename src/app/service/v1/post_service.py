from app.controller.v1.dto.post_dto import PostDto
from app.data.v1.model.post import Post
from app.data.v1.post_repository import PostRepository
from app.service.v1.base_service import BaseService


class PostService(BaseService[Post, PostDto]):
    """
    Service for Post entity providing CRUD operations with DTO mapping.

    Inherits from BaseService with Post entity and PostDto DTO.
    Can be extended with custom business logic methods.
    """

    def __init__(self, repository: PostRepository):
        """
        Initialize PostService with PostRepository.

        Args:
            repository: The PostRepository instance
        """
        super().__init__(repository, Post, PostDto)
