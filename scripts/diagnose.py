"""Standalone API health check for Valet voice services."""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import httpx

from voicetools.config import settings
from voicetools.tools.schemas import ALL_SCHEMAS


def build_tools() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": schema.name,
                "description": schema.description,
                "parameters": {
                    "type": "object",
                    "properties": schema.properties,
                    "required": schema.required,
                },
            },
        }
        for schema in ALL_SCHEMAS
    ]


async def test_openrouter(
    client: httpx.AsyncClient, *, with_stream_options: bool
) -> tuple[str, str | None]:
    """Returns (status, error_detail)."""
    label = "WITH" if with_stream_options else "WITHOUT"
    body: dict = {
        "model": settings.voice_model,
        "stream": True,
        "messages": [{"role": "user", "content": "Say 'hello' in one word."}],
        "tools": build_tools(),
        "max_tokens": 20,
    }
    if with_stream_options:
        body["stream_options"] = {"include_usage": True}

    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": "https://valet.ai",
        "X-Title": "Valet AI",
        "Content-Type": "application/json",
    }

    try:
        async with client.stream(
            "POST",
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=30.0,
        ) as resp:
            if resp.status_code != 200:
                body_text = ""
                async for chunk in resp.aiter_text():
                    body_text += chunk
                    if len(body_text) >= 500:
                        break
                return "FAIL", f"HTTP {resp.status_code}: {body_text[:500]}"

            got_chunk = False
            async for line in resp.aiter_lines():
                if not line.startswith("data: "):
                    continue
                payload = line[6:].strip()
                if payload == "[DONE]":
                    break
                try:
                    data = json.loads(payload)
                except json.JSONDecodeError:
                    continue
                if "error" in data:
                    return "FAIL", f"SSE error: {json.dumps(data['error'])[:500]}"
                got_chunk = True

            if not got_chunk:
                return "FAIL", "No SSE chunks received"
            return "PASS", None
    except Exception as e:
        return "FAIL", str(e)[:500]


async def test_elevenlabs(client: httpx.AsyncClient) -> tuple[str, str | None]:
    if not settings.elevenlabs_api_key:
        return "SKIPPED", "elevenlabs_api_key not set"

    url = f"https://api.elevenlabs.io/v1/text-to-speech/{settings.elevenlabs_voice_id}"
    headers = {"xi-api-key": settings.elevenlabs_api_key}
    body = {"text": "Hello.", "model_id": settings.elevenlabs_model}

    try:
        resp = await client.post(url, headers=headers, json=body, timeout=15.0)
        if resp.status_code != 200:
            return "FAIL", f"HTTP {resp.status_code}: {resp.text[:500]}"
        ct = resp.headers.get("content-type", "")
        if "audio/" not in ct:
            return "FAIL", f"Unexpected content-type: {ct}"
        return "PASS", None
    except Exception as e:
        return "FAIL", str(e)[:500]


async def test_mongodb() -> tuple[str, str | None]:
    if settings.backend != "mongo":
        return "SKIPPED", f"backend={settings.backend}"

    try:
        from motor.motor_asyncio import AsyncIOMotorClient

        client = AsyncIOMotorClient(settings.mongodb_uri, serverSelectionTimeoutMS=5000)
        result = await client.admin.command("ping")
        if result.get("ok") == 1:
            return "PASS", None
        return "FAIL", f"Unexpected ping result: {result}"
    except Exception as e:
        return "FAIL", str(e)[:500]


async def main():
    print("\n=== Valet API Health Check ===\n")

    results: list[tuple[str, str, str | None]] = []

    async with httpx.AsyncClient() as client:
        # OpenRouter WITH stream_options
        print("[OpenRouter] WITH stream_options...", end=" ", flush=True)
        status, detail = await test_openrouter(client, with_stream_options=True)
        print(status)
        if detail and status == "FAIL":
            print(f"  {detail}")
        results.append(("OpenRouter WITH stream_options", status, detail))

        # OpenRouter WITHOUT stream_options
        print("[OpenRouter] WITHOUT stream_options...", end=" ", flush=True)
        status, detail = await test_openrouter(client, with_stream_options=False)
        print(status)
        if detail and status == "FAIL":
            print(f"  {detail}")
        results.append(("OpenRouter WITHOUT stream_options", status, detail))

        # ElevenLabs
        print("[ElevenLabs]...", end=" ", flush=True)
        status, detail = await test_elevenlabs(client)
        print(status)
        if detail and status != "PASS":
            print(f"  {detail}")
        results.append(("ElevenLabs", status, detail))

    # MongoDB
    print("[MongoDB]...", end=" ", flush=True)
    status, detail = await test_mongodb()
    print(status)
    if detail and status != "PASS":
        print(f"  {detail}")
    results.append(("MongoDB", status, detail))

    passed = sum(1 for _, s, _ in results if s == "PASS")
    failed = sum(1 for _, s, _ in results if s == "FAIL")
    skipped = sum(1 for _, s, _ in results if s == "SKIPPED")

    print(f"\n=== Summary: {passed} passed, {failed} failed, {skipped} skipped ===\n")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
