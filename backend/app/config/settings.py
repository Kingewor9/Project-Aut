from __future__ import annotations

from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    app_env: str = "development"
    app_secret: str = "changeme-super-secret-key"

    # MongoDB
    mongodb_uri: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "automata_tg"

    # Telegram
    telegram_bot_token: str = ""
    telegram_webhook_secret: str = ""
    telegram_mini_app_url: str = ""
    telegram_support_username: str = "automata_support"
    telegram_announce_channel: str = "https://t.me/automata_tg"

    # Gemini AI
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    test_generation_allowance: int = 3
    style_analysis_allowance: int = 3
    usage_credit_pack_size: int = 5
    usage_credit_pack_price_stars: int = 150

    # Social links
    social_twitter: str = "https://twitter.com/automatatg"
    social_instagram: str = "https://instagram.com/automatatg"
    social_tiktok: str = "https://tiktok.com/@automatatg"
    social_website: str = "https://automatatg.com"

    # CORS
    cors_origins: str = "*"

    @property
    def cors_origins_list(self) -> list[str]:
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",")]

    @property
    def is_production(self) -> bool:
        return self.app_env == "production"


settings = Settings()
