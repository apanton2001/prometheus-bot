import pytest
import os
from unittest.mock import patch
from ...core.config import Settings, get_settings

@pytest.fixture
def mock_env():
    """Create a mock environment for testing."""
    env_vars = {
        "SECRET_KEY": "test-secret-key",
        "DATABASE_URL": "sqlite:///./test.db",
        "EXCHANGE_ID": "test-exchange",
        "EXCHANGE_API_KEY": "test-api-key",
        "EXCHANGE_API_SECRET": "test-api-secret",
        "INITIAL_BALANCE": "5000.0",
        "RISK_PERCENTAGE": "2.0",
        "MAX_POSITION_SIZE": "500.0",
        "RATE_LIMIT_REQUESTS": "50",
        "RATE_LIMIT_WINDOW": "30",
        "LOG_LEVEL": "DEBUG",
        "LOG_FORMAT": "test-format",
        "CACHE_TTL": "600",
        "ENABLE_METRICS": "False",
        "METRICS_PORT": "8080"
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars

def test_default_settings():
    """Test default settings values."""
    settings = Settings()
    
    # Test API settings
    assert settings.API_V1_STR == "/api/v1"
    assert settings.PROJECT_NAME == "Prometheus Bot"
    assert settings.VERSION == "0.1.0"
    assert settings.DESCRIPTION == "AI-powered trading bot with market analysis"
    
    # Test security settings
    assert settings.ALGORITHM == "HS256"
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES == 30
    
    # Test database settings
    assert settings.DATABASE_URL == "sqlite:///./prometheus.db"
    
    # Test exchange settings
    assert settings.EXCHANGE_ID == "binance"
    assert settings.EXCHANGE_API_KEY.get_secret_value() == ""
    assert settings.EXCHANGE_API_SECRET.get_secret_value() == ""
    
    # Test trading settings
    assert settings.INITIAL_BALANCE == 10000.0
    assert settings.RISK_PERCENTAGE == 1.0
    assert settings.MAX_POSITION_SIZE == 1000.0
    
    # Test strategy settings
    assert settings.TRADING_STRATEGY_CONFIG["fast_ma_period"] == 10
    assert settings.TRADING_STRATEGY_CONFIG["slow_ma_period"] == 20
    assert settings.TRADING_STRATEGY_CONFIG["rsi_period"] == 14
    assert settings.TRADING_STRATEGY_CONFIG["rsi_overbought"] == 70
    assert settings.TRADING_STRATEGY_CONFIG["rsi_oversold"] == 30
    assert settings.TRADING_STRATEGY_CONFIG["stop_loss_pct"] == 2.0
    assert settings.TRADING_STRATEGY_CONFIG["take_profit_pct"] == 4.0
    
    # Test content generator settings
    assert settings.CONTENT_GENERATOR_CONFIG["model_name"] == "gpt-4"
    assert settings.CONTENT_GENERATOR_CONFIG["temperature"] == 0.7
    assert settings.CONTENT_GENERATOR_CONFIG["max_tokens"] == 1000
    assert settings.CONTENT_GENERATOR_CONFIG["rsi_period"] == 14
    assert settings.CONTENT_GENERATOR_CONFIG["ma_periods"] == [20, 50, 200]
    
    # Test rate limiting settings
    assert settings.RATE_LIMIT_REQUESTS == 100
    assert settings.RATE_LIMIT_WINDOW == 60
    
    # Test logging settings
    assert settings.LOG_LEVEL == "INFO"
    assert "%(asctime)s" in settings.LOG_FORMAT
    
    # Test cache settings
    assert settings.CACHE_TTL == 300
    
    # Test monitoring settings
    assert settings.ENABLE_METRICS is True
    assert settings.METRICS_PORT == 9090

def test_env_settings(mock_env):
    """Test settings loaded from environment variables."""
    settings = Settings()
    
    # Test API settings
    assert settings.SECRET_KEY.get_secret_value() == "test-secret-key"
    assert settings.DATABASE_URL == "sqlite:///./test.db"
    
    # Test exchange settings
    assert settings.EXCHANGE_ID == "test-exchange"
    assert settings.EXCHANGE_API_KEY.get_secret_value() == "test-api-key"
    assert settings.EXCHANGE_API_SECRET.get_secret_value() == "test-api-secret"
    
    # Test trading settings
    assert settings.INITIAL_BALANCE == 5000.0
    assert settings.RISK_PERCENTAGE == 2.0
    assert settings.MAX_POSITION_SIZE == 500.0
    
    # Test rate limiting settings
    assert settings.RATE_LIMIT_REQUESTS == 50
    assert settings.RATE_LIMIT_WINDOW == 30
    
    # Test logging settings
    assert settings.LOG_LEVEL == "DEBUG"
    assert settings.LOG_FORMAT == "test-format"
    
    # Test cache settings
    assert settings.CACHE_TTL == 600
    
    # Test monitoring settings
    assert settings.ENABLE_METRICS is False
    assert settings.METRICS_PORT == 8080

def test_get_settings():
    """Test get_settings function."""
    settings1 = get_settings()
    settings2 = get_settings()
    
    # Test that the same instance is returned
    assert settings1 is settings2

def test_case_sensitivity():
    """Test case sensitivity of settings."""
    settings = Settings()
    
    # Test that settings are case sensitive
    assert hasattr(settings, "API_V1_STR")
    assert not hasattr(settings, "api_v1_str")

def test_env_file():
    """Test loading settings from .env file."""
    # Create a temporary .env file
    with open(".env", "w") as f:
        f.write("""
        SECRET_KEY=test-secret-key
        DATABASE_URL=sqlite:///./test.db
        EXCHANGE_ID=test-exchange
        """)
    
    try:
        settings = Settings()
        assert settings.SECRET_KEY.get_secret_value() == "test-secret-key"
        assert settings.DATABASE_URL == "sqlite:///./test.db"
        assert settings.EXCHANGE_ID == "test-exchange"
    finally:
        # Clean up
        if os.path.exists(".env"):
            os.remove(".env")

def test_type_conversion():
    """Test type conversion of settings values."""
    settings = Settings()
    
    # Test numeric types
    assert isinstance(settings.INITIAL_BALANCE, float)
    assert isinstance(settings.RISK_PERCENTAGE, float)
    assert isinstance(settings.MAX_POSITION_SIZE, float)
    assert isinstance(settings.RATE_LIMIT_REQUESTS, int)
    assert isinstance(settings.RATE_LIMIT_WINDOW, int)
    assert isinstance(settings.CACHE_TTL, int)
    assert isinstance(settings.METRICS_PORT, int)
    
    # Test boolean type
    assert isinstance(settings.ENABLE_METRICS, bool)
    
    # Test string types
    assert isinstance(settings.API_V1_STR, str)
    assert isinstance(settings.PROJECT_NAME, str)
    assert isinstance(settings.VERSION, str)
    assert isinstance(settings.DESCRIPTION, str)
    assert isinstance(settings.ALGORITHM, str)
    assert isinstance(settings.DATABASE_URL, str)
    assert isinstance(settings.EXCHANGE_ID, str)
    assert isinstance(settings.LOG_LEVEL, str)
    assert isinstance(settings.LOG_FORMAT, str)
    
    # Test dictionary types
    assert isinstance(settings.TRADING_STRATEGY_CONFIG, dict)
    assert isinstance(settings.CONTENT_GENERATOR_CONFIG, dict)

def test_secret_str():
    """Test handling of secret values."""
    settings = Settings()
    
    # Test that secret values are properly wrapped
    assert isinstance(settings.SECRET_KEY, SecretStr)
    assert isinstance(settings.EXCHANGE_API_KEY, SecretStr)
    assert isinstance(settings.EXCHANGE_API_SECRET, SecretStr)
    
    # Test that secret values can be accessed
    assert settings.SECRET_KEY.get_secret_value() is not None
    assert settings.EXCHANGE_API_KEY.get_secret_value() is not None
    assert settings.EXCHANGE_API_SECRET.get_secret_value() is not None 