from functools import lru_cache

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

"""
Load environment variables from .env
"""
load_dotenv()


class Settings(BaseSettings):
    """
    Application configuration loaded from environment variables.
    """

    # Runtime configuration
    ENVIRONMENT: str
    DEBUG: bool

    # Basic app metadata
    APP_NAME: str
    APP_VERSION: str
    API_PREFIX: str
    API_HOST: str
    API_PORT: int

    # CORS configuration
    CORS_ORIGINS: list[str]
    CORS_CREDENTIALS: bool
    CORS_METHODS: list[str]
    CORS_HEADERS: list[str]

    # Logging
    LOG_LEVEL: str

    # Schema files
    SCHEMA_DIR_PATH: str
    SCHEMA_FILE_NAME: str

    # Database connection
    DATABASE_URL: str
    DATABASE_TABLE_NAME: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached singleton instance of Settings.
    """
    return Settings()
