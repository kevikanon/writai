from app.services.generators.base import ContentGenerator, GenerationRequest, GenerationResult
from app.services.llm_service import LLMMessage
import time


class ShortInfoWriter(ContentGenerator):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        start_time = time.time()
        result = GenerationResult()

        validation_error = self.validate_input(request)
        if validation_error:
            result.errors.append(validation_error)
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
                    max_tokens=60,
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
        return f"""Generate a concise SEO article title for "{keyword}".
Requirements:
- Include the main keyword
- Be compelling and clear
- 40-60 characters
Return only the title."""

    def _build_content_prompt(self, request: GenerationRequest) -> str:
        keyword = request.target_keywords[0] if request.target_keywords else "the topic"
        keywords_str = ", ".join(request.target_keywords) if request.target_keywords else ""

        prompt = f"""Write a concise SEO article about "{keyword}".
Target keywords: {keywords_str}
Word count: 300-500 words
Tone: {request.tone}

Structure:
1. Brief introduction (2-3 sentences)
2. 2-3 H2 sections with valuable content
3. Quick summary

Requirements:
- Short paragraphs
- Use the keyword naturally
- Be direct and informative

Return in Markdown format."""

        if request.custom_prompt:
            prompt += f"\n\nAdditional: {request.custom_prompt}"

        return prompt