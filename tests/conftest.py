import pytest
from typing import Generator, Dict
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

# Import your models and app
from api.main import app
from database.models.base import Base

# Test database URL
TEST_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_db_engine():
    """
    Create a test database engine.
    
    Returns:
        Engine: SQLAlchemy engine for test database
    """
    engine = create_engine(TEST_DATABASE_URL)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator:
    """
    Create a test database session.
    
    Args:
        test_db_engine: SQLAlchemy engine
        
    Returns:
        Generator: Database session
    """
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    try:
        yield session
    finally:
        session.rollback()
        session.close()

@pytest.fixture(scope="module")
def test_client() -> Generator:
    """
    Create a test client for the FastAPI application.
    
    Returns:
        Generator: TestClient instance
    """
    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def mock_trading_data() -> Dict:
    """
    Create mock trading data for testing.
    
    Returns:
        Dict: Mock trading data
    """
    return {
        "symbol": "BTC/USDT",
        "timestamp": datetime.utcnow().isoformat(),
        "open": 50000.0,
        "high": 51000.0,
        "low": 49000.0,
        "close": 50500.0,
        "volume": 100.0
    }

@pytest.fixture(scope="function")
def mock_content_data() -> Dict:
    """
    Create mock content data for testing.
    
    Returns:
        Dict: Mock content data
    """
    return {
        "prompt": "Generate market analysis for BTC/USDT",
        "context": {
            "timeframe": "1h",
            "market_trend": "bullish",
            "key_levels": {
                "support": 49000,
                "resistance": 51000
            }
        }
    }

@pytest.fixture(scope="function")
def mock_service_data() -> Dict:
    """
    Create mock service data for testing.
    
    Returns:
        Dict: Mock service data
    """
    return {
        "service_id": "premium_analysis",
        "name": "Premium Market Analysis",
        "description": "Detailed market analysis with AI insights",
        "price": 99.99,
        "features": [
            "Real-time market analysis",
            "AI-powered predictions",
            "Portfolio optimization"
        ]
    }

@pytest.fixture(scope="function")
def test_user_token() -> str:
    """
    Create a test user authentication token.
    
    Returns:
        str: Test authentication token
    """
    # TODO: Implement proper token generation
    return "test_token_123"

@pytest.fixture(scope="function")
def test_headers(test_user_token) -> Dict[str, str]:
    """
    Create test request headers with authentication.
    
    Args:
        test_user_token (str): Test authentication token
        
    Returns:
        Dict[str, str]: Test request headers
    """
    return {
        "Authorization": f"Bearer {test_user_token}",
        "Content-Type": "application/json"
    } 