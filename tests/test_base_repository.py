from datetime import date

import pytest
from app.data.v1.model.post import Post, PostState
from app.data.v1.post_repository import PostRepository
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


@pytest.fixture(name="post_repository")
def post_repository_fixture(session: Session) -> PostRepository:
    """Create a PostRepository instance for testing."""
    return PostRepository(session)


class TestBaseRepository:
    """Tests for BaseRepository with Post entity."""

    def test_create_post_returns_created_entity(
        self, post_repository: PostRepository
    ):
        """Test that create returns the created entity with ID."""
        # Arrange
        post = Post(
            title="Test Post",
            content="Test Content",
            author="John Doe",
            date=date(2025, 1, 1),
        )

        # Act
        created_post = post_repository.create(post)

        # Assert
        assert created_post.id is not None
        assert created_post.title == "Test Post"
        assert created_post.author == "John Doe"

    def test_read_post_by_id_returns_entity(self, post_repository: PostRepository):
        """Test that read returns the entity by ID."""
        # Arrange
        post = Post(
            title="Test Post",
            content="Test Content",
            author="John Doe",
            date=date(2025, 1, 1),
        )
        created_post = post_repository.create(post)

        # Act
        read_post = post_repository.read(created_post.id)

        # Assert
        assert read_post is not None
        assert read_post.id == created_post.id
        assert read_post.title == "Test Post"

    def test_read_post_nonexistent_returns_none(self, post_repository: PostRepository):
        """Test that read returns None for non-existent ID."""
        # Act
        result = post_repository.read(999)

        # Assert
        assert result is None

    def test_read_all_posts_returns_list(self, post_repository: PostRepository):
        """Test that read_all returns list of posts."""
        # Arrange
        post1 = Post(
            title="Post 1", content="Content 1", author="Author 1", date=date(2025, 1, 1)
        )
        post2 = Post(
            title="Post 2", content="Content 2", author="Author 2", date=date(2025, 1, 2)
        )
        post_repository.create(post1)
        post_repository.create(post2)

        # Act
        posts = post_repository.read_all()

        # Assert
        assert len(posts) == 2
        assert posts[0].title == "Post 1"
        assert posts[1].title == "Post 2"

    def test_read_all_posts_with_pagination(self, post_repository: PostRepository):
        """Test that read_all respects pagination parameters."""
        # Arrange
        for i in range(5):
            post = Post(
                title=f"Post {i}",
                content=f"Content {i}",
                author=f"Author {i}",
                date=date(2025, 1, 1),
            )
            post_repository.create(post)

        # Act
        posts = post_repository.read_all(skip=1, limit=2)

        # Assert
        assert len(posts) == 2

    def test_update_post_modifies_entity(self, post_repository: PostRepository):
        """Test that update modifies entity fields."""
        # Arrange
        post = Post(
            title="Original Title",
            content="Original Content",
            author="Original Author",
            date=date(2025, 1, 1),
        )
        created_post = post_repository.create(post)

        # Act
        updated_post = Post(
            title="Updated Title",
            content="Updated Content",
            author="Updated Author",
            date=date(2025, 1, 2),
            state=PostState.PUBLISHED,
        )
        result = post_repository.update(created_post.id, updated_post)

        # Assert
        assert result is not None
        assert result.title == "Updated Title"
        assert result.content == "Updated Content"
        assert result.author == "Updated Author"
        assert result.state == PostState.PUBLISHED

    def test_update_nonexistent_post_returns_none(self, post_repository: PostRepository):
        """Test that update returns None for non-existent ID."""
        # Arrange
        post = Post(
            title="Test", content="Content", author="Author", date=date(2025, 1, 1)
        )

        # Act
        result = post_repository.update(999, post)

        # Assert
        assert result is None

    def test_delete_post_removes_entity(self, post_repository: PostRepository):
        """Test that delete removes the entity."""
        # Arrange
        post = Post(
            title="Test Post",
            content="Test Content",
            author="John Doe",
            date=date(2025, 1, 1),
        )
        created_post = post_repository.create(post)

        # Act
        success = post_repository.delete(created_post.id)

        # Assert
        assert success is True
        assert post_repository.read(created_post.id) is None

    def test_delete_nonexistent_post_returns_false(self, post_repository: PostRepository):
        """Test that delete returns False for non-existent ID."""
        # Act
        result = post_repository.delete(999)

        # Assert
        assert result is False
