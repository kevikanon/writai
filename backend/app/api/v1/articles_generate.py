import uuid
import logging
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import httpx
import markdown

from app.db.database import get_db
from app.db.models import Article, ArticleVersion, User
from app.schemas.article import ArticleResponse, ArticleGenerateRequest
from app.services.generators import GenerationRequest, GeneratorType, get_generator
from app.services.llm_service import get_llm_service
from app.api.v1.users import CurrentUser

router = APIRouter()
logger = logging.getLogger(__name__)


def convert_markdown_to_html(content: str) -> str:
    import re
    content = content.strip()
    content = re.sub(r'^```markdown\n?', '', content)
    content = re.sub(r'\n?```$', '', content)
    content = content.strip()
    if not content:
        return content
    return markdown.markdown(content)


@router.post("/{article_id}/generate", response_model=ArticleResponse)
async def generate_article(
    article_id: uuid.UUID,
    request: ArticleGenerateRequest,
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

    if article.status == "published":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot regenerate a published article",
        )

    if not request.target_keywords and not article.target_keyword and request.generator_type != GeneratorType.MANUAL:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one target keyword is required",
        )

    try:
        llm_service = await get_llm_service(db, current_user.id, request.provider, request.model)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    generator = get_generator(request.generator_type, llm_service)

    keywords = [request.target_keywords] if request.target_keywords else []
    if article.target_keyword and article.target_keyword not in keywords:
        keywords.insert(0, article.target_keyword)

    gen_request = GenerationRequest(
        user_id=current_user.id,
        generator_type=request.generator_type,
        llm_provider=request.provider.value,
        llm_model=request.model,
        target_keywords=keywords,
        title=article.title if article.title and article.title != "Untitled" else None,
        word_count_min=request.word_count_min,
        word_count_max=request.word_count_max,
        tone=request.tone,
        num_subheadings=request.num_subheadings,
        num_faqs=request.num_faqs,
        pros_cons=request.pros_cons,
        alternatives=request.alternatives,
        custom_prompt=request.custom_prompt,
        outline=request.outline,
        subject_name=request.subject_name,
        profession=request.profession,
        chronological_timeline=request.chronological_timeline,
        max_keywords=request.max_keywords,
    )

    try:
        result = await generator.generate(gen_request)
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

    try:
        if article.content:
            version = ArticleVersion(
                article_id=article.id,
                title=article.title,
                content=article.content,
                word_count=article.word_count,
            )
            db.add(version)

        article.title = result.title or article.title
        article.content = convert_markdown_to_html(result.content)
        article.slug = result.slug or article.slug
        article.word_count = result.word_count
        article.reading_time = result.reading_time
        article.meta_title = result.meta_title
        article.meta_description = result.meta_description
        article.featured_image_url = result.featured_image_url
        article.status = "generated"
        article.article_type = request.generator_type.value

        if result.warnings:
            logger.info(f"Generation completed with warnings for article {article_id}: {result.warnings}")

        await db.commit()
        await db.refresh(article)
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save article {article_id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save generated article",
        )

    return article