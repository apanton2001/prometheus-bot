import pytest
from fastapi.testclient import TestClient
from datetime import datetime
from api.main import app

client = TestClient(app)

def test_health_check():
    """
    Test health check endpoint.
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert data["version"] == "1.0.0"

def test_get_trading_strategies(test_headers):
    """
    Test getting trading strategies.
    
    Args:
        test_headers (dict): Test request headers
    """
    response = client.get("/api/v1/trading/strategies", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_get_positions(test_headers):
    """
    Test getting trading positions.
    
    Args:
        test_headers (dict): Test request headers
    """
    response = client.get("/api/v1/trading/positions", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_generate_content(test_headers, mock_content_data):
    """
    Test content generation endpoint.
    
    Args:
        test_headers (dict): Test request headers
        mock_content_data (dict): Mock content data
    """
    response = client.post(
        "/api/v1/content/generate",
        headers=test_headers,
        json=mock_content_data
    )
    assert response.status_code == 200
    data = response.json()
    assert "content" in data
    assert isinstance(data["content"], str)
    assert len(data["content"]) > 0

def test_get_services(test_headers):
    """
    Test getting available services.
    
    Args:
        test_headers (dict): Test request headers
    """
    response = client.get("/api/v1/services", headers=test_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

def test_unauthorized_access():
    """
    Test unauthorized access to protected endpoints.
    """
    # Test without authentication
    response = client.get("/api/v1/trading/positions")
    assert response.status_code == 401
    
    response = client.post("/api/v1/content/generate", json={"prompt": "test"})
    assert response.status_code == 401
    
    response = client.get("/api/v1/services")
    assert response.status_code == 401

def test_invalid_content_generation(test_headers):
    """
    Test content generation with invalid data.
    
    Args:
        test_headers (dict): Test request headers
    """
    # Test with missing prompt
    response = client.post(
        "/api/v1/content/generate",
        headers=test_headers,
        json={"context": {"test": "data"}}
    )
    assert response.status_code == 422
    
    # Test with invalid context
    response = client.post(
        "/api/v1/content/generate",
        headers=test_headers,
        json={"prompt": "test", "context": "invalid"}
    )
    assert response.status_code == 422

def test_error_handling(test_headers):
    """
    Test API error handling.
    
    Args:
        test_headers (dict): Test request headers
    """
    # Test with invalid endpoint
    response = client.get("/api/v1/invalid", headers=test_headers)
    assert response.status_code == 404
    
    # Test with invalid method
    response = client.post("/api/v1/trading/positions", headers=test_headers)
    assert response.status_code == 405

def test_rate_limiting(test_headers):
    """
    Test API rate limiting.
    
    Args:
        test_headers (dict): Test request headers
    """
    # Make multiple requests in quick succession
    for _ in range(10):
        response = client.get("/api/v1/trading/strategies", headers=test_headers)
        assert response.status_code in [200, 429]  # Either success or rate limit 