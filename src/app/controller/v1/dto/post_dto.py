from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from app.data.v1.model.post import PostState


class PostDto(BaseModel):
    """Post Data Transfer Object."""
    model_config = ConfigDict(from_attributes=True)

    id: int | None = None
    title: str = Field(..., min_length=1, max_length=128)
    subtext: str = Field(default="", max_length=256)
    content: str = Field(default="")
    author: str = Field(..., min_length=1, max_length=128)
    date: date
    state: PostState = PostState.DRAFT
