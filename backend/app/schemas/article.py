import uuid
from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict, HttpUrl, field_validator, model_validator

from app.schemas.user_api_key import LLMProvider
from app.services.generators.base import GeneratorType


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

    @field_validator('meta_title')
    @classmethod
    def validate_meta_title(cls, v: str) -> str:
        if v and len(v) > 60:
            raise ValueError('must be 60 characters or less for SEO')
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


class ArticleGenerateRequest(BaseModel):
    provider: LLMProvider = LLMProvider.OPENAI
    model: Optional[str] = None
    generator_type: GeneratorType = GeneratorType.MAGIC
    target_keywords: Optional[str] = None
    word_count_min: int = 800
    word_count_max: int = 1500
    tone: str = "professional"
    num_subheadings: int = 5
    num_faqs: int = 3
    pros_cons: bool = False
    alternatives: bool = False
    custom_prompt: Optional[str] = None
    outline: Optional[dict] = None
    subject_name: Optional[str] = None
    profession: Optional[str] = None
    chronological_timeline: bool = False
    max_keywords: int = 50

    @field_validator('outline')
    @classmethod
    def validate_outline(cls, v: Optional[dict]) -> Optional[dict]:
        if v is None:
            return v
        if not isinstance(v, dict):
            raise ValueError('outline must be a dictionary')
        if 'sections' in v and not isinstance(v['sections'], list):
            raise ValueError('outline.sections must be a list')
        return v

    @field_validator('word_count_min', 'word_count_max')
    @classmethod
    def validate_word_count(cls, v: int) -> int:
        if v < 100:
            raise ValueError('must be at least 100')
        if v > 10000:
            raise ValueError('must not exceed 10000')
        return v

    @field_validator('tone')
    @classmethod
    def validate_tone(cls, v: str) -> str:
        valid_tones = ['professional', 'casual', 'formal', 'friendly', 'authoritative', 'humorous']
        if v not in valid_tones:
            raise ValueError(f'must be one of: {", ".join(valid_tones)}')
        return v
