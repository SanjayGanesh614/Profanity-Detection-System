from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str = "sqlite:///./spazor.db"
    toxicity_threshold: float = 0.8
    discord_webhook_url: str = ""
    port: int = 8000
    environment: str = "development"
    groq_api_key: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()
