from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class Settings(BaseSettings):
    """Настройки приложения из переменных окружения."""

    # Telegram
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")

    # Market Provider
    market_provider: Literal["mock", "steam", "csfloat", "skinport"] = Field(
        default="mock", env="MARKET_PROVIDER"
    )
    market_api_key: str | None = Field(default=None, env="MARKET_API_KEY")
    market_api_url: str | None = Field(default=None, env="MARKET_API_URL")

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/cs2_market_bot",
        env="DATABASE_URL",
    )

    # Redis
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")

    # Fee
    fee_percent: float = Field(default=0.15, env="FEE_PERCENT")

    # Currency
    default_currency: Literal["RUB", "USD"] = Field(default="RUB", env="DEFAULT_CURRENCY")

    # Rate limits - Free
    free_scan_interval_minutes: int = Field(default=30, env="FREE_SCAN_INTERVAL_MINUTES")
    max_free_filters: int = Field(default=3, env="MAX_FREE_FILTERS")
    max_free_signals: int = Field(default=10, env="MAX_FREE_SIGNALS")

    # Rate limits - Premium
    premium_scan_interval_minutes: int = Field(default=5, env="PREMIUM_SCAN_INTERVAL_MINUTES")
    max_premium_filters: int = Field(default=20, env="MAX_PREMIUM_FILTERS")
    max_premium_signals: int = Field(default=100, env="MAX_PREMIUM_SIGNALS")

    # Signal duplicate window
    signal_duplicate_window_hours: int = Field(default=6, env="SIGNAL_DUPLICATE_WINDOW_HOURS")

    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
