import httpx
from loguru import logger

from voicetools.config import settings


class LLMError(Exception):
    pass


async def call_strong_model(
    messages: list[dict],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1024,
) -> str:
    model = model or settings.strong_model
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {settings.openrouter_api_key}",
                "HTTP-Referer": "https://valet.ai",
                "X-Title": "Valet AI",
            },
            json={
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            },
        )
        if response.status_code != 200:
            raise LLMError(f"OpenRouter error {response.status_code}: {response.text}")
        data = response.json()
        return data["choices"][0]["message"]["content"]
