from app.services.generators.base import ContentGenerator, GenerationRequest, GenerationResult
from app.services.llm_service import LLMMessage
import time
import uuid


class MagicWriter(ContentGenerator):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        start_time = time.time()
        result = GenerationResult()

        try:
            keyword = request.target_keywords[0] if request.target_keywords else "general topic"
            
            if request.title:
                result.title = request.title
            else:
                title_messages = [
                    LLMMessage(
                        role="user",
                        content=self._build_title_prompt(request),
                    )
                ]
                title_response = await self.call_llm(
                    messages=title_messages,
                    system="You are an expert SEO title writer.",
                    temperature=0.8,
                    max_tokens=100,
                )
                result.title = self._parse_title(title_response.content)
            
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
                max_tokens=4096,
            )
            
            result.content = content_response.content
            result.word_count = self.count_words(result.content)
            result.reading_time = self.calculate_reading_time(result.word_count)
            result.meta_title = result.title[:60] if len(result.title) > 60 else result.title
            result.meta_description = self._generate_meta_description(result.content)
            result.tokens_used = content_response.usage.get("total_tokens", 0)
            result.processing_time = time.time() - start_time

        except Exception as e:
            result.errors.append(str(e))
            result.processing_time = time.time() - start_time

        return result

    def _build_title_prompt(self, request: GenerationRequest) -> str:
        keyword = request.target_keywords[0] if request.target_keywords else "the topic"
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
        
        prompt = f"""Write a comprehensive SEO article about "{keyword}".
Target keywords: {keywords_str}
Word count: {request.word_count_min}-{request.word_count_max} words
Tone: {request.tone}
Point of view: {request.point_of_view}

Structure requirements:
1. Compelling introduction with hook
2. At least {request.num_subheadings} H2 sections with subheadings containing keywords
3. Detailed, valuable content in each section
4. FAQ section with {request.num_faqs}+ common questions and answers
"""

        if request.pros_cons:
            prompt += "5. Pros and Cons section\n"
        if request.alternatives:
            prompt += "6. Alternatives/Comparisons section\n"
        
        prompt += f"""
7. Conclusion with call-to-action

Additional requirements:
- Use short paragraphs (2-3 sentences each)
- Include transition sentences between sections
- Naturally incorporate secondary keywords
- Write for both readers and search engines
- Add at least one table or list where relevant

Return the complete article in Markdown format."""

        if request.custom_prompt:
            prompt += f"\n\nAdditional instructions: {request.custom_prompt}"

        return prompt

    def _parse_title(self, content: str) -> str:
        title = content.strip()
        title = title.strip('"').strip("'")
        lines = title.split('\n')
        return lines[0].strip()

    def _generate_meta_description(self, content: str) -> str:
        sentences = content.split('.')
        meta = ""
        for sentence in sentences[:3]:
            sentence = sentence.strip()
            if len(meta) + len(sentence) + 1 <= 160:
                meta += sentence + ". "
            else:
                break
        return meta.strip()