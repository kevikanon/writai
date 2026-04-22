from app.services.generators.base import ContentGenerator, GenerationRequest, GenerationResult
import time


class ManualWriter(ContentGenerator):
    async def generate(self, request: GenerationRequest) -> GenerationResult:
        start_time = time.time()
        result = GenerationResult()

        try:
            if not request.custom_prompt and not request.target_keywords:
                result.errors.append("Content is required for ManualWriter")
                result.processing_time = time.time() - start_time
                return result

            content_input = request.custom_prompt or request.target_keywords[0]

            result.title = request.title or "Untitled Article"
            result.slug = self.generate_slug(result.title)
            result.content = content_input
            result.word_count = self.count_words(content_input)
            result.reading_time = self.calculate_reading_time(result.word_count)
            result.meta_title = result.title[:60] if len(result.title) > 60 else result.title
            result.meta_description = self.generate_meta_description(content_input)
            result.processing_time = time.time() - start_time

        except Exception as e:
            result.errors.append(str(e))
            result.processing_time = time.time() - start_time

        return result