from datetime import date
from enum import Enum

from sqlmodel import Field, SQLModel


class PostState(str, Enum):
    """Post publication state."""
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"


class Post(SQLModel, table=True):
    """Post database model."""
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(default="Post Title", max_length=128)
    subtext: str = Field(default="", max_length=256)
    content: str = Field(default="")
    author: str = Field(max_length=128)
    date: date
    state: PostState = Field(default=PostState.DRAFT)
