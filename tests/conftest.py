import pytest
from unittest.mock import AsyncMock, MagicMock

from voicetools.config import Settings


@pytest.fixture
def mock_settings(monkeypatch):
    s = Settings(openrouter_api_key="test-key-123", deepgram_api_key="test-deepgram-key")
    monkeypatch.setattr("voicetools.config.settings", s)
    monkeypatch.setattr("voicetools.llm.settings", s)
    return s


@pytest.fixture(autouse=True)
def reset_provider(monkeypatch):
    """Reset provider singletons before each test so tests are isolated."""
    import voicetools.backends.provider as provider
    monkeypatch.setattr(provider, "_mock_booking", None)
    monkeypatch.setattr(provider, "_mock_shop", None)
    monkeypatch.setattr(provider, "_mock_user", None)


@pytest.fixture
def mock_params():
    params = MagicMock()
    params.result_callback = AsyncMock()
    params.arguments = {}
    return params
