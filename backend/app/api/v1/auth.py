from datetime import datetime, timedelta
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import RegisterRequest, LoginRequest, AuthResponse
from app.core.security import verify_password, get_password_hash
from app.core.config import settings
from app.services.jwt import create_access_token

router = APIRouter()


@router.post("/register", response_model=AuthResponse)
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        name=request.name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(user.id)
    return AuthResponse(
        access_token=access_token,
        user_id=user.id,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    access_token = create_access_token(user.id)
    return AuthResponse(
        access_token=access_token,
        user_id=user.id,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

    user = User(
        email=request.email,
        password_hash=get_password_hash(request.password),
        name=request.name
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = f"dummy_token_{user.id}"
    return AuthResponse(
        access_token=access_token,
        user_id=user.id,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )


@router.post("/login", response_model=AuthResponse)
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == request.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )

    access_token = f"dummy_token_{user.id}"
    return AuthResponse(
        access_token=access_token,
        user_id=user.id,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )
