# app/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_title: str
    openai_api_key: str

    # .env 파일 지정
    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
