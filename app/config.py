import logging
from pydantic_settings import BaseSettings, SettingsConfigDict

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

class Settings(BaseSettings):

    GEMINI_API_KEY: str
    MONGODB_URI: str
    
    MONGODB_DB_NAME: str = "interview_assistant"
    
    ENVIRONMENT: str = "development"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()