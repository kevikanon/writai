import httpx
import asyncio
import logging
from typing import Optional, Callable
from dataclasses import dataclass

from app.schemas.user_api_key import LLMProvider

logger = logging.getLogger(__name__)


_global_client: Optional[httpx.AsyncClient] = None
_client_lock = asyncio.Lock()


async def get_global_client() -> httpx.AsyncClient:
    global _global_client
    async with _client_lock:
        if _global_client is None or _global_client.is_closed:
            _global_client = httpx.AsyncClient(
                timeout=httpx.Timeout(120.0, connect=30.0),
                limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
            )
        return _global_client


async def close_global_client():
    global _global_client
    async with _client_lock:
        if _global_client and not _global_client.is_closed:
            await _global_client.aclose()
            _global_client = None


@dataclass
class LLMResponse:
    content: str
    usage: dict
    model: str
    provider: str


@dataclass
class LLMMessage:
    role: str
    content: str


class LLMService:
    def __init__(self, api_key: str, provider: LLMProvider, model: str = None):
        self.api_key = api_key
        self.provider = provider
        self.model = model or self._get_default_model(provider)

    def _get_default_model(self, provider: LLMProvider) -> str:
        defaults = {
            LLMProvider.OPENAI: "gpt-4o",
            LLMProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
            LLMProvider.GOOGLE: "gemini-1.5-pro",
            LLMProvider.MISTRAL: "mistral-large-latest",
        }
        return defaults.get(provider, "gpt-4o")

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: str = None,
        max_retries: int = 3,
    ) -> LLMResponse:
        if self.provider == LLMProvider.OPENAI:
            return await self._generate_with_retry(
                self._generate_openai, messages, temperature, max_tokens, system, max_retries
            )
        elif self.provider == LLMProvider.ANTHROPIC:
            return await self._generate_with_retry(
                self._generate_anthropic, messages, temperature, max_tokens, system, max_retries
            )
        elif self.provider == LLMProvider.GOOGLE:
            return await self._generate_with_retry(
                self._generate_google, messages, temperature, max_tokens, system, max_retries
            )
        elif self.provider == LLMProvider.MISTRAL:
            return await self._generate_with_retry(
                self._generate_mistral, messages, temperature, max_tokens, system, max_retries
            )
        elif self.provider == LLMProvider.AMAZON:
            raise ValueError("Amazon Bedrock provider requires AWS credentials setup")
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

    async def _generate_with_retry(
        self,
        method: Callable,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        system: str,
        max_retries: int = 3,
    ) -> LLMResponse:
        retryable_status_codes = {429, 500, 502, 503, 504}
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await method(messages, temperature, max_tokens, system)
            except httpx.TimeoutException as e:
                last_exception = e
                logger.warning(f"Attempt {attempt + 1}/{max_retries} timed out")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)
            except httpx.HTTPStatusError as e:
                last_exception = e
                if e.response.status_code in retryable_status_codes:
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed with {e.response.status_code}")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                else:
                    raise
            except ValueError as e:
                last_exception = e
                if "429" in str(e):
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} rate limited")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(2 ** attempt)
                else:
                    raise

        raise last_exception or ValueError("Max retries exceeded")

    async def _generate_openai(
        self,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        system: str,
    ) -> LLMResponse:
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend([{"role": m.role, "content": m.content} for m in messages])

        client = await get_global_client()
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

        if response.status_code != 200:
            raise ValueError(f"OpenAI API error: {response.status_code} - {response.text}")

        data = response.json()
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            usage=data.get("usage", {}),
            model=data.get("model", self.model),
            provider="openai",
        )

    async def _generate_anthropic(
        self,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        system: str,
    ) -> LLMResponse:
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "user", "content": f"<system>{system}</system>"})
        formatted_messages.extend([{"role": m.role, "content": m.content} for m in messages])

        client = await get_global_client()
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

        if response.status_code != 200:
            raise ValueError(f"Anthropic API error: {response.status_code} - {response.text}")

        data = response.json()
        return LLMResponse(
            content=data["content"][0]["text"],
            usage=data.get("usage", {}),
            model=data.get("model", self.model),
            provider="anthropic",
        )

    async def _generate_google(
        self,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        system: str,
    ) -> LLMResponse:
        formatted_contents = []
        if system:
            formatted_contents.append({"role": "user", "parts": [{"text": f"<system>{system}</system>"}]})
        for m in messages:
            role = "model" if m.role == "assistant" else "user"
            formatted_contents.append({"role": role, "parts": [{"text": m.content}]})

        client = await get_global_client()
        response = await client.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent",
            params={"key": self.api_key},
            headers={"Content-Type": "application/json"},
            json={
                "contents": formatted_contents,
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": max_tokens,
                },
            },
        )

        if response.status_code != 200:
            raise ValueError(f"Google API error: {response.status_code} - {response.text}")

        data = response.json()
        return LLMResponse(
            content=data["candidates"][0]["content"]["parts"][0]["text"],
            usage=data.get("usageMetadata", {}),
            model=self.model,
            provider="google",
        )

    async def _generate_mistral(
        self,
        messages: list[LLMMessage],
        temperature: float,
        max_tokens: int,
        system: str,
    ) -> LLMResponse:
        formatted_messages = []
        if system:
            formatted_messages.append({"role": "system", "content": system})
        formatted_messages.extend([{"role": m.role, "content": m.content} for m in messages])

        client = await get_global_client()
        response = await client.post(
            "https://api.mistral.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "messages": formatted_messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )

        if response.status_code != 200:
            raise ValueError(f"Mistral API error: {response.status_code} - {response.text}")

        data = response.json()
        return LLMResponse(
            content=data["choices"][0]["message"]["content"],
            usage=data.get("usage", {}),
            model=data.get("model", self.model),
            provider="mistral",
        )


async def get_llm_service(
    db,
    user_id,
    provider: LLMProvider,
    model: str = None,
) -> LLMService:
    from sqlalchemy import select, and_
    from app.db.models import UserAPIKey

    result = await db.execute(
        select(UserAPIKey).where(
            and_(
                UserAPIKey.user_id == user_id,
                UserAPIKey.provider == provider.value,
                UserAPIKey.is_active == True,
            )
        )
    )
    api_key_record = result.scalar_one_or_none()

    if not api_key_record:
        raise ValueError(f"No active API key found for {provider.value}")

    from app.core.encryption import decrypt_api_key
    decrypted_key = decrypt_api_key(api_key_record.encrypted_key)

    return LLMService(decrypted_key, provider, model)