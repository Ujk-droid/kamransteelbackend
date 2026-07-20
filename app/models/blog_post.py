from datetime import datetime, timezone
from enum import Enum
from typing import List, Optional

from sqlalchemy import Column, DateTime, Text
from sqlalchemy import Enum as SAEnum
from sqlmodel import Field, Relationship, SQLModel


class PostStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"


class BlogPost(SQLModel, table=True):
    __tablename__ = "blog_posts"

    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    slug: str = Field(unique=True, index=True)
    content: str = Field(sa_column=Column(Text, nullable=False))
    meta_description: str = Field(max_length=300)
    keywords: Optional[str] = None

    featured_image_url: Optional[str] = None
    featured_image_public_id: Optional[str] = None

    status: PostStatus = Field(
        sa_column=Column(
            SAEnum(PostStatus, name="poststatus"),
            nullable=False,
            default=PostStatus.DRAFT,
        )
    )

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    images: List["BlogPostImage"] = Relationship(
        back_populates="blog_post",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )

    @property
    def reading_time_minutes(self) -> int:
        word_count = len(self.content.split())
        return max(1, round(word_count / 200))


class BlogPostImage(SQLModel, table=True):
    __tablename__ = "blog_post_images"

    id: Optional[int] = Field(default=None, primary_key=True)
    blog_post_id: int = Field(foreign_key="blog_posts.id")
    image_url: str
    public_id: str

    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )

    blog_post: Optional[BlogPost] = Relationship(back_populates="images")
