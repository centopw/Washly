from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    openrouter_api_key: str
    deepgram_api_key: str
    voice_model: str = "openai/gpt-4o-mini"
    strong_model: str = "openai/gpt-4o"
    tts_voice_id: str = "bf_emma"
    stt_model: str = "large-v3-turbo"
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_database: str = "valet"
    backend: str = "mock"
    log_level: str = "INFO"
    server_host: str = "0.0.0.0"
    server_port: int = 7860


settings = Settings()
