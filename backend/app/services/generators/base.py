from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional
import uuid
import logging

from app.services.llm_service import LLMService, LLMMessage, LLMResponse

logger = logging.getLogger(__name__)


@dataclass
class GenerationRequest:
    user_id: uuid.UUID
    generator_type: str
    llm_provider: str = "openai"
    llm_model: Optional[str] = None
    target_keywords: list[str] = field(default_factory=list)
    title: Optional[str] = None
    word_count_min: int = 800
    word_count_max: int = 1500
    tone: str = "professional"
    point_of_view: str = "third_person"
    generate_ai_title: bool = True
    slug_source: str = "keyword"
    use_realtime_data: bool = False
    include_images: bool = True
    image_credit: bool = True
    include_video: bool = False
    custom_prompt: Optional[str] = None
    article_format: str = "long"
    num_subheadings: int = 5
    num_faqs: int = 3
    pros_cons: bool = False
    alternatives: bool = False
    relevant_details: Optional[str] = None
    outline: Optional[dict] = None
    subject_name: Optional[str] = None
    profession: Optional[str] = None
    chronological_timeline: bool = False


@dataclass
class GenerationResult:
    article_id: Optional[uuid.UUID] = None
    title: str = ""
    content: str = ""
    slug: str = ""
    excerpt: Optional[str] = None
    word_count: int = 0
    reading_time: int = 0
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    featured_image_url: Optional[str] = None
    outline: Optional[dict] = None
    tokens_used: int = 0
    processing_time: float = 0.0
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class ContentGenerator(ABC):
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    @abstractmethod
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        pass

    def validate_input(self, request: GenerationRequest) -> Optional[str]:
        if not request.user_id:
            return "user_id is required"
        if not request.target_keywords and not request.custom_prompt:
            return "Either target_keywords or custom_prompt is required"
        if request.word_count_min > request.word_count_max:
            return "word_count_min cannot be greater than word_count_max"
        if request.num_subheadings < 1:
            return "num_subheadings must be at least 1"
        if request.num_faqs < 0:
            return "num_faqs cannot be negative"
        return None

    async def call_llm(
        self,
        messages: list[LLMMessage],
        system: str = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> LLMResponse:
        logger.debug(f"Calling LLM with {len(messages)} messages")
        return await self.llm_service.generate(
            messages=messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def build_system_prompt(self, request: GenerationRequest) -> str:
        base_prompt = f"""You are an expert SEO content writer specializing in {request.tone} writing.
You create well-structured, SEO-optimized articles that are engaging and informative."""
        if request.use_realtime_data:
            base_prompt += "\nYou have access to real-time data and should incorporate current information."
        return base_prompt

    def calculate_reading_time(self, word_count: int) -> int:
        return max(1, word_count // 200)

    def generate_slug(self, title: str) -> str:
        import re
        slug = title.lower()
        slug = re.sub(r'[^a-z0-9\s-]', '', slug)
        slug = re.sub(r'[\s-]+', '-', slug)
        slug = slug.strip('-')
        return slug

    def count_words(self, text: str) -> int:
        if not text:
            return 0
        return len(text.split())

    def generate_meta_description(self, content: str) -> str:
        import re

        content = re.sub(r'\n+', ' ', content)
        content = re.sub(r'\s+', ' ', content)

        sentences = re.split(r'(?<=[.!?])\s+', content)

        meta = ""
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            if len(meta) + len(sentence) + 1 <= 160:
                meta = sentence
            else:
                break

        if not meta:
            meta = content[:157].rsplit(' ', 1)[0] + "..."

        if not meta.endswith(('.', '!', '?')):
            meta = meta.rstrip(',;:') + "."

        return meta.strip()

    def parse_title(self, content: str) -> str:
        title = content.strip()
        title = title.strip('"').strip("'")
        lines = title.split('\n')
        return lines[0].strip()