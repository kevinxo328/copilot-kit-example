from typing import Optional

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr
    OPENAI_BASE_URL: str
    OPENAI_MODEL: str
    LANGSMITH_API_KEY: Optional[str]
    TAVILY_API_KEY: str
    USE_CUSTOM_CHECKPOINTER: bool = True

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )


env = Settings()  # pyright: ignore[reportCallIssue]
