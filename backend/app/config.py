"""
Configuration settings for FilaDB
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Database
    DATABASE_URL: str = "postgresql://filadb_user:filadb_password@localhost:5432/filadb"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    
    # SpoolmanDB Integration
    SPOOLMAN_DB_URL: str = "https://donkie.github.io/SpoolmanDB"
    SPOOLMAN_DB_SYNC_INTERVAL: int = 3600  # 1 hour in seconds
    
    # File uploads
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # NFC Settings
    NFC_TAG_PREFIX: str = "FILADB"
    
    # Application
    APP_NAME: str = "FilaDB"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
