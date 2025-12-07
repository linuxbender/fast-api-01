from datetime import date

import pytest
from app.controller.v1.dto.post_dto import PostDto
from app.data.v1.model.post import Post, PostState
from app.data.v1.post_repository import PostRepository
from app.service.v1.post_service import PostService
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="post_service")
def post_service_fixture(session: Session) -> PostService:
    """Create a PostService instance for testing."""
    repository = PostRepository(session)
    return PostService(repository)


class TestBaseService:
    """Tests for BaseService with Post entity and DTO mapping."""

    def test_create_post_with_dto_returns_dto(self, post_service: PostService):
        """Test that create converts DTO to entity and back."""
        # Arrange
        post_dto = PostDto(
            title="Test Post",
            content="Test Content",
            author="John Doe",
            date=date(2025, 1, 1),
        )

        # Act
        created_dto = post_service.create(post_dto)

        # Assert
        assert created_dto.id is not None
        assert created_dto.title == "Test Post"
        assert created_dto.author == "John Doe"

    def test_read_post_returns_dto(self, post_service: PostService):
        """Test that read returns DTO."""
        # Arrange
        post_dto = PostDto(
            title="Test Post",
            content="Test Content",
            author="John Doe",
            date=date(2025, 1, 1),
        )
        created_dto = post_service.create(post_dto)

        # Act
        read_dto = post_service.read(created_dto.id)

        # Assert
        assert read_dto is not None
        assert read_dto.id == created_dto.id
        assert read_dto.title == "Test Post"

    def test_read_nonexistent_returns_none(self, post_service: PostService):
        """Test that read returns None for non-existent ID."""
        # Act
        result = post_service.read(999)

        # Assert
        assert result is None

    def test_read_all_returns_list_of_dtos(self, post_service: PostService):
        """Test that read_all returns list of DTOs."""
        # Arrange
        post1 = PostDto(
            title="Post 1", content="Content 1", author="Author 1", date=date(2025, 1, 1)
        )
        post2 = PostDto(
            title="Post 2", content="Content 2", author="Author 2", date=date(2025, 1, 2)
        )
        post_service.create(post1)
        post_service.create(post2)

        # Act
        posts = post_service.read_all()

        # Assert
        assert len(posts) == 2
        assert isinstance(posts[0], PostDto)
        assert posts[0].title == "Post 1"

    def test_update_post_with_dto_returns_updated_dto(self, post_service: PostService):
        """Test that update converts DTO and returns updated DTO."""
        # Arrange
        original_dto = PostDto(
            title="Original Title",
            content="Original Content",
            author="Original Author",
            date=date(2025, 1, 1),
        )
        created_dto = post_service.create(original_dto)

        # Act
        updated_dto = PostDto(
            title="Updated Title",
            content="Updated Content",
            author="Updated Author",
            date=date(2025, 1, 2),
            state=PostState.PUBLISHED,
        )
        result = post_service.update(created_dto.id, updated_dto)

        # Assert
        assert result is not None
        assert result.title == "Updated Title"
        assert result.state == PostState.PUBLISHED

    def test_delete_post_returns_true(self, post_service: PostService):
        """Test that delete returns True for existing entity."""
        # Arrange
        post_dto = PostDto(
            title="Test Post",
            content="Test Content",
            author="John Doe",
            date=date(2025, 1, 1),
        )
        created_dto = post_service.create(post_dto)

        # Act
        success = post_service.delete(created_dto.id)

        # Assert
        assert success is True

    def test_dto_to_entity_conversion(self, post_service: PostService):
        """Test DTO to entity conversion."""
        # Arrange
        post_dto = PostDto(
            id=1,
            title="Test",
            content="Content",
            author="Author",
            date=date(2025, 1, 1),
            state=PostState.PUBLISHED,
        )

        # Act
        entity = post_service.dto_to_entity(post_dto)

        # Assert
        assert isinstance(entity, Post)
        assert entity.title == "Test"
        assert entity.state == PostState.PUBLISHED

    def test_entity_to_dto_conversion(self, post_service: PostService):
        """Test entity to DTO conversion."""
        # Arrange
        entity = Post(
            id=1,
            title="Test",
            content="Content",
            author="Author",
            date=date(2025, 1, 1),
            state=PostState.DRAFT,
        )

        # Act
        dto = post_service.entity_to_dto(entity)

        # Assert
        assert isinstance(dto, PostDto)
        assert dto.title == "Test"
        assert dto.state == PostState.DRAFT
