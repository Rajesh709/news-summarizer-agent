from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    # NewsAPI
    news_api_key: str
    news_api_base_url: str = "https://newsapi.org/v2"

    # Redis (REDIS_URL takes priority — set automatically by Railway)
    redis_url: Optional[str] = None
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_password: str = ""
    redis_db: int = 0
    redis_ttl: int = 3600

    # App
    app_env: str = "development"
    app_host: str = "0.0.0.0"
    app_port: int = 8001
    log_level: str = "INFO"

    # Streamlit
    streamlit_port: int = 8502
    backend_url: str = "http://localhost:8001"

    # Email (Gmail SMTP)
    email_sender: str = ""
    email_app_password: str = ""
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 465

    # Daily Digest Scheduler
    digest_recipient: str = "rajeshkm.709@gmail.com"
    digest_time: str = "07:00"          # 24h format — 7:00 AM
    digest_timezone: str = "Asia/Kolkata"  # IST

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()
