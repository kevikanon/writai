from app.services.generators.base import ContentGenerator, GenerationRequest, GenerationResult
from app.services.llm_service import LLMMessage
import time
import json


class OutlineToArticle(ContentGenerator):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        start_time = time.time()
        result = GenerationResult()

        validation_error = self.validate_input(request)
        if validation_error:
            result.errors.append(validation_error)
            result.processing_time = time.time() - start_time
            return result

        if not request.outline:
            result.errors.append("outline is required for OutlineToArticle")
            result.processing_time = time.time() - start_time
            return result

        try:
            keyword = request.target_keywords[0] if request.target_keywords else "the topic"

            if request.title:
                result.title = request.title
            else:
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

            content_messages = [
                LLMMessage(
                    role="user",
                    content=self._build_content_prompt(request),
                )
            ]

            content_response = await self.call_llm(
                messages=content_messages,
                system=self.build_system_prompt(request),
                temperature=0.7,
                max_tokens=self.calculate_max_tokens(request.word_count_max),
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

    def _build_content_prompt(self, request: GenerationRequest) -> str:
        keyword = request.target_keywords[0] if request.target_keywords else "the topic"
        keywords_str = ", ".join(request.target_keywords)

        outline_json = json.dumps(request.outline)

        prompt = f"""Write a comprehensive SEO article based on the provided outline.
Keyword: {keyword}
Target keywords: {keywords_str}
Word count: {request.word_count_min}-{request.word_count_max} words
Tone: {request.tone}
Point of view: {request.point_of_view}

Outline structure:
{outline_json}

Structure requirements:
1. Compelling introduction with hook
2. Use the outline sections as H2 headings exactly as provided
3. Expand each section with detailed, valuable content
4. Include relevant subheadings from outline
5. FAQ section with {request.num_faqs}+ questions (if not in outline)
6. Conclusion with call-to-action

Additional requirements:
- Short paragraphs (2-3 sentences each)
- Use transition sentences between sections
- Naturally incorporate keywords
- Write for both readers and search engines

Return the complete article in Markdown format."""

        if request.custom_prompt:
            prompt += f"\n\nAdditional instructions: {request.custom_prompt}"

        return prompt