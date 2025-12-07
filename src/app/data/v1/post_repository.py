from sqlmodel import Session

from app.data.v1.base_repository import BaseRepository
from app.data.v1.model.post import Post


class PostRepository(BaseRepository[Post]):
    """
    Repository for Post entity providing CRUD operations.

    Inherits from BaseRepository with Post as the entity type.
    Can be extended with custom query methods specific to Post.
    """

    def __init__(self, session: Session):
        """
        Initialize PostRepository with database session.

        Args:
            session: SQLModel database session
        """
        super().__init__(session, Post)
