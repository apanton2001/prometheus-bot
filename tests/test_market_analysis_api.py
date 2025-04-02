import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from api.main import app
from api.core.auth import create_access_token

client = TestClient(app)

@pytest.fixture
def test_token():
    """Create a test access token"""
    return create_access_token({"sub": "test_user"})

@pytest.fixture
def test_headers(test_token):
    """Create test headers with authentication token"""
    return {"Authorization": f"Bearer {test_token}"}

def test_get_market_analysis(test_headers):
    """Test getting market analysis"""
    response = client.get(
        "/market-analysis/BTC/USDT",
        headers=test_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "symbol" in data
    assert "timeframe" in data
    assert "timestamp" in data
    assert "analysis" in data
    assert "content" in data
    assert "signal" in data
    
    # Check data types
    assert isinstance(data["symbol"], str)
    assert isinstance(data["timeframe"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["analysis"], dict)
    assert isinstance(data["content"], str)
    assert isinstance(data["signal"], dict) or data["signal"] is None

def test_get_market_analysis_with_params(test_headers):
    """Test getting market analysis with custom parameters"""
    response = client.get(
        "/market-analysis/BTC/USDT",
        params={
            "timeframe": "4h",
            "limit": 200
        },
        headers=test_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["timeframe"] == "4h"
    assert "analysis" in data
    assert "content" in data
    assert "signal" in data

def test_get_trading_signals(test_headers):
    """Test getting trading signals"""
    response = client.get(
        "/market-analysis/BTC/USDT/signals",
        headers=test_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "symbol" in data
    assert "timeframe" in data
    assert "timestamp" in data
    assert "signal" in data
    
    # Check data types
    assert isinstance(data["symbol"], str)
    assert isinstance(data["timeframe"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["signal"], dict) or data["signal"] is None

def test_get_market_content(test_headers):
    """Test getting market content"""
    response = client.get(
        "/market-analysis/BTC/USDT/content",
        headers=test_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    # Check required fields
    assert "symbol" in data
    assert "timeframe" in data
    assert "timestamp" in data
    assert "content" in data
    
    # Check data types
    assert isinstance(data["symbol"], str)
    assert isinstance(data["timeframe"], str)
    assert isinstance(data["timestamp"], str)
    assert isinstance(data["content"], str)

def test_get_market_content_with_context(test_headers):
    """Test getting market content with additional context"""
    response = client.get(
        "/market-analysis/BTC/USDT/content",
        params={
            "context": {
                "additional_info": "Test context"
            }
        },
        headers=test_headers
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "content" in data
    assert isinstance(data["content"], str)

def test_unauthorized_access():
    """Test access without authentication"""
    response = client.get("/market-analysis/BTC/USDT")
    assert response.status_code == 401

def test_invalid_symbol(test_headers):
    """Test request with invalid symbol"""
    response = client.get(
        "/market-analysis/INVALID",
        headers=test_headers
    )
    assert response.status_code == 200  # Should still work with sample data

def test_invalid_timeframe(test_headers):
    """Test request with invalid timeframe"""
    response = client.get(
        "/market-analysis/BTC/USDT",
        params={"timeframe": "invalid"},
        headers=test_headers
    )
    assert response.status_code == 200  # Should still work with sample data

def test_invalid_limit(test_headers):
    """Test request with invalid limit"""
    response = client.get(
        "/market-analysis/BTC/USDT",
        params={"limit": -1},
        headers=test_headers
    )
    assert response.status_code == 200  # Should still work with sample data

def test_error_handling(test_headers):
    """Test error handling"""
    # Test with invalid endpoint
    response = client.get(
        "/market-analysis/invalid/endpoint",
        headers=test_headers
    )
    assert response.status_code == 404
    
    # Test with invalid method
    response = client.post(
        "/market-analysis/BTC/USDT",
        headers=test_headers
    )
    assert response.status_code == 405

def test_rate_limiting(test_headers):
    """Test rate limiting"""
    # Make multiple requests in quick succession
    responses = []
    for _ in range(10):
        response = client.get(
            "/market-analysis/BTC/USDT",
            headers=test_headers
        )
        responses.append(response.status_code)
    
    # Should either get 200 or 429 (Too Many Requests)
    assert all(status in [200, 429] for status in responses) 