"""
Unit tests for PostController business logic.

Tests the controller layer in isolation by mocking the service layer.
Each test focuses on a single endpoint and its response handling.
"""

from datetime import date

import pytest
from app.controller.v1.dto.post_dto import PostDto
from app.controller.v1.post_controller import PostController
from app.data.v1.model.post import Post, PostState
from app.service.v1.post_service import PostService
from fastapi import APIRouter, HTTPException


@pytest.fixture
def mock_service(mocker):
    """Create a mocked PostService instance."""
    return mocker.Mock(spec=PostService)


@pytest.fixture
def router():
    """Create a FastAPI router for testing."""
    return APIRouter()


@pytest.fixture
def post_controller(mocker, mock_service, router):
    """Create a PostController with mocked service."""
    # Mock the route config
    mocker.patch(
        "app.controller.v1.post_controller.get_route_config",
        return_value=mocker.Mock(
            prefix="/v1/post",
            tags=["posts"],
            description="Post management endpoints",
        ),
    )
    mocker.patch("app.controller.v1.post_controller.logger")

    controller = PostController(router, mock_service)
    controller.service = mock_service
    return controller


class TestPostControllerCreate:
    """Tests for POST endpoint (Create)."""

    def test_create_post_calls_service_create(self, mocker, post_controller, mock_service):
        """Test that create_post calls service.create with correct DTO."""
        # Arrange
        post_dto = PostDto(
            title="Test Post",
            subtext="A test post",
            content="This is test content",
            author="Test Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        created_post = Post(
            id=1,
            title="Test Post",
            subtext="A test post",
            content="This is test content",
            author="Test Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        mock_service.create.return_value = created_post

        # Act
        result = post_controller.service.create(post_dto)

        # Assert
        assert result.id == 1
        assert result.title == "Test Post"
        mock_service.create.assert_called_once_with(post_dto)

    def test_create_post_with_draft_state(self, mocker, post_controller, mock_service):
        """Test creating a post with DRAFT state."""
        # Arrange
        post_dto = PostDto(
            title="Draft Post",
            subtext="A draft post",
            content="Draft content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.DRAFT,
        )
        created_post = Post(
            id=1,
            title="Draft Post",
            subtext="A draft post",
            content="Draft content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.DRAFT,
        )
        mock_service.create.return_value = created_post

        # Act
        result = post_controller.service.create(post_dto)

        # Assert
        assert result.state == PostState.DRAFT
        mock_service.create.assert_called_once()

    def test_create_post_returns_dto_with_id(self, mocker, post_controller, mock_service):
        """Test that created post includes generated ID."""
        # Arrange
        post_dto = PostDto(
            title="Test",
            subtext="Test",
            content="Content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        created_post = Post(
            id=1,
            title="Test",
            subtext="Test",
            content="Content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        mock_service.create.return_value = created_post

        # Act
        result = post_controller.service.create(post_dto)

        # Assert
        assert result.id is not None
        assert isinstance(result.id, int)


class TestPostControllerRead:
    """Tests for GET /{id} endpoint (Read)."""

    def test_read_existing_post(self, mocker, post_controller, mock_service):
        """Test reading an existing post."""
        # Arrange
        post_id = 1
        expected_post = Post(
            id=post_id,
            title="Readable Post",
            subtext="Can be read",
            content="Content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        mock_service.read.return_value = expected_post

        # Act
        result = post_controller.service.read(post_id)

        # Assert
        assert result.id == post_id
        assert result.title == "Readable Post"
        mock_service.read.assert_called_once_with(post_id)

    def test_read_nonexistent_post_returns_none(self, mocker, post_controller, mock_service):
        """Test reading a non-existent post returns None."""
        # Arrange
        post_id = 9999
        mock_service.read.return_value = None

        # Act
        result = post_controller.service.read(post_id)

        # Assert
        assert result is None
        mock_service.read.assert_called_once_with(post_id)

    def test_read_post_preserves_all_fields(self, mocker, post_controller, mock_service):
        """Test that read preserves all fields."""
        # Arrange
        expected_post = Post(
            id=1,
            title="Complete Post",
            subtext="Full details",
            content="Full content here",
            author="John Doe",
            date=date(2025, 12, 7),
            state=PostState.PUBLISHED,
        )
        mock_service.read.return_value = expected_post

        # Act
        result = post_controller.service.read(1)

        # Assert
        assert result.title == "Complete Post"
        assert result.subtext == "Full details"
        assert result.content == "Full content here"
        assert result.author == "John Doe"


class TestPostControllerReadAll:
    """Tests for GET endpoint (Read All)."""

    def test_read_all_returns_list(self, mocker, post_controller, mock_service):
        """Test that read_all returns list of posts."""
        # Arrange
        expected_posts = [
            Post(
                id=1,
                title="Post 1",
                subtext="Sub 1",
                content="Content 1",
                author="Author",
                date=date(2025, 1, 15),
                state=PostState.PUBLISHED,
            ),
            Post(
                id=2,
                title="Post 2",
                subtext="Sub 2",
                content="Content 2",
                author="Author",
                date=date(2025, 1, 15),
                state=PostState.PUBLISHED,
            ),
        ]
        mock_service.read_all.return_value = expected_posts

        # Act
        result = post_controller.service.read_all(skip=0, limit=100)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 2
        mock_service.read_all.assert_called_once_with(skip=0, limit=100)

    def test_read_all_returns_all_created_posts(self, mocker, post_controller, mock_service):
        """Test that read_all returns all posts."""
        # Arrange
        expected_posts = [
            Post(
                id=i,
                title=f"Post {i}",
                subtext=f"Subtext {i}",
                content=f"Content {i}",
                author=f"Author {i}",
                date=date(2025, 1, 15),
                state=PostState.PUBLISHED,
            )
            for i in range(1, 4)
        ]
        mock_service.read_all.return_value = expected_posts

        # Act
        result = post_controller.service.read_all(skip=0, limit=100)

        # Assert
        assert len(result) == 3

    def test_read_all_with_skip_parameter(self, mocker, post_controller, mock_service):
        """Test read_all passes skip parameter to service."""
        # Arrange
        mock_service.read_all.return_value = []

        # Act
        post_controller.service.read_all(skip=2, limit=100)

        # Assert
        mock_service.read_all.assert_called_once_with(skip=2, limit=100)

    def test_read_all_with_limit_parameter(self, mocker, post_controller, mock_service):
        """Test read_all passes limit parameter to service."""
        # Arrange
        mock_service.read_all.return_value = []

        # Act
        post_controller.service.read_all(skip=0, limit=2)

        # Assert
        mock_service.read_all.assert_called_once_with(skip=0, limit=2)

    def test_read_all_empty_returns_empty_list(self, mocker, post_controller, mock_service):
        """Test read_all returns empty list when no posts."""
        # Arrange
        mock_service.read_all.return_value = []

        # Act
        result = post_controller.service.read_all(skip=0, limit=100)

        # Assert
        assert isinstance(result, list)
        assert len(result) == 0


class TestPostControllerUpdate:
    """Tests for PUT /{id} endpoint (Update)."""

    def test_update_existing_post(self, mocker, post_controller, mock_service):
        """Test updating an existing post."""
        # Arrange
        post_id = 1
        update_dto = PostDto(
            title="Updated Title",
            subtext="Updated",
            content="Updated content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        updated_post = Post(
            id=post_id,
            title="Updated Title",
            subtext="Updated",
            content="Updated content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        mock_service.update.return_value = updated_post

        # Act
        result = post_controller.service.update(post_id, update_dto)

        # Assert
        assert result.title == "Updated Title"
        assert result.state == PostState.PUBLISHED
        mock_service.update.assert_called_once_with(post_id, update_dto)

    def test_update_nonexistent_post_returns_none(self, mocker, post_controller, mock_service):
        """Test updating a non-existent post returns None."""
        # Arrange
        post_id = 9999
        update_dto = PostDto(
            title="Updated",
            subtext="Updated",
            content="Content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        mock_service.update.return_value = None

        # Act
        result = post_controller.service.update(post_id, update_dto)

        # Assert
        assert result is None

    def test_update_post_partially(self, mocker, post_controller, mock_service):
        """Test updating some fields of a post."""
        # Arrange
        post_id = 1
        update_dto = PostDto(
            title="New Title",
            subtext="Subtext",
            content="Content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        updated_post = Post(
            id=post_id,
            title="New Title",
            subtext="Subtext",
            content="Content",
            author="Author",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        mock_service.update.return_value = updated_post

        # Act
        result = post_controller.service.update(post_id, update_dto)

        # Assert
        assert result.title == "New Title"
        assert result.state == PostState.PUBLISHED


class TestPostControllerDelete:
    """Tests for DELETE /{id} endpoint (Delete)."""

    def test_delete_existing_post(self, mocker, post_controller, mock_service):
        """Test deleting an existing post."""
        # Arrange
        post_id = 1
        mock_service.delete.return_value = True

        # Act
        result = post_controller.service.delete(post_id)

        # Assert
        assert result is True
        mock_service.delete.assert_called_once_with(post_id)

    def test_delete_nonexistent_post_returns_false(self, mocker, post_controller, mock_service):
        """Test deleting a non-existent post returns False."""
        # Arrange
        post_id = 9999
        mock_service.delete.return_value = False

        # Act
        result = post_controller.service.delete(post_id)

        # Assert
        assert result is False

    def test_delete_calls_service_delete(self, mocker, post_controller, mock_service):
        """Test that delete calls service.delete with correct ID."""
        # Arrange
        post_id = 1
        mock_service.delete.return_value = True

        # Act
        post_controller.service.delete(post_id)

        # Assert
        mock_service.delete.assert_called_once_with(post_id)


class TestPostControllerDTOHandling:
    """Tests for DTO handling and validation."""

    def test_create_with_all_fields(self, mocker, post_controller, mock_service):
        """Test creating post with all DTO fields."""
        # Arrange
        post_dto = PostDto(
            title="Complete",
            subtext="Full",
            content="Full content",
            author="Author Name",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        created_post = Post(
            id=1,
            title="Complete",
            subtext="Full",
            content="Full content",
            author="Author Name",
            date=date(2025, 1, 15),
            state=PostState.PUBLISHED,
        )
        mock_service.create.return_value = created_post

        # Act
        result = post_controller.service.create(post_dto)

        # Assert
        assert result.title == post_dto.title
        assert result.author == post_dto.author
        assert result.state == post_dto.state

    def test_update_preserves_dto_fields(self, mocker, post_controller, mock_service):
        """Test that update preserves all DTO fields."""
        # Arrange
        update_dto = PostDto(
            title="Updated",
            subtext="Updated Sub",
            content="Updated Content",
            author="Updated Author",
            date=date(2025, 12, 7),
            state=PostState.ARCHIVED,
        )
        updated_post = Post(
            id=1,
            title="Updated",
            subtext="Updated Sub",
            content="Updated Content",
            author="Updated Author",
            date=date(2025, 12, 7),
            state=PostState.ARCHIVED,
        )
        mock_service.update.return_value = updated_post

        # Act
        result = post_controller.service.update(1, update_dto)

        # Assert
        assert result.title == update_dto.title
        assert result.content == update_dto.content
        assert result.state == update_dto.state
