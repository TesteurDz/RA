import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "RA - Reputation Analyzer"
    DATABASE_URL: str = "sqlite+aiosqlite:///./ra.db"
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "uploads")

    class Config:
        env_file = ".env"


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
