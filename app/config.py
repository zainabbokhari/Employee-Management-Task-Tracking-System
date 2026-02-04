"""
Application Configuration Settings
Uses pydantic-settings for environment variable management
"""
from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database (SQLite default for easy setup, change to MySQL for production)
    DATABASE_URL: str = "sqlite:///./employee_management.db"
    
    # JWT Settings
    SECRET_KEY: str = "your-super-secret-key-change-this"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Application Settings
    APP_NAME: str = "Employee Management System"
    DEBUG: bool = True
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Convert comma-separated origins to list"""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance"""
    return Settings()


settings = get_settings()
