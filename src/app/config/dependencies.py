"""FastAPI dependencies."""

from sqlmodel import Session

from app.data.database import engine


def get_db_session() -> Session:
    """Get database session.

    Yields:
        Database session
    """
    with Session(engine) as session:
        yield session
