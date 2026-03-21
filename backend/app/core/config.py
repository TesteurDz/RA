import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "RA - Reputation Analyzer"
    DATABASE_URL: str = "sqlite+aiosqlite:///./ra.db"
    UPLOAD_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "static", "uploads")
    MISTRAL_API_KEY: str = "87m8LTifjN5H1TwaVtBAjpc1CPgzlSK1"

    # VPS Claude proxy fallback for OCR
    VPS_PROXY_URL: str = "http://187.124.37.159:3333"
    VPS_PROXY_TOKEN: str = "8603178f5dce57a05d78f909509ff026af8ffb34880b59c043d4f83fe7184b3e"

    class Config:
        env_file = ".env"


settings = Settings()

os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
