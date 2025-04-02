import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from ...api.main import app
from ...core.auth import create_access_token
from ...core.config import settings

client = TestClient(app)

@pytest.fixture
def test_token():
    """Create a test access token."""
    return create_access_token({"sub": "test_user"})

@pytest.fixture
def test_headers(test_token):
    """Create test headers with authentication token."""
    return {"Authorization": f"Bearer {test_token}"}

@pytest.fixture
def mock_provider():
    """Create a mock market data provider."""
    with patch('...api.routes.data.provider') as mock:
        provider = Mock()
        
        # Configure mock methods
        provider.get_ohlcv.return_value = pd.DataFrame({
            'open': [35000, 35050],
            'high': [35100, 35200],
            'low': [34900, 35000],
            'close': [35050, 35150],
            'volume': [100, 150]
        }, index=pd.date_range(start='2024-01-01', periods=2, freq='1h'))
        
        provider.get_ticker.return_value = {
            'symbol': 'BTC/USDT',
            'last': 35000,
            'bid': 34950,
            'ask': 35050,
            'volume': 1000,
            'timestamp': datetime.utcnow()
        }
        
        provider.get_orderbook.return_value = {
            'symbol': 'BTC/USDT',
            'bids': [[34950, 1], [34900, 2]],
            'asks': [[35050, 1], [35100, 2]],
            'timestamp': datetime.utcnow()
        }
        
        provider.get_recent_trades.return_value = [{
            'id': '123',
            'timestamp': datetime.utcnow(),
            'price': 35000,
            'amount': 0.1,
            'side': 'buy',
            'cost': 3500
        }]
        
        provider.get_symbols.return_value = ['BTC/USDT', 'ETH/USDT']
        
        provider.get_exchange_info.return_value = {
            'id': 'binance',
            'name': 'Binance',
            'version': '1.0.0',
            'timeframes': {'1h': 3600, '1d': 86400},
            'has': {'fetchOHLCV': True, 'fetchTicker': True},
            'rateLimit': 1000,
            'urls': {'api': {'public': 'https://api.binance.com/api/v3'}}
        }
        
        mock.MarketDataProvider.return_value = provider
        yield provider

def test_get_ohlcv(test_headers, mock_provider):
    """Test getting OHLCV data."""
    # Test without parameters
    response = client.get("/data/ohlcv/BTC/USDT", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert "timeframe" in data
    assert "data" in data
    assert "timestamp" in data
    assert len(data["data"]) == 2
    
    # Test with parameters
    since = datetime.utcnow() - timedelta(days=7)
    response = client.get(
        f"/data/ohlcv/BTC/USDT?timeframe=1d&since={since}&limit=50",
        headers=test_headers
    )
    assert response.status_code == 200

def test_get_ticker(test_headers, mock_provider):
    """Test getting ticker data."""
    response = client.get("/data/ticker/BTC/USDT", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert "data" in data
    assert "timestamp" in data
    assert all(key in data["data"] for key in ['last', 'bid', 'ask', 'volume'])

def test_get_orderbook(test_headers, mock_provider):
    """Test getting order book data."""
    # Test without limit
    response = client.get("/data/orderbook/BTC/USDT", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert "data" in data
    assert "timestamp" in data
    assert all(key in data["data"] for key in ['bids', 'asks'])
    
    # Test with limit
    response = client.get("/data/orderbook/BTC/USDT?limit=10", headers=test_headers)
    assert response.status_code == 200

def test_get_recent_trades(test_headers, mock_provider):
    """Test getting recent trades."""
    # Test without limit
    response = client.get("/data/trades/BTC/USDT", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert "data" in data
    assert "timestamp" in data
    assert len(data["data"]) == 1
    
    # Test with limit
    response = client.get("/data/trades/BTC/USDT?limit=20", headers=test_headers)
    assert response.status_code == 200

def test_get_symbols(test_headers, mock_provider):
    """Test getting available symbols."""
    response = client.get("/data/symbols", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "symbols" in data
    assert "timestamp" in data
    assert len(data["symbols"]) == 2
    assert all(symbol in data["symbols"] for symbol in ['BTC/USDT', 'ETH/USDT'])

def test_get_exchange_info(test_headers, mock_provider):
    """Test getting exchange information."""
    response = client.get("/data/exchange-info", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "info" in data
    assert "timestamp" in data
    assert all(key in data["info"] for key in ['id', 'name', 'version', 'timeframes'])

def test_clear_cache(test_headers, mock_provider):
    """Test clearing data cache."""
    response = client.post("/data/clear-cache", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "message" in data
    assert "timestamp" in data

def test_unauthorized_access():
    """Test access without authentication."""
    response = client.get("/data/ohlcv/BTC/USDT")
    assert response.status_code == 401

def test_invalid_symbol(test_headers, mock_provider):
    """Test with invalid trading symbol."""
    response = client.get("/data/ohlcv/INVALID", headers=test_headers)
    assert response.status_code == 500

def test_invalid_timeframe(test_headers, mock_provider):
    """Test with invalid timeframe."""
    response = client.get("/data/ohlcv/BTC/USDT?timeframe=invalid", headers=test_headers)
    assert response.status_code == 200  # Should handle invalid timeframe gracefully

def test_invalid_limit(test_headers, mock_provider):
    """Test with invalid limit."""
    response = client.get("/data/ohlcv/BTC/USDT?limit=-1", headers=test_headers)
    assert response.status_code == 200  # Should handle invalid limit gracefully

def test_error_handling(test_headers, mock_provider):
    """Test error handling for invalid endpoints and methods."""
    # Test invalid endpoint
    response = client.get("/data/invalid", headers=test_headers)
    assert response.status_code == 404
    
    # Test invalid method
    response = client.post("/data/ohlcv/BTC/USDT", headers=test_headers)
    assert response.status_code == 405

def test_rate_limiting(test_headers, mock_provider):
    """Test rate limiting by making multiple requests."""
    for _ in range(10):
        response = client.get("/data/ohlcv/BTC/USDT", headers=test_headers)
        assert response.status_code in [200, 429]  # Should either succeed or be rate limited 