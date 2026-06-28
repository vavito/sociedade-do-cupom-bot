from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = Field(default="local", alias="APP_ENV")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    database_url: str = Field(alias="DATABASE_URL")

    telegram_bot_token: str = Field(default="", alias="TELEGRAM_BOT_TOKEN")
    telegram_chat_id: str = Field(default="", alias="TELEGRAM_CHAT_ID")
    telegram_post_bot_enabled: bool = Field(default=True, alias="TELEGRAM_POST_BOT_ENABLED")

    aliexpress_app_key: str = Field(default="", alias="ALIEXPRESS_APP_KEY")
    aliexpress_app_secret: str = Field(default="", alias="ALIEXPRESS_APP_SECRET")
    aliexpress_tracking_id: str = Field(default="", alias="ALIEXPRESS_TRACKING_ID")
    aliexpress_api_base_url: str = Field(
        default="https://api-sg.aliexpress.com/sync",
        alias="ALIEXPRESS_API_BASE_URL",
    )

    shopee_app_id: str = Field(default="", alias="SHOPEE_APP_ID")
    shopee_secret: str = Field(default="", alias="SHOPEE_SECRET")
    shopee_sub_id: str = Field(default="telegram", alias="SHOPEE_SUB_ID")
    shopee_api_base_url: str = Field(
        default="https://open-api.affiliate.shopee.com.br/graphql",
        alias="SHOPEE_API_BASE_URL",
    )

    scheduler_interval_minutes: int = Field(default=10, alias="SCHEDULER_INTERVAL_MINUTES")
    scheduler_enabled: bool = Field(default=True, alias="SCHEDULER_ENABLED")

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
