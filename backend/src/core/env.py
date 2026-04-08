from pydantic import SecretStr
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: SecretStr
    OPENAI_BASE_URL: str
    OPENAI_MODEL: str


env = Settings(_env_file='.env', _env_file_encoding='utf-8')
