"""
Demo script showcasing the generic CRUD implementation with PostController.

This script demonstrates:
- Creating posts
- Reading posts
- Updating posts
- Deleting posts
- Listing all posts
"""

from datetime import date

from sqlmodel import Session, SQLModel, create_engine

from app.controller.v1.dto.post_dto import PostDto
from app.data.v1.model.post import PostState
from app.data.v1.post_repository import PostRepository
from app.service.v1.post_service import PostService

# Create in-memory SQLite database
DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(DATABASE_URL, echo=False)

# Create tables
SQLModel.metadata.create_all(engine)


def demo_crud_operations():
    """Demonstrate CRUD operations using the generic implementation."""

    print("\n" + "=" * 70)
    print("🚀 Generic CRUD Implementation Demo")
    print("=" * 70)

    # Initialize repository and service
    session = Session(engine)
    repository = PostRepository(session)
    service = PostService(repository)

    # 1. CREATE - Create posts
    print("\n1️⃣  CREATE - Creating posts...")
    print("-" * 70)

    post1_dto = PostDto(
        title="Getting Started with FastAPI",
        subtext="Learn the basics of FastAPI framework",
        content="FastAPI is a modern, fast web framework for building APIs with Python...",
        author="Alice Johnson",
        date=date(2025, 1, 5),
        state=PostState.PUBLISHED,
    )

    post2_dto = PostDto(
        title="Advanced Python Patterns",
        subtext="Design patterns in Python",
        content="Understanding design patterns is crucial for writing scalable code...",
        author="Bob Smith",
        date=date(2025, 1, 10),
        state=PostState.DRAFT,
    )

    created_post1 = service.create(post1_dto)
    created_post2 = service.create(post2_dto)

    print(f"✅ Created: {created_post1.title} (ID: {created_post1.id})")
    print(f"✅ Created: {created_post2.title} (ID: {created_post2.id})")

    # 2. READ - Read single post
    print("\n2️⃣  READ - Reading a single post...")
    print("-" * 70)

    read_post = service.read(created_post1.id)
    if read_post:
        print(f"✅ Retrieved: {read_post.title}")
        print(f"   Author: {read_post.author}")
        print(f"   State: {read_post.state}")
        print(f"   Date: {read_post.date}")

    # 3. READ ALL - List all posts
    print("\n3️⃣  READ ALL - Listing all posts...")
    print("-" * 70)

    all_posts = service.read_all(skip=0, limit=10)
    print(f"✅ Total posts: {len(all_posts)}")
    for i, post in enumerate(all_posts, 1):
        print(f"   {i}. [{post.state}] {post.title} by {post.author}")

    # 4. UPDATE - Update a post
    print("\n4️⃣  UPDATE - Updating a post...")
    print("-" * 70)

    update_dto = PostDto(
        title="Advanced Python Patterns (Updated)",
        subtext="Design patterns in Python - Comprehensive Guide",
        content=(
            "Understanding design patterns is crucial for writing "
            "scalable, maintainable code..."
        ),
        author="Bob Smith",
        date=date(2025, 1, 10),
        state=PostState.PUBLISHED,  # Changed from DRAFT to PUBLISHED
    )

    updated_post = service.update(created_post2.id, update_dto)
    if updated_post:
        print(f"✅ Updated: {updated_post.title}")
        print(f"   New state: {updated_post.state}")

    # 5. Verify update
    print("\n5️⃣  VERIFY - Verifying the update...")
    print("-" * 70)

    verified_post = service.read(created_post2.id)
    if verified_post:
        print(f"✅ Verified: {verified_post.title}")
        print(f"   Current state: {verified_post.state}")
        print(f"   Content preview: {verified_post.content[:50]}...")

    # 6. DELETE - Delete a post
    print("\n6️⃣  DELETE - Deleting a post...")
    print("-" * 70)

    success = service.delete(created_post2.id)
    print(f"✅ Deleted: {created_post2.title} (Success: {success})")

    # 7. Verify deletion
    print("\n7️⃣  VERIFY - Verifying the deletion...")
    print("-" * 70)

    deleted_post = service.read(created_post2.id)
    if deleted_post is None:
        print(f"✅ Confirmed: Post with ID {created_post2.id} no longer exists")
    else:
        print("❌ Error: Post still exists")

    # 8. Final state
    print("\n8️⃣  FINAL STATE - Remaining posts...")
    print("-" * 70)

    final_posts = service.read_all()
    print(f"✅ Remaining posts: {len(final_posts)}")
    for i, post in enumerate(final_posts, 1):
        print(f"   {i}. {post.title} (ID: {post.id}, State: {post.state})")

    # Cleanup
    session.close()

    print("\n" + "=" * 70)
    print("✨ Demo completed successfully!")
    print("=" * 70 + "\n")


def main():
    """Main entry point for the demo."""
    demo_crud_operations()


if __name__ == "__main__":
    main()
