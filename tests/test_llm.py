import pytest
import respx
import httpx

from voicetools.llm import LLMError, call_strong_model


@pytest.mark.asyncio
@respx.mock
async def test_call_strong_model_success(mock_settings):
    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=httpx.Response(
            200,
            json={"choices": [{"message": {"content": "Hello there"}}]},
        )
    )
    result = await call_strong_model([{"role": "user", "content": "Hi"}])
    assert result == "Hello there"


@pytest.mark.asyncio
@respx.mock
async def test_call_strong_model_raises_on_error(mock_settings):
    respx.post("https://openrouter.ai/api/v1/chat/completions").mock(
        return_value=httpx.Response(500, text="Server error")
    )
    with pytest.raises(LLMError):
        await call_strong_model([{"role": "user", "content": "Hi"}])
