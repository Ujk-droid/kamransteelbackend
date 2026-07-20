from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models.blog_post import PostStatus


class BlogPostImageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    image_url: str
    created_at: datetime


class BlogPostCreate(BaseModel):
    title: str
    slug: Optional[str] = None
    content: str
    meta_description: str = Field(max_length=300)
    keywords: Optional[str] = None
    status: PostStatus = PostStatus.DRAFT


class BlogPostUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    meta_description: Optional[str] = Field(default=None, max_length=300)
    keywords: Optional[str] = None
    status: Optional[PostStatus] = None


class BlogPostSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    slug: str
    meta_description: str
    keywords: Optional[str] = None
    featured_image_url: Optional[str] = None
    status: PostStatus
    created_at: datetime
    reading_time_minutes: int


class BlogPostRead(BlogPostSummary):
    content: str
    images: List[BlogPostImageRead] = []


class GenerateBlogImageRequest(BaseModel):
    prompt: str
