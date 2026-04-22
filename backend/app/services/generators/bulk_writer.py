from app.services.generators.base import ContentGenerator, GenerationRequest, GenerationResult
from app.services.llm_service import LLMMessage
import time
import uuid


class BulkWriter(ContentGenerator):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        start_time = time.time()
        result = GenerationResult()

        validation_error = self.validate_input(request)
        if validation_error:
            result.errors.append(validation_error)
            result.processing_time = time.time() - start_time
            return result

        if len(request.target_keywords) < 1:
            result.errors.append("At least one keyword is required")
            result.processing_time = time.time() - start_time
            return result

        try:
            keywords = request.target_keywords
            num_articles = min(len(keywords), 50)

            if request.title:
                result.title = request.title
            else:
                keyword = keywords[0]
                title_messages = [
                    LLMMessage(
                        role="user",
                        content=self._build_title_prompt(keyword),
                    )
                ]
                title_response = await self.call_llm(
                    messages=title_messages,
                    system="You are an expert SEO title writer.",
                    temperature=0.8,
                    max_tokens=100,
                )
                result.title = self.parse_title(title_response.content)

            result.slug = self.generate_slug(result.title)

            keywords_prompt = self._build_keywords_prompt(keywords[:num_articles])
            content_messages = [
                LLMMessage(
                    role="user",
                    content=keywords_prompt,
                )
            ]

            content_response = await self.call_llm(
                messages=content_messages,
                system=self.build_system_prompt(request),
                temperature=0.7,
                max_tokens=4096,
            )

            result.content = content_response.content
            result.word_count = self.count_words(result.content)
            result.reading_time = self.calculate_reading_time(result.word_count)
            result.meta_title = result.title[:60] if len(result.title) > 60 else result.title
            result.meta_description = self.generate_meta_description(result.content)
            result.tokens_used = content_response.usage.get("total_tokens", 0)
            result.processing_time = time.time() - start_time

        except Exception as e:
            result.errors.append(str(e))
            result.processing_time = time.time() - start_time

        return result

    def _build_title_prompt(self, keyword: str) -> str:
        return f"""Generate an SEO-optimized article title for the keyword "{keyword}".
Requirements:
- Include the main keyword naturally
- Be compelling and click-worthy
- 50-60 characters ideal
- Use power words to increase CTR
Return only the title, no additional text."""

    def _build_keywords_prompt(self, keywords: list[str]) -> str:
        keywords_str = ", ".join(keywords)
        return f"""Write a comprehensive SEO article covering multiple related keywords.
Target keywords: {keywords_str}
Word count: 800-1500 words
Tone: professional

Structure requirements:
1. Compelling introduction with hook that addresses multiple search intents
2. H2 sections covering each keyword topic with subheadings containing keywords naturally
3. Detailed, valuable content in each section
4. FAQ section addressing common questions

Additional requirements:
- Use short paragraphs (2-3 sentences each)
- Include transition sentences between sections
- Write for both readers and search engines
- Naturally incorporate all keywords throughout the content

Return the complete article in Markdown format."""