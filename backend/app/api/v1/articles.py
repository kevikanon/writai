import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.db.database import get_db
from app.db.models import Article, ArticleVersion, User
from app.schemas.article import (
    ArticleResponse,
    ArticleCreate,
    ArticleUpdate,
    ArticleVersionResponse,
)
from app.api.v1.users import CurrentUser

router = APIRouter()


def generate_slug(title: str) -> str:
    import re
    slug = title.lower()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    slug = slug.strip('-')
    return slug


def calculate_reading_time(word_count: int) -> int:
    return max(1, word_count // 200)


def count_words(text: str) -> int:
    if not text:
        return 0
    return len(text.split())


@router.get("", response_model=list[ArticleResponse])
async def list_articles(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    status_filter: str = None,
    article_type: str = None,
    search: str = None,
    page: int = 1,
    per_page: int = 10,
):
    query = select(Article).where(Article.user_id == current_user.id)

    if status_filter:
        query = query.where(Article.status == status_filter)
    if article_type:
        query = query.where(Article.article_type == article_type)
    if search:
        query = query.where(Article.title.ilike(f"%{search}%"))

    query = query.order_by(Article.created_at.desc())
    query = query.offset((page - 1) * per_page).limit(per_page)

    result = await db.execute(query)
    return result.scalars().all()


@router.post("", response_model=ArticleResponse, status_code=status.HTTP_201_CREATED)
async def create_article(
    request: ArticleCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    slug = generate_slug(request.title)

    existing = await db.execute(
        select(Article).where(
            Article.user_id == current_user.id,
            Article.slug == slug
        )
    )
    if existing.scalar_one_or_none():
        slug = f"{slug}-{uuid.uuid4().hex[:8]}"

    word_count = count_words(request.content) if request.content else 0
    reading_time = calculate_reading_time(word_count)

    article = Article(
        user_id=current_user.id,
        title=request.title,
        slug=slug,
        content=request.content,
        word_count=word_count,
        reading_time=reading_time,
        status="draft",
        article_type=request.article_type or "magic",
        target_keyword=request.target_keyword,
        secondary_keywords=request.secondary_keywords,
        tone=request.tone,
        word_count_target=request.word_count_target,
        meta_title=request.meta_title,
        meta_description=request.meta_description,
        featured_image_url=request.featured_image_url,
        source="editor",
    )
    db.add(article)
    await db.commit()
    await db.refresh(article)

    if request.content:
        version = ArticleVersion(
            article_id=article.id,
            title=article.title,
            content=article.content,
            word_count=article.word_count,
        )
        db.add(version)
        await db.commit()

    return article


@router.get("/{article_id}", response_model=ArticleResponse)
async def get_article(
    article_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Article).where(
            Article.id == article_id,
            Article.user_id == current_user.id,
        )
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )
    return article


@router.patch("/{article_id}", response_model=ArticleResponse)
async def update_article(
    article_id: uuid.UUID,
    request: ArticleUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Article).where(
            Article.id == article_id,
            Article.user_id == current_user.id,
        )
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    if request.title is not None:
        article.title = request.title
    if request.content is not None:
        article.content = request.content
        article.word_count = count_words(request.content)
        article.reading_time = calculate_reading_time(article.word_count)
    if request.target_keyword is not None:
        article.target_keyword = request.target_keyword
    if request.secondary_keywords is not None:
        article.secondary_keywords = request.secondary_keywords
    if request.tone is not None:
        article.tone = request.tone
    if request.word_count_target is not None:
        article.word_count_target = request.word_count_target
    if request.meta_title is not None:
        article.meta_title = request.meta_title
    if request.meta_description is not None:
        article.meta_description = request.meta_description
    if request.featured_image_url is not None:
        article.featured_image_url = request.featured_image_url
    if request.status is not None:
        article.status = request.status

    await db.commit()
    await db.refresh(article)
    return article


@router.delete("/{article_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_article(
    article_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Article).where(
            Article.id == article_id,
            Article.user_id == current_user.id,
        )
    )
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    await db.delete(article)
    await db.commit()
    return None


@router.get("/{article_id}/versions", response_model=list[ArticleVersionResponse])
async def list_article_versions(
    article_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    article_result = await db.execute(
        select(Article).where(
            Article.id == article_id,
            Article.user_id == current_user.id,
        )
    )
    article = article_result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    result = await db.execute(
        select(ArticleVersion)
        .where(ArticleVersion.article_id == article_id)
        .order_by(ArticleVersion.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{article_id}/versions", response_model=ArticleVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_article_version(
    article_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    article_result = await db.execute(
        select(Article).where(
            Article.id == article_id,
            Article.user_id == current_user.id,
        )
    )
    article = article_result.scalar_one_or_none()

    if not article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found",
        )

    version = ArticleVersion(
        article_id=article.id,
        title=article.title,
        content=article.content or "",
        word_count=article.word_count,
    )
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return version
