from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GitHub To Tech Blog (GTTB)"
    github_token: str | None = None
    github_api_base: str = "https://api.github.com"
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"
    database_url: str = "sqlite:///./gttb.db"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
