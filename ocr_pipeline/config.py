import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MAX_FILE_SIZE_MB: int = 20
    SUPPORTED_MIME: list = ["application/pdf"]
    OCR_LANG: str = "eng"
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = "gpt-4o"
    REDIS_URL: str = "memory://"        # use "redis://localhost:6379/0" for real Redis
    RESULT_TTL_SECONDS: int = 86400     # 24 h
    MOCK_LLM: bool = False              # set True in CI to skip real OpenAI calls

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
