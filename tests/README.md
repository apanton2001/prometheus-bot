# Testing Framework

This directory contains the test suites for the Prometheus Bot project.

## Features

- Unit tests for all components
- Integration tests for system-wide functionality
- Performance tests
- Mock services for external dependencies
- Continuous integration setup

## Setup

1. Install test dependencies
   ```
   pip install -r requirements-test.txt
   ```

2. Configure test environment
   ```
   cp .env.test.example .env.test
   # Edit .env.test with test configuration
   ```

## Running Tests

### Run all tests
```
pytest
```

### Run specific test modules
```
pytest tests/trading/
pytest tests/content/
pytest tests/service/
pytest tests/stock_analysis/
```

### Run tests with coverage
```
pytest --cov=prometheus_bot
```

### Generate coverage report
```
pytest --cov=prometheus_bot --cov-report=html
```

## Test Categories

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test interactions between components
- **Functional Tests**: Test end-to-end functionality
- **Performance Tests**: Test system performance and scalability

## Mock Services

The test framework includes mock implementations for external services:

- **MockExchange**: Simulates cryptocurrency exchange API
- **MockOpenAI**: Simulates OpenAI API for content generation
- **MockPaymentGateway**: Simulates payment processing
- **MockStockAPI**: Simulates financial data APIs

## Continuous Integration

Tests are automatically run on GitHub Actions for each pull request and push to main branches.

## Writing Tests

Follow these guidelines when writing tests:

1. Test files should be named `test_*.py`
2. Use descriptive test names starting with `test_`
3. Use fixtures for common test setup
4. Mock external dependencies
5. Assert specific outcomes
6. Clean up after tests

Example:
```python
def test_enhanced_ma_strategy_buy_signal():
    # Arrange
    strategy = EnhancedMAStrategy()
    data = load_test_data('btc_usdt_1h.csv')
    
    # Act
    result = strategy.analyze_buy_signal(data)
    
    # Assert
    assert result.signal == 'buy'
    assert result.confidence >= 0.75
``` 