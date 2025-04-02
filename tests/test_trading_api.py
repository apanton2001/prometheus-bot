import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
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
def sample_market_data():
    """Create sample market data for testing."""
    dates = pd.date_range(
        start=datetime.utcnow() - timedelta(hours=100),
        periods=100,
        freq='1h'
    )
    
    base_price = 50000
    prices = base_price + np.random.normal(0, 1000, 100).cumsum()
    
    data = pd.DataFrame({
        'open': prices + np.random.normal(0, 100, 100),
        'high': prices + abs(np.random.normal(0, 200, 100)),
        'low': prices - abs(np.random.normal(0, 200, 100)),
        'close': prices + np.random.normal(0, 100, 100),
        'volume': abs(np.random.normal(100, 20, 100))
    }, index=dates)
    
    data['high'] = data[['open', 'close']].max(axis=1) + abs(np.random.normal(0, 100, 100))
    data['low'] = data[['open', 'close']].min(axis=1) - abs(np.random.normal(0, 100, 100))
    
    return data

def test_get_positions(test_headers):
    """Test getting all positions."""
    response = client.get("/trading/positions", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "positions" in data
    assert "timestamp" in data
    assert isinstance(data["positions"], list)

def test_get_position(test_headers):
    """Test getting position for a specific symbol."""
    # Test with non-existent position
    response = client.get("/trading/positions/BTC/USDT", headers=test_headers)
    assert response.status_code == 404
    
    # Test with valid symbol
    response = client.get("/trading/positions/ETH/USDT", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert "position" in data
    assert "timestamp" in data

def test_get_trades(test_headers):
    """Test getting trade history."""
    # Test without filters
    response = client.get("/trading/trades", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "trades" in data
    assert "timestamp" in data
    assert isinstance(data["trades"], list)
    
    # Test with symbol filter
    response = client.get("/trading/trades?symbol=BTC/USDT", headers=test_headers)
    assert response.status_code == 200
    
    # Test with date filters
    start_date = datetime.utcnow() - timedelta(days=7)
    end_date = datetime.utcnow()
    response = client.get(
        f"/trading/trades?start_date={start_date}&end_date={end_date}",
        headers=test_headers
    )
    assert response.status_code == 200

def test_get_performance(test_headers):
    """Test getting performance metrics."""
    response = client.get("/trading/performance", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "timestamp" in data
    assert isinstance(data["metrics"], dict)

def test_get_balance(test_headers):
    """Test getting account balance."""
    response = client.get("/trading/balance", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "balance" in data
    assert "timestamp" in data
    assert isinstance(data["balance"], float)

def test_update_market_data(test_headers, sample_market_data):
    """Test updating market data."""
    # Convert DataFrame to dict for request
    data_dict = sample_market_data.to_dict(orient='records')
    
    response = client.post(
        "/trading/update?symbol=BTC/USDT",
        headers=test_headers,
        json={"data": data_dict}
    )
    assert response.status_code == 200
    data = response.json()
    assert "symbol" in data
    assert "signal" in data
    assert "closed_positions" in data
    assert "timestamp" in data

def test_get_daily_report(test_headers):
    """Test getting daily trading report."""
    response = client.get("/trading/report/daily", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "timestamp" in data
    assert isinstance(data["report"], str)

def test_get_performance_report(test_headers):
    """Test getting performance report."""
    response = client.get("/trading/report/performance", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert "report" in data
    assert "timestamp" in data
    assert isinstance(data["report"], str)

def test_unauthorized_access():
    """Test access without authentication."""
    response = client.get("/trading/positions")
    assert response.status_code == 401

def test_invalid_symbol(test_headers):
    """Test with invalid trading symbol."""
    response = client.get("/trading/positions/INVALID", headers=test_headers)
    assert response.status_code == 404

def test_invalid_date_range(test_headers):
    """Test with invalid date range."""
    start_date = datetime.utcnow()
    end_date = datetime.utcnow() - timedelta(days=1)
    response = client.get(
        f"/trading/trades?start_date={start_date}&end_date={end_date}",
        headers=test_headers
    )
    assert response.status_code == 200  # Should handle invalid date range gracefully

def test_error_handling(test_headers):
    """Test error handling for invalid endpoints and methods."""
    # Test invalid endpoint
    response = client.get("/trading/invalid", headers=test_headers)
    assert response.status_code == 404
    
    # Test invalid method
    response = client.post("/trading/positions", headers=test_headers)
    assert response.status_code == 405

def test_rate_limiting(test_headers):
    """Test rate limiting by making multiple requests."""
    for _ in range(10):
        response = client.get("/trading/positions", headers=test_headers)
        assert response.status_code in [200, 429]  # Should either succeed or be rate limited 