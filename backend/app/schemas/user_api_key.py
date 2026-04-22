import uuid
from datetime import datetime
from typing import Optional
from enum import Enum

from pydantic import BaseModel, ConfigDict


class LLMProvider(str, Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    MISTRAL = "mistral"
    AMAZON = "amazon"


class UserAPIKeyResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    provider: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UserAPIKeyCreate(BaseModel):
    provider: LLMProvider
    api_key: str


class UserAPIKeyUpdate(BaseModel):
    api_key: Optional[str] = None
    is_active: Optional[bool] = None


class UserAPIKeyProviderResponse(BaseModel):
    provider: str
    has_key: bool
    is_active: bool


class UserAPIKeyValidateRequest(BaseModel):
    provider: LLMProvider
    api_key: str


class UserAPIKeyValidateResponse(BaseModel):
    valid: bool
    provider: str
    error: Optional[str] = None
