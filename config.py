# config.py
from pydantic import BaseSettings, AnyHttpUrl
from typing import Optional
import os

class Settings(BaseSettings):
    ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Telegram
    TELEGRAM_BOT_TOKEN: Optional[str]

    # WhatsApp
    WHATSAPP_TOKEN: Optional[str]
    PHONE_NUMBER_ID: Optional[str]
    WHATSAPP_API_VERSION: str = "v17.0"
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: Optional[str]
    FACEBOOK_APP_SECRET: Optional[str]

    # LangGraph
    LANGGRAPH_ENDPOINT: Optional[str]
    LANGGRAPH_API_KEY: Optional[str]

    # WooCommerce
    WC_URL: Optional[str]
    WC_CONSUMER_KEY: Optional[str]
    WC_CONSUMER_SECRET: Optional[str]

    # DB + redis
    DATABASE_URL: str = "sqlite:///./multibot.db"
    REDIS_URL: Optional[str] = None

    # Timezone / holidays
    TIMEZONE: str = "America/Guatemala"
    HOLIDAYS_JSON_PATH: str = "./data/holidays.json"

    ADMIN_EMAILS: str = "intermotores.ventas@gmail.com"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
