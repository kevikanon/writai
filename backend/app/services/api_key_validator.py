import httpx
from typing import Optional


class APIKeyValidator:
    def __init__(self):
        self.providers = {
            "openai": self._validate_openai,
            "anthropic": self._validate_anthropic,
            "google": self._validate_google,
            "mistral": self._validate_mistral,
            "amazon": self._validate_amazon,
        }

    async def validate(self, provider: str, api_key: str) -> dict:
        if provider not in self.providers:
            return {"valid": False, "provider": provider, "error": f"Unknown provider: {provider}"}
        
        return await self.providers[provider](api_key)

    async def _validate_openai(self, api_key: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.openai.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return {"valid": True, "provider": "openai"}
                elif response.status_code == 401:
                    return {"valid": False, "provider": "openai", "error": "Invalid OpenAI API key"}
                else:
                    return {"valid": False, "provider": "openai", "error": f"OpenAI API error: {response.status_code}"}
        except Exception as e:
            return {"valid": False, "provider": "openai", "error": f"Failed to validate OpenAI key: {str(e)}"}

    async def _validate_anthropic(self, api_key: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.anthropic.com/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                    },
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return {"valid": True, "provider": "anthropic"}
                elif response.status_code == 401:
                    return {"valid": False, "provider": "anthropic", "error": "Invalid Anthropic API key"}
                else:
                    return {"valid": False, "provider": "anthropic", "error": f"Anthropic API error: {response.status_code}"}
        except Exception as e:
            return {"valid": False, "provider": "anthropic", "error": f"Failed to validate Anthropic key: {str(e)}"}

    async def _validate_google(self, api_key: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://generativelanguage.googleapis.com/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return {"valid": True, "provider": "google"}
                elif response.status_code == 401:
                    return {"valid": False, "provider": "google", "error": "Invalid Google API key"}
                else:
                    return {"valid": False, "provider": "google", "error": f"Google API error: {response.status_code}"}
        except Exception as e:
            return {"valid": False, "provider": "google", "error": f"Failed to validate Google key: {str(e)}"}

    async def _validate_mistral(self, api_key: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.mistral.ai/v1/models",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    return {"valid": True, "provider": "mistral"}
                elif response.status_code == 401:
                    return {"valid": False, "provider": "mistral", "error": "Invalid Mistral API key"}
                else:
                    return {"valid": False, "provider": "mistral", "error": f"Mistral API error: {response.status_code}"}
        except Exception as e:
            return {"valid": False, "provider": "mistral", "error": f"Failed to validate Mistral key: {str(e)}"}

    async def _validate_amazon(self, api_key: str) -> dict:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.amazon.com/",
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0,
                )
                if response.status_code in (200, 204):
                    return {"valid": True, "provider": "amazon"}
                elif response.status_code == 401:
                    return {"valid": False, "provider": "amazon", "error": "Invalid Amazon API key"}
                else:
                    return {"valid": False, "provider": "amazon", "error": f"Amazon API error: {response.status_code}"}
        except Exception as e:
            return {"valid": False, "provider": "amazon", "error": f"Failed to validate Amazon key: {str(e)}"}


api_key_validator = APIKeyValidator()
