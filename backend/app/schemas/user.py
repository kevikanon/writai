import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr, ConfigDict


class UserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    name: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserSettingsResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    default_tone: Optional[str] = "professional"
    default_article_type: Optional[str] = "magic"
    auto_save: bool = True
    realtime_data_default: bool = False
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserSettingsUpdate(BaseModel):
    default_tone: Optional[str] = None
    default_article_type: Optional[str] = None
    auto_save: Optional[bool] = None
    realtime_data_default: Optional[bool] = None