from app.services.generators.base import ContentGenerator, GenerationRequest, GenerationResult
from app.services.llm_service import LLMMessage
import time


class BiographyWriter(ContentGenerator):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        start_time = time.time()
        result = GenerationResult()

        validation_error = self.validate_input(request)
        if validation_error:
            result.errors.append(validation_error)
            result.processing_time = time.time() - start_time
            return result

        try:
            subject_name = request.target_keywords[0] if request.target_keywords else request.custom_prompt
            if not subject_name:
                subject_name = "the subject"

            result.title = request.title or f"Biography of {subject_name}"
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
            result.meta_description = self.generate_meta_description(result.content)
            result.tokens_used = content_response.usage.get("total_tokens", 0)
            result.processing_time = time.time() - start_time

        except Exception as e:
            result.errors.append(str(e))
            result.processing_time = time.time() - start_time

        return result

    def _build_content_prompt(self, request: GenerationRequest) -> str:
        subject_name = request.target_keywords[0] if request.target_keywords else request.custom_prompt or "the subject"
        profession = request.relevant_details or "not specified"
        life_events = request.target_keywords[1:] if len(request.target_keywords) > 1 else []

        prompt = f"""Write a comprehensive biography article about {subject_name}.
Profession/Claim to fame: {profession}
Word count: {request.word_count_min}-{request.word_count_max} words
Tone: {request.tone}

{"Include the following key events: " + ", ".join(life_events) if life_events else ""}

{"Use chronological timeline format." if request.article_format == "timeline" else "Use standard biography structure."}

Structure requirements:
1. Introduction - Early life and background
2. Career highlights and major achievements
3. Personal life (if notable)
4. Legacy and impact
5. Conclusion

Requirements:
- Short paragraphs (2-3 sentences each)
- Include relevant dates and milestones
- Write in {"first person" if request.point_of_view == "first_person" else "third person"} voice
- Be factual and informative

Return in Markdown format."""

        if request.custom_prompt:
            prompt += f"\n\nAdditional: {request.custom_prompt}"

        return prompt