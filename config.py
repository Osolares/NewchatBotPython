from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    ENV: str = "development"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    TELEGRAM_BOT_TOKEN: Optional[str]

    WHATSAPP_TOKEN: Optional[str]
    PHONE_NUMBER_ID: Optional[str]
    WHATSAPP_API_VERSION: str = "v17.0"
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: Optional[str]
    FACEBOOK_APP_SECRET: Optional[str]

    LANGGRAPH_ENDPOINT: Optional[str]
    LANGGRAPH_API_KEY: Optional[str]

    WC_URL: Optional[str]
    WC_CONSUMER_KEY: Optional[str]
    WC_CONSUMER_SECRET: Optional[str]

    DATABASE_URL: str = "sqlite:///./multibot.db"
    REDIS_URL: Optional[str] = None

    TIMEZONE: str = "America/Guatemala"
    HOLIDAYS_JSON_PATH: str = "./data/holidays.json"

    ADMIN_API_KEY: Optional[str]
    ADMIN_EMAILS: Optional[str]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()
