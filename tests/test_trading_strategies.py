import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from trading.strategies.base_strategy import BaseStrategy

class TestStrategy(BaseStrategy):
    """
    Test implementation of BaseStrategy for testing purposes.
    """
    
    def generate_signals(self, data: pd.DataFrame) -> dict:
        """Generate test signals."""
        return {
            "action": "buy",
            "price": data["close"].iloc[-1],
            "size": 1.0,
            "confidence": 0.8,
            "timestamp": datetime.utcnow()
        }
    
    def calculate_position_size(self, signal: dict, account_balance: float) -> float:
        """Calculate test position size."""
        return account_balance * 0.1
    
    def validate_signal(self, signal: dict) -> bool:
        """Validate test signals."""
        return True

@pytest.fixture
def sample_market_data() -> pd.DataFrame:
    """
    Create sample market data for testing.
    
    Returns:
        pd.DataFrame: Sample OHLCV data
    """
    dates = pd.date_range(start="2023-01-01", periods=100, freq="1H")
    data = pd.DataFrame({
        "open": np.random.normal(50000, 1000, 100),
        "high": np.random.normal(51000, 1000, 100),
        "low": np.random.normal(49000, 1000, 100),
        "close": np.random.normal(50500, 1000, 100),
        "volume": np.random.normal(100, 20, 100)
    }, index=dates)
    return data

@pytest.fixture
def strategy_config() -> dict:
    """
    Create test strategy configuration.
    
    Returns:
        dict: Strategy configuration
    """
    return {
        "name": "test_strategy",
        "timeframe": "1h",
        "risk_percentage": 1.0,
        "max_positions": 3
    }

def test_strategy_initialization(strategy_config):
    """
    Test strategy initialization.
    
    Args:
        strategy_config (dict): Strategy configuration
    """
    strategy = TestStrategy(strategy_config)
    assert strategy.config == strategy_config
    assert strategy.position is None
    assert strategy.last_signal is None
    assert strategy.last_update is None

def test_generate_signals(strategy_config, sample_market_data):
    """
    Test signal generation.
    
    Args:
        strategy_config (dict): Strategy configuration
        sample_market_data (pd.DataFrame): Sample market data
    """
    strategy = TestStrategy(strategy_config)
    signal = strategy.generate_signals(sample_market_data)
    
    assert isinstance(signal, dict)
    assert "action" in signal
    assert "price" in signal
    assert "size" in signal
    assert "confidence" in signal
    assert "timestamp" in signal

def test_calculate_position_size(strategy_config):
    """
    Test position size calculation.
    
    Args:
        strategy_config (dict): Strategy configuration
    """
    strategy = TestStrategy(strategy_config)
    signal = {
        "action": "buy",
        "price": 50000.0,
        "size": 1.0,
        "confidence": 0.8,
        "timestamp": datetime.utcnow()
    }
    
    position_size = strategy.calculate_position_size(signal, 10000.0)
    assert position_size == 1000.0  # 10% of account balance

def test_validate_signal(strategy_config):
    """
    Test signal validation.
    
    Args:
        strategy_config (dict): Strategy configuration
    """
    strategy = TestStrategy(strategy_config)
    signal = {
        "action": "buy",
        "price": 50000.0,
        "size": 1.0,
        "confidence": 0.8,
        "timestamp": datetime.utcnow()
    }
    
    assert strategy.validate_signal(signal) is True

def test_update_method(strategy_config, sample_market_data):
    """
    Test strategy update method.
    
    Args:
        strategy_config (dict): Strategy configuration
        sample_market_data (pd.DataFrame): Sample market data
    """
    strategy = TestStrategy(strategy_config)
    signal = strategy.update(sample_market_data)
    
    assert signal is not None
    assert strategy.last_signal == signal
    assert strategy.last_update is not None

def test_position_management(strategy_config):
    """
    Test position management methods.
    
    Args:
        strategy_config (dict): Strategy configuration
    """
    strategy = TestStrategy(strategy_config)
    position = {
        "symbol": "BTC/USDT",
        "size": 1.0,
        "entry_price": 50000.0,
        "timestamp": datetime.utcnow()
    }
    
    strategy.set_position(position)
    assert strategy.get_position() == position

def test_metrics(strategy_config):
    """
    Test strategy metrics.
    
    Args:
        strategy_config (dict): Strategy configuration
    """
    strategy = TestStrategy(strategy_config)
    metrics = strategy.get_metrics()
    
    assert isinstance(metrics, dict)
    assert "total_trades" in metrics
    assert "winning_trades" in metrics
    assert "losing_trades" in metrics
    assert "win_rate" in metrics
    assert "profit_factor" in metrics
    assert "max_drawdown" in metrics 