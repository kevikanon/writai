import hashlib
import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.exc import IntegrityError

from app.db.database import get_db
from app.db.models import UserAPIKey
from app.schemas.user_api_key import (
    UserAPIKeyResponse,
    UserAPIKeyCreate,
    UserAPIKeyUpdate,
    UserAPIKeyProviderResponse,
    UserAPIKeyValidateRequest,
    UserAPIKeyValidateResponse,
)
from app.api.v1.users import CurrentUser
from app.services.api_key_validator import api_key_validator
from app.core.encryption import encrypt_api_key

router = APIRouter()


def hash_api_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()


@router.get("", response_model=list[UserAPIKeyResponse])
async def list_api_keys(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserAPIKey).where(UserAPIKey.user_id == current_user.id)
    )
    return result.scalars().all()


@router.get("/providers", response_model=list[UserAPIKeyProviderResponse])
async def list_provider_status(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserAPIKey).where(UserAPIKey.user_id == current_user.id)
    )
    keys = result.scalars().all()

    providers = {}
    for key in keys:
        providers[key.provider] = {
            "has_key": True,
            "is_active": key.is_active,
        }

    all_providers = ["openai", "anthropic", "google", "mistral", "amazon"]
    response = []
    for provider in all_providers:
        if provider in providers:
            response.append(
                UserAPIKeyProviderResponse(
                    provider=provider,
                    has_key=providers[provider]["has_key"],
                    is_active=providers[provider]["is_active"],
                )
            )
        else:
            response.append(
                UserAPIKeyProviderResponse(
                    provider=provider,
                    has_key=False,
                    is_active=False,
                )
            )

    return response


@router.post("/validate", response_model=UserAPIKeyValidateResponse)
async def validate_api_key(
    request: UserAPIKeyValidateRequest,
):
    result = await api_key_validator.validate(request.provider, request.api_key)
    return UserAPIKeyValidateResponse(**result)


@router.post("", response_model=UserAPIKeyResponse, status_code=status.HTTP_201_CREATED)
async def create_api_key(
    request: UserAPIKeyCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    encrypted = encrypt_api_key(request.api_key)
    api_key = UserAPIKey(
        user_id=current_user.id,
        provider=request.provider.value,
        key_hash=hash_api_key(request.api_key),
        encrypted_key=encrypted,
    )
    db.add(api_key)
    
    try:
        await db.commit()
        await db.refresh(api_key)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"API key for {request.provider.value} already exists. Use PATCH to update.",
        )
    
    return api_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_key(
    key_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserAPIKey).where(
            and_(
                UserAPIKey.id == key_id,
                UserAPIKey.user_id == current_user.id,
            )
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    await db.delete(api_key)
    await db.commit()
    return None


@router.patch("/{key_id}", response_model=UserAPIKeyResponse)
async def update_api_key(
    key_id: uuid.UUID,
    request: UserAPIKeyUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserAPIKey).where(
            and_(
                UserAPIKey.id == key_id,
                UserAPIKey.user_id == current_user.id,
            )
        )
    )
    api_key = result.scalar_one_or_none()

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API key not found",
        )

    if request.api_key is not None:
        api_key.key_hash = hash_api_key(request.api_key)
        api_key.encrypted_key = encrypt_api_key(request.api_key)
    if request.is_active is not None:
        api_key.is_active = request.is_active

    await db.commit()
    await db.refresh(api_key)
    return api_key
