"""Application settings loaded from environment variables / .env."""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    """Runtime configuration. Secrets must come from env, never hardcoded."""

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    DATABASE_URL: str = "postgresql+asyncpg://postgres:Bhoomi123@localhost:5432/smart_farmer"

    JWT_SECRET: str = "change-me-to-a-long-random-string"

    JWT_ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    OPENWEATHER_API_KEY: str = ""

    DATA_GOV_API_KEY: str = ""

    CORS_ORIGINS: str = "*"

    @property
    def cors_origin_list(self) -> list[str]:
        raw = self.CORS_ORIGINS.strip()

        if raw == "*":
            return ["*"]

        return [
            part.strip()
            for part in raw.split(",")
            if part.strip()
        ]




settings = Settings()

print("DATABASE URL:", settings.DATABASE_URL)
print("OPENWEATHER KEY LOADED:", bool(settings.OPENWEATHER_API_KEY))