from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )
    
    BOT_TOKEN: str = Field(..., description="Токен Telegram бота")
    ADMIN_ID: int = Field(..., description="Telegram ID администратора")


config = Settings()
