import logging
import sys
from typing import Optional
from pathlib import Path

from core.config import get_settings, get_log_dir

settings = get_settings()

def setup_logging() -> None:
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    log_dir = get_log_dir()
    log_dir.mkdir(parents=True, exist_ok=True)
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Create formatters
    formatter = logging.Formatter(settings.LOG_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(settings.LOG_LEVEL)
    
    # File handler
    file_handler = logging.FileHandler(log_dir / settings.LOG_FILE)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(settings.LOG_LEVEL)
    
    # Add handlers
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """Get a logger instance with the specified name and level"""
    logger = logging.getLogger(name)
    
    if level:
        logger.setLevel(level)
    else:
        logger.setLevel(settings.LOG_LEVEL)
    
    # Prevent propagation to root logger if handlers already exist
    if logger.handlers:
        logger.propagate = False
    
    return logger

def get_trading_logger() -> logging.Logger:
    """Get logger for trading operations"""
    return get_logger("trading")

def get_api_logger() -> logging.Logger:
    """Get logger for API operations"""
    return get_logger("api")

def get_data_logger() -> logging.Logger:
    """Get logger for data operations"""
    return get_logger("data")

def get_content_logger() -> logging.Logger:
    """Get logger for content generation"""
    return get_logger("content")

def get_system_logger() -> logging.Logger:
    """Get logger for system operations"""
    return get_logger("system") 