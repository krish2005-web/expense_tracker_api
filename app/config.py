from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_SQLITE_URL = f"sqlite:///{(BASE_DIR / 'expense_tracker.db').as_posix()}"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = DEFAULT_SQLITE_URL
    SECRET_KEY: str = "dev-only-change-this-in-production"
    ALGORITHM: str = "HS256"
    FRONTEND_URL: str = "http://localhost:5500"


settings = Settings()
