from typing import Dict, Any, List, Optional
import os
from pydantic_settings import BaseSettings
from pydantic import Field, SecretStr
from functools import lru_cache
from pathlib import Path

class Settings(BaseSettings):
    """
    Application settings.
    Loads from environment variables with fallback to default values.
    """
    
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Prometheus Bot"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "Automated trading, content generation, and service delivery system"
    
    # Security
    SECRET_KEY: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_HASH_ALGORITHM: str = "bcrypt"
    
    # CORS
    CORS_ORIGINS: List[str] = ["*"]
    CORS_HEADERS: List[str] = ["*"]
    
    # Database
    DATABASE_URL: str
    SQL_ECHO: bool = False
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_POOL_SIZE: int = 10
    
    # Trading
    TRADING_ENABLED: bool = True
    MAX_POSITIONS: int = 10
    DEFAULT_LEVERAGE: float = 1.0
    RISK_PERCENTAGE: float = 1.0
    STOP_LOSS_PERCENTAGE: float = 2.0
    TAKE_PROFIT_PERCENTAGE: float = 4.0
    
    # Content Generation
    CONTENT_GENERATION_ENABLED: bool = True
    OPENAI_API_KEY: str
    OPENAI_MODEL: str = "gpt-4"
    OPENAI_TEMPERATURE: float = 0.7
    OPENAI_MAX_TOKENS: int = 2000
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS_PER_MINUTE: int = 60
    RATE_LIMIT_REQUESTS_PER_HOUR: int = 1000
    RATE_LIMIT_BURST_SIZE: int = 10
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: str = "prometheus.log"
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = True
    PROMETHEUS_PORT: int = 9090
    SENTRY_DSN: Optional[str] = None
    
    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_MAX_SIZE: int = 1000
    
    # File Storage
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = ["jpg", "jpeg", "png", "pdf"]
    
    # Email
    SMTP_HOST: str = "localhost"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_EMAIL: str = "noreply@prometheus-bot.com"
    
    # Webhook
    WEBHOOK_ENABLED: bool = False
    WEBHOOK_SECRET: str = ""
    WEBHOOK_TIMEOUT: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

def get_base_dir() -> Path:
    """Get the base directory of the project"""
    return Path(__file__).resolve().parent.parent

def get_upload_dir() -> Path:
    """Get the upload directory path"""
    upload_dir = get_base_dir() / get_settings().UPLOAD_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir

def get_log_dir() -> Path:
    """Get the log directory path"""
    log_dir = get_base_dir() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir 