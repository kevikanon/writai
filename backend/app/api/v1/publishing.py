import uuid
import json
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.db.database import get_db
from app.db.models import PublishingConfig
from app.schemas.publishing import (
    PublishingConfigResponse,
    PublishingConfigCreate,
    PublishingConfigUpdate,
)
from app.api.v1.users import CurrentUser

router = APIRouter()


@router.get("", response_model=list[PublishingConfigResponse])
async def list_publishing_configs(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PublishingConfig).where(PublishingConfig.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("", response_model=PublishingConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_publishing_config(
    request: PublishingConfigCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    if request.is_default:
        result = await db.execute(
            select(PublishingConfig).where(
                and_(
                    PublishingConfig.user_id == current_user.id,
                    PublishingConfig.is_default == True,
                )
            )
        )
        existing_default = result.scalars().all()
        for config in existing_default:
            config.is_default = False

    site_url_str = str(request.site_url) if request.site_url else None

    config = PublishingConfig(
        user_id=current_user.id,
        platform=request.platform.value,
        name=request.name,
        site_url=site_url_str,
        category_id=request.category_id,
        is_default=request.is_default,
        is_active=True,
        credentials=request.credentials,
    )
    db.add(config)
    await db.commit()
    await db.refresh(config)
    return config


@router.get("/{config_id}", response_model=PublishingConfigResponse)
async def get_publishing_config(
    config_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PublishingConfig).where(
            and_(
                PublishingConfig.id == config_id,
                PublishingConfig.user_id == current_user.id,
            )
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publishing config not found",
        )
    return config


@router.patch("/{config_id}", response_model=PublishingConfigResponse)
async def update_publishing_config(
    config_id: uuid.UUID,
    request: PublishingConfigUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PublishingConfig).where(
            and_(
                PublishingConfig.id == config_id,
                PublishingConfig.user_id == current_user.id,
            )
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publishing config not found",
        )

    if request.is_default and not config.is_default:
        result = await db.execute(
            select(PublishingConfig).where(
                and_(
                    PublishingConfig.user_id == current_user.id,
                    PublishingConfig.is_default == True,
                    PublishingConfig.id != config_id,
                )
            )
        )
        existing_defaults = result.scalars().all()
        for c in existing_defaults:
            c.is_default = False

    if request.name is not None:
        config.name = request.name
    if request.site_url is not None:
        config.site_url = str(request.site_url)
    if request.category_id is not None:
        config.category_id = request.category_id
    if request.is_default is not None:
        config.is_default = request.is_default
    if request.is_active is not None:
        config.is_active = request.is_active
    if request.credentials is not None:
        config.credentials = request.credentials

    await db.commit()
    await db.refresh(config)
    return config


@router.delete("/{config_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_publishing_config(
    config_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(PublishingConfig).where(
            and_(
                PublishingConfig.id == config_id,
                PublishingConfig.user_id == current_user.id,
            )
        )
    )
    config = result.scalar_one_or_none()

    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publishing config not found",
        )

    await db.delete(config)
    await db.commit()
    return None
