import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User
from app.schemas.user import UserResponse, UserUpdate
from app.services.jwt import verify_access_token

router = APIRouter()


async def get_current_user(
    token: str,
    db: AsyncSession = Depends(get_db)
) -> User:
    user_id = verify_access_token(token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    return user


@router.get("/me", response_model=UserResponse)
async def get_profile(
    db: AsyncSession = Depends(get_db),
    token: str = None
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Auth middleware not yet implemented")


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    request: UserUpdate,
    db: AsyncSession = Depends(get_db),
    token: str = None
):
    raise HTTPException(status_code=status.HTTP_501_NOT_IMPLEMENTED, detail="Auth middleware not yet implemented")