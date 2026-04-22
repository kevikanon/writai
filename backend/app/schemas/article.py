import uuid
from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator, model_validator


class ArticleStatus(str, Enum):
    DRAFT = "draft"
    GENERATED = "generated"
    PUBLISHED = "published"


class ArticleType(str, Enum):
    MAGIC = "magic"
    BULK = "bulk"
    SHORT_INFO = "short_info"
    OUTLINE = "outline"
    AMAZON_REVIEW = "amazon_review"
    BIOGRAPHY = "biography"
    MANUAL = "manual"


class ArticleResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    slug: str
    content: Optional[str] = None
    excerpt: Optional[str] = None
    word_count: int
    reading_time: int
    status: ArticleStatus
    article_type: ArticleType
    target_keyword: Optional[str] = None
    secondary_keywords: Optional[list] = None
    tone: Optional[str] = None
    word_count_target: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    featured_image_url: Optional[str] = None
    source: str
    published_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('word_count', 'reading_time')
    @classmethod
    def validate_positive(cls, v: int) -> int:
        if v < 0:
            raise ValueError('must be non-negative')
        return v

    model_config = ConfigDict(from_attributes=True)


class ArticleCreate(BaseModel):
    title: str
    content: Optional[str] = None
    article_type: Optional[ArticleType] = ArticleType.MAGIC
    target_keyword: Optional[str] = None
    secondary_keywords: Optional[list] = None
    tone: Optional[str] = None
    word_count_target: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    featured_image_url: Optional[HttpUrl] = None

    @field_validator('title')
    @classmethod
    def validate_title(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError('title cannot be empty')
        return v


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    article_type: Optional[ArticleType] = None
    target_keyword: Optional[str] = None
    secondary_keywords: Optional[list] = None
    tone: Optional[str] = None
    word_count_target: Optional[int] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    featured_image_url: Optional[HttpUrl] = None
    status: Optional[ArticleStatus] = None


class ArticleVersionResponse(BaseModel):
    id: uuid.UUID
    article_id: uuid.UUID
    content: str
    title: str
    word_count: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ArticleListResponse(BaseModel):
    items: list[ArticleResponse]
    total: int
    page: int
    per_page: int
    total_pages: int
