import uuid
import logging
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import httpx

from app.db.database import get_db
from app.db.models import Article, ArticleVersion, User
from app.schemas.article import ArticleResponse
from app.schemas.user_api_key import LLMProvider
from app.services.generators import MagicWriter, GenerationRequest
from app.services.llm_service import get_llm_service
from app.api.v1.users import CurrentUser

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/{article_id}/generate", response_model=ArticleResponse)
async def generate_article(
    article_id: uuid.UUID,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    provider: LLMProvider = LLMProvider.OPENAI,
    model: Optional[str] = None,
    target_keywords: str = None,
    word_count_min: int = 800,
    word_count_max: int = 1500,
    tone: str = "professional",
    num_subheadings: int = 5,
    num_faqs: int = 3,
    pros_cons: bool = False,
    alternatives: bool = False,
    custom_prompt: str = None,
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

    if article.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot regenerate a published article",
        )

    if not target_keywords and not article.target_keyword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one target keyword is required",
        )

    try:
        llm_service = await get_llm_service(db, current_user.id, provider, model)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    generator = MagicWriter(llm_service)

    keywords = [target_keywords] if target_keywords else []
    if article.target_keyword and article.target_keyword not in keywords:
        keywords.insert(0, article.target_keyword)

    request = GenerationRequest(
        user_id=current_user.id,
        generator_type="magic",
        llm_provider=provider.value,
        llm_model=model,
        target_keywords=keywords,
        title=article.title if article.title and article.title != "Untitled" else None,
        word_count_min=word_count_min,
        word_count_max=word_count_max,
        tone=tone,
        num_subheadings=num_subheadings,
        num_faqs=num_faqs,
        pros_cons=pros_cons,
        alternatives=alternatives,
        custom_prompt=custom_prompt,
    )

    try:
        result = await generator.generate(request)
    except httpx.TimeoutException:
        logger.error(f"Generation timed out for article {article_id}")
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Generation timed out. Please try again with a smaller word count.",
        )
    except httpx.HTTPStatusError as e:
        logger.error(f"LLM API error for article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"LLM API error: {e.response.status_code}",
        )
    except Exception as e:
        logger.error(f"Generation failed for article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {str(e)}",
        )

    if result.errors:
        logger.warning(f"Generation completed with warnings for article {article_id}: {result.errors}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Generation failed: {result.errors[0]}",
        )

    if article.content:
        version = ArticleVersion(
            article_id=article.id,
            title=article.title,
            content=article.content,
            word_count=article.word_count,
        )
        db.add(version)

    article.title = result.title or article.title
    article.content = result.content
    article.slug = result.slug or article.slug
    article.word_count = result.word_count
    article.reading_time = result.reading_time
    article.meta_title = result.meta_title
    article.meta_description = result.meta_description
    article.featured_image_url = result.featured_image_url
    article.status = "generated"
    article.article_type = "magic"

    if result.warnings:
        logger.info(f"Generation completed with warnings for article {article_id}: {result.warnings}")

    await db.commit()
    await db.refresh(article)

    return article