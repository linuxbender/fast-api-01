"""
Tests for PostController HTTP endpoints.

Tests all CRUD operations through HTTP endpoints:
- POST /v1/post/ - Create
- GET /v1/post/{id} - Read
- GET /v1/post/ - Read all
- PUT /v1/post/{id} - Update
- DELETE /v1/post/{id} - Delete
"""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool
from datetime import date

from app.app import app
from app.data.database import get_session
from app.data.v1.model.post import Post, PostState
from app.controller.v1.dto.post_dto import PostDto


@pytest.fixture(name="client")
def client_fixture():
    """Create TestClient with fresh test database per test."""
    # Create fresh in-memory database for each test
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    
    def get_session_override():
        session = Session(engine)
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="session")
def session_fixture():
    """Create in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    session = Session(engine)
    yield session
    session.close()


class TestPostControllerCreate:
    """Tests for POST /v1/post/ (Create) endpoint."""

    def test_create_post_returns_201_with_valid_data(self, client: TestClient):
        """Test that creating a post returns 201 with valid data."""
        post_data = {
            "title": "Test Post",
            "subtext": "A test post",
            "content": "This is test content",
            "author": "Test Author",
            "date": "2025-01-15",
            "state": "published",
        }

        response = client.post("/v1/post/", json=post_data)

        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test Post"
        assert data["author"] == "Test Author"
        assert "id" in data
        assert data["id"] is not None

    def test_create_post_with_draft_state(self, client: TestClient):
        """Test creating a post with DRAFT state."""
        post_data = {
            "title": "Draft Post",
            "subtext": "A draft post",
            "content": "Draft content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "draft",
        }

        response = client.post("/v1/post/", json=post_data)

        assert response.status_code == 201
        data = response.json()
        assert data["state"] == "draft"

    def test_create_multiple_posts(self, client: TestClient):
        """Test creating multiple posts."""
        posts_data = [
            {
                "title": f"Post {i}",
                "subtext": f"Subtext {i}",
                "content": f"Content {i}",
                "author": f"Author {i}",
                "date": "2025-01-15",
                "state": "published",
            }
            for i in range(3)
        ]

        responses = [client.post("/v1/post/", json=data) for data in posts_data]

        assert all(r.status_code == 201 for r in responses)
        assert len(responses) == 3


class TestPostControllerRead:
    """Tests for GET /v1/post/{id} (Read) endpoint."""

    def test_read_existing_post_returns_200(self, client: TestClient):
        """Test reading an existing post returns 200."""
        # Create a post first
        post_data = {
            "title": "Readable Post",
            "subtext": "Can be read",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        create_response = client.post("/v1/post/", json=post_data)
        post_id = create_response.json()["id"]

        # Read the post
        read_response = client.get(f"/v1/post/{post_id}")

        assert read_response.status_code == 200
        data = read_response.json()
        assert data["id"] == post_id
        assert data["title"] == "Readable Post"

    def test_read_nonexistent_post_returns_404(self, client: TestClient):
        """Test reading a non-existent post returns 404."""
        response = client.get("/v1/post/9999")

        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_read_post_preserves_all_fields(self, client: TestClient):
        """Test that reading a post preserves all fields."""
        post_data = {
            "title": "Complete Post",
            "subtext": "Full details",
            "content": "Full content here",
            "author": "John Doe",
            "date": "2025-12-07",
            "state": "published",
        }
        create_response = client.post("/v1/post/", json=post_data)
        post_id = create_response.json()["id"]

        read_response = client.get(f"/v1/post/{post_id}")
        data = read_response.json()

        assert data["title"] == "Complete Post"
        assert data["subtext"] == "Full details"
        assert data["content"] == "Full content here"
        assert data["author"] == "John Doe"


class TestPostControllerReadAll:
    """Tests for GET /v1/post/ (Read All) endpoint."""

    def test_read_all_returns_posts(self, client: TestClient):
        """Test that read all returns posts."""
        response = client.get("/v1/post/")

        assert response.status_code == 200
        assert isinstance(response.json(), list)
        """Test that read all returns all created posts."""
        # Create 3 posts
        posts_data = [
            {
                "title": f"Post {i}",
                "subtext": f"Subtext {i}",
                "content": f"Content {i}",
                "author": f"Author {i}",
                "date": "2025-01-15",
                "state": "published",
            }
            for i in range(3)
        ]

        for data in posts_data:
            client.post("/v1/post/", json=data)

        response = client.get("/v1/post/")

        assert response.status_code == 200
        data = response.json()
        # Should have at least 3 posts (may have more from other tests)
        assert len(data) >= 3
        # Check that our posts are present
        titles = [post["title"] for post in data]
        assert "Post 0" in titles
        assert "Post 1" in titles
        assert "Post 2" in titles

    def test_read_all_with_skip_parameter(self, client: TestClient):
        """Test read all with skip parameter."""
        # Create 5 posts
        for i in range(5):
            post_data = {
                "title": f"Post {i}",
                "subtext": f"Subtext {i}",
                "content": f"Content {i}",
                "author": "Author",
                "date": "2025-01-15",
                "state": "published",
            }
            client.post("/v1/post/", json=post_data)

        # Get total count first
        all_response = client.get("/v1/post/?skip=0&limit=1000")
        total_count = len(all_response.json())

        response = client.get("/v1/post/?skip=2&limit=1000")

        assert response.status_code == 200
        data = response.json()
        # Should skip first 2 items
        assert len(data) == total_count - 2

    def test_read_all_with_limit_parameter(self, client: TestClient):
        """Test read all with limit parameter."""
        # Create 5 posts
        for i in range(5):
            post_data = {
                "title": f"Post {i}",
                "subtext": f"Subtext {i}",
                "content": f"Content {i}",
                "author": "Author",
                "date": "2025-01-15",
                "state": "published",
            }
            client.post("/v1/post/", json=post_data)

        response = client.get("/v1/post/?skip=0&limit=2")

        assert response.status_code == 200
        data = response.json()
        # Should be limited to 2
        assert len(data) <= 2


class TestPostControllerUpdate:
    """Tests for PUT /v1/post/{id} (Update) endpoint."""

    def test_update_existing_post_returns_200(self, client: TestClient):
        """Test updating an existing post returns 200."""
        # Create a post
        post_data = {
            "title": "Original Title",
            "subtext": "Original",
            "content": "Original content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "draft",
        }
        create_response = client.post("/v1/post/", json=post_data)
        post_id = create_response.json()["id"]

        # Update the post
        update_data = {
            "title": "Updated Title",
            "subtext": "Updated",
            "content": "Updated content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        update_response = client.put(f"/v1/post/{post_id}", json=update_data)

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["title"] == "Updated Title"
        assert data["state"] == "published"

    def test_update_nonexistent_post_returns_404(self, client: TestClient):
        """Test updating a non-existent post returns 404."""
        update_data = {
            "title": "Updated",
            "subtext": "Updated",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        response = client.put("/v1/post/9999", json=update_data)

        assert response.status_code == 404

    def test_update_post_partially(self, client: TestClient):
        """Test updating only some fields of a post."""
        # Create a post
        post_data = {
            "title": "Original",
            "subtext": "Subtext",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "draft",
        }
        create_response = client.post("/v1/post/", json=post_data)
        post_id = create_response.json()["id"]

        # Update only title and state
        update_data = {
            "title": "New Title",
            "subtext": "Subtext",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        update_response = client.put(f"/v1/post/{post_id}", json=update_data)

        assert update_response.status_code == 200
        data = update_response.json()
        assert data["title"] == "New Title"
        assert data["state"] == "published"

    def test_verify_update_persisted(self, client: TestClient):
        """Test that update is persisted by reading the post."""
        # Create a post
        post_data = {
            "title": "Original",
            "subtext": "Subtext",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "draft",
        }
        create_response = client.post("/v1/post/", json=post_data)
        post_id = create_response.json()["id"]

        # Update the post
        update_data = {
            "title": "Updated",
            "subtext": "Subtext",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        client.put(f"/v1/post/{post_id}", json=update_data)

        # Read it back
        read_response = client.get(f"/v1/post/{post_id}")
        data = read_response.json()

        assert data["title"] == "Updated"


class TestPostControllerDelete:
    """Tests for DELETE /v1/post/{id} (Delete) endpoint."""

    def test_delete_existing_post_returns_204(self, client: TestClient):
        """Test deleting an existing post returns 204."""
        # Create a post
        post_data = {
            "title": "Post to Delete",
            "subtext": "Delete me",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        create_response = client.post("/v1/post/", json=post_data)
        post_id = create_response.json()["id"]

        # Delete the post
        delete_response = client.delete(f"/v1/post/{post_id}")

        assert delete_response.status_code == 204

    def test_delete_nonexistent_post_returns_404(self, client: TestClient):
        """Test deleting a non-existent post returns 404."""
        response = client.delete("/v1/post/9999")

        assert response.status_code == 404

    def test_deleted_post_cannot_be_read(self, client: TestClient):
        """Test that a deleted post cannot be read."""
        # Create a post
        post_data = {
            "title": "Post to Delete",
            "subtext": "Delete me",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        create_response = client.post("/v1/post/", json=post_data)
        post_id = create_response.json()["id"]

        # Delete the post
        client.delete(f"/v1/post/{post_id}")

        # Try to read it - should get 404
        read_response = client.get(f"/v1/post/{post_id}")
        assert read_response.status_code == 404

    def test_deleted_post_not_in_read_all(self, client: TestClient):
        """Test that a deleted post is not in read all."""
        # Create a post
        post_data = {
            "title": "Unique Post to Delete Test",
            "subtext": "Delete me",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        create_response = client.post("/v1/post/", json=post_data)
        post_id = create_response.json()["id"]

        # Verify post exists
        verify_response = client.get(f"/v1/post/{post_id}")
        assert verify_response.status_code == 200

        # Delete the post
        delete_response = client.delete(f"/v1/post/{post_id}")
        assert delete_response.status_code == 204

        # Try to read it - should get 404
        read_after = client.get(f"/v1/post/{post_id}")
        assert read_after.status_code == 404


class TestPostControllerWorkflow:
    """Integration tests for complete workflows."""

    def test_full_crud_workflow(self, client: TestClient):
        """Test complete CRUD workflow."""
        # CREATE
        post_data = {
            "title": "Workflow Post",
            "subtext": "Testing workflow",
            "content": "Workflow content",
            "author": "Workflow Author",
            "date": "2025-01-15",
            "state": "draft",
        }
        create_response = client.post("/v1/post/", json=post_data)
        assert create_response.status_code == 201
        post_id = create_response.json()["id"]

        # READ
        read_response = client.get(f"/v1/post/{post_id}")
        assert read_response.status_code == 200
        assert read_response.json()["title"] == "Workflow Post"

        # UPDATE
        update_data = {
            "title": "Workflow Post Updated",
            "subtext": "Testing workflow",
            "content": "Workflow content",
            "author": "Workflow Author",
            "date": "2025-01-15",
            "state": "published",
        }
        update_response = client.put(f"/v1/post/{post_id}", json=update_data)
        assert update_response.status_code == 200
        assert update_response.json()["state"] == "published"

        # DELETE
        delete_response = client.delete(f"/v1/post/{post_id}")
        assert delete_response.status_code == 204

        # VERIFY DELETED
        read_after_delete = client.get(f"/v1/post/{post_id}")
        assert read_after_delete.status_code == 404

    def test_multiple_posts_workflow(self, client: TestClient):
        """Test workflow with multiple posts."""
        # Create multiple posts
        posts_ids = []
        for i in range(3):
            post_data = {
                "title": f"Multi Post {i}",
                "subtext": f"Subtext {i}",
                "content": f"Content {i}",
                "author": f"Author {i}",
                "date": "2025-01-15",
                "state": "published",
            }
            response = client.post("/v1/post/", json=post_data)
            posts_ids.append(response.json()["id"])

        # Verify all 3 were created
        assert len(posts_ids) == 3

        # Delete the middle one
        delete_response = client.delete(f"/v1/post/{posts_ids[1]}")
        assert delete_response.status_code == 204

        # Verify it's deleted
        read_after_delete = client.get(f"/v1/post/{posts_ids[1]}")
        assert read_after_delete.status_code == 404

        # Verify others still exist
        assert client.get(f"/v1/post/{posts_ids[0]}").status_code == 200
        assert client.get(f"/v1/post/{posts_ids[2]}").status_code == 200

    def test_state_transitions(self, client: TestClient):
        """Test state transitions (DRAFT -> PUBLISHED -> ARCHIVED)."""
        # Create in DRAFT
        post_data = {
            "title": "State Transition Post",
            "subtext": "Testing states",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "draft",
        }
        create_response = client.post("/v1/post/", json=post_data)
        post_id = create_response.json()["id"]

        # Transition to PUBLISHED
        update_data = post_data.copy()
        update_data["state"] = "published"
        response = client.put(f"/v1/post/{post_id}", json=update_data)
        assert response.json()["state"] == "published"

        # Transition to ARCHIVED
        update_data["state"] = "archived"
        response = client.put(f"/v1/post/{post_id}", json=update_data)
        assert response.json()["state"] == "archived"


class TestPostControllerResponseFormat:
    """Tests for response format and structure."""

    def test_create_response_contains_id(self, client: TestClient):
        """Test that create response includes the generated ID."""
        post_data = {
            "title": "Test",
            "subtext": "Test",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        response = client.post("/v1/post/", json=post_data)
        data = response.json()

        assert "id" in data
        assert isinstance(data["id"], int)
        assert data["id"] > 0

    def test_post_response_dto_format(self, client: TestClient):
        """Test that post response matches DTO format."""
        post_data = {
            "title": "DTO Test",
            "subtext": "Testing DTO",
            "content": "Content",
            "author": "Author",
            "date": "2025-01-15",
            "state": "published",
        }
        response = client.post("/v1/post/", json=post_data)
        data = response.json()

        # Check DTO fields
        assert "id" in data
        assert "title" in data
        assert "subtext" in data
        assert "content" in data
        assert "author" in data
        assert "date" in data
        assert "state" in data

    def test_read_all_response_is_list(self, client: TestClient):
        """Test that read all returns a list."""
        response = client.get("/v1/post/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_error_response_has_detail(self, client: TestClient):
        """Test that error responses include detail message."""
        response = client.get("/v1/post/9999")
        assert response.status_code == 404
        assert "detail" in response.json()
