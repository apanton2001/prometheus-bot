import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from contextlib import contextmanager
import logging
from typing import Generator
from dotenv import load_dotenv
from pathlib import Path

from core.config import get_settings

# Load environment variables
load_dotenv()

settings = get_settings()
logger = logging.getLogger(__name__)

# Get database URL from environment or use default SQLite database
def get_database_url():
    """Get database URL from environment variables or use default SQLite database"""
    db_user = os.getenv("DB_USER", "")
    db_pass = os.getenv("DB_PASS", "")
    db_host = os.getenv("DB_HOST", "")
    db_port = os.getenv("DB_PORT", "")
    db_name = os.getenv("DB_NAME", "")
    
    # If PostgreSQL configuration is available, use it
    if db_user and db_pass and db_host and db_port and db_name:
        return f"postgresql://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}"
    
    # Otherwise use SQLite
    base_dir = Path(__file__).resolve().parent.parent
    return f"sqlite:///{base_dir}/prometheus.db"

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    echo=settings.SQL_ECHO
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

def init_db() -> None:
    """Initialize the database by creating all tables"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {str(e)}")
        raise

@contextmanager
def get_db() -> Generator[Session, None, None]:
    """Get database session with automatic cleanup"""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"Database error: {str(e)}")
        raise
    finally:
        db.close()

def get_db_session() -> Session:
    """Get a new database session"""
    return SessionLocal()

def close_db() -> None:
    """Close all database connections"""
    engine.dispose()
    logger.info("Database connections closed")

# Import all models here to ensure they are registered with Base
from models.user import User, Role, Subscription, SubscriptionPlan, TradingAccount, APIKey
from models.trading import Position, Trade, PerformanceMetrics
from models.content import Content, ContentTemplate
from models.service import Service, ServiceInstance
from models.market import MarketData, TechnicalIndicator
from models.notification import Notification, NotificationTemplate
from models.audit import AuditLog
from models.cache import CacheEntry
from models.monitoring import SystemMetric, Alert, AlertRule

if __name__ == "__main__":
    # Initialize the database if this file is run directly
    from .schema import init_db
    init_db(engine)
    print("Database initialized successfully") 