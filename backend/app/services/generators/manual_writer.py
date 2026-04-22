from app.services.generators.base import ContentGenerator, GenerationRequest, GenerationResult
import time
import re


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
            result.meta_description = self._generate_meta_description(content_input)
            result.processing_time = time.time() - start_time

        except Exception as e:
            result.errors.append(str(e))
            result.processing_time = time.time() - start_time

        return result

    def _generate_meta_description(self, content: str) -> str:
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