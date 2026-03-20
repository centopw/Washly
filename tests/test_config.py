import pytest
from pydantic import ValidationError

from voicetools.config import Settings


def test_settings_loads_with_required_key():
    s = Settings(openrouter_api_key="sk-test")
    assert s.openrouter_api_key == "sk-test"


def test_settings_defaults():
    s = Settings(openrouter_api_key="sk-test")
    assert s.voice_model == "openai/gpt-4o-mini"
    assert s.strong_model == "openai/gpt-4o"
    assert s.tts_voice_id == "bf_emma"
    assert s.log_level == "INFO"
    assert s.server_host == "0.0.0.0"
    assert s.server_port == 7860


def test_settings_fails_without_api_key():
    with pytest.raises(ValidationError):
        Settings()
