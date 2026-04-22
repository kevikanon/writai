import uuid
from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict


class PublishingPlatform(str, Enum):
    WORDPRESS = "wordpress"
    BLOGGER = "blogger"
    SHOPIFY = "shopify"
    WEBHOOK = "webhook"


class PublishingConfigResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    platform: str
    name: str
    site_url: Optional[str] = None
    category_id: Optional[str] = None
    is_default: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class PublishingConfigCreate(BaseModel):
    platform: PublishingPlatform
    name: str
    site_url: Optional[str] = None
    category_id: Optional[str] = None
    is_default: bool = False
    credentials: dict


class PublishingConfigUpdate(BaseModel):
    name: Optional[str] = None
    site_url: Optional[str] = None
    category_id: Optional[str] = None
    is_default: Optional[bool] = None
    is_active: Optional[bool] = None
    credentials: Optional[dict] = None