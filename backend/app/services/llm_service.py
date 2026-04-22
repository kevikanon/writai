import httpx
import json
from typing import Optional, AsyncIterator
from dataclasses import dataclass

from app.schemas.user_api_key import LLMProvider


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
            LLMProvider.AMAZON: "anthropic.claude-3-5-sonnet-20241022-v1:0",
        }
        return defaults.get(provider, "gpt-4o")

    async def generate(
        self,
        messages: list[LLMMessage],
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: str = None,
    ) -> LLMResponse:
        if self.provider == LLMProvider.OPENAI:
            return await self._generate_openai(messages, temperature, max_tokens, system)
        elif self.provider == LLMProvider.ANTHROPIC:
            return await self._generate_anthropic(messages, temperature, max_tokens, system)
        elif self.provider == LLMProvider.GOOGLE:
            return await self._generate_google(messages, temperature, max_tokens, system)
        elif self.provider == LLMProvider.MISTRAL:
            return await self._generate_mistral(messages, temperature, max_tokens, system)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

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

        async with httpx.AsyncClient() as client:
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
                timeout=120.0,
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

        async with httpx.AsyncClient() as client:
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
                timeout=120.0,
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

        async with httpx.AsyncClient() as client:
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
                timeout=120.0,
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

        async with httpx.AsyncClient() as client:
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
                timeout=120.0,
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

    return LLMService(api_key_record.encrypted_key, provider, model)