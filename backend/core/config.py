import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # API Configuration
    PROJECT_NAME: str = "Lowball.ai"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security
    API_SECRET_TOKEN: str
    GOOGLE_API_KEY: Optional[str] = None
    
    # Database
    DB_PATH: str = "lowball.db"
    
    # Business Logic Limits
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    CONVERSATION_WINDOW: int = 10

    # Ensure .env is loaded from the backend directory regardless of where the app is started
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"),
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()
