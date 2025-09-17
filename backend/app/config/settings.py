from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # Application Settings
    app_name: str = "Dripple Video Processing API"
    app_version: str = "1.0.0"
    debug: bool = False
    secret_key: str = "your-secret-key-change-in-production"
    
    # Database Settings
    database_url: str = "postgresql://dripple_user:password@localhost:5432/dripple_db"
    
    # Redis Settings
    redis_url: str = "redis://localhost:6379/0"
    
    # File Storage Settings
    upload_dir: str = "./uploads"
    processed_dir: str = "./processed"
    max_file_size: int = 500 * 1024 * 1024  # 500MB
    allowed_extensions: list = ["mp4", "avi", "mov", "mkv", "webm"]
    
    # FFmpeg Settings
    ffmpeg_path: str = "ffmpeg"
    ffprobe_path: str = "ffprobe"
    
    # Celery Settings
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/0"
    
    # Security Settings
    access_token_expire_minutes: int = 30
    algorithm: str = "HS256"
    
    # CORS Settings
    allowed_origins: list = ["*"]
    allowed_methods: list = ["*"]
    allowed_headers: list = ["*"]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Ensure directories exist
os.makedirs(settings.upload_dir, exist_ok=True)
os.makedirs(settings.processed_dir, exist_ok=True)
