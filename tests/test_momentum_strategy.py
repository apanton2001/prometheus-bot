import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from trading.strategies.momentum_strategy import MomentumStrategy

@pytest.fixture
def strategy_config():
    return {
        'fast_ma_period': 10,
        'slow_ma_period': 30,
        'rsi_period': 14,
        'rsi_overbought': 70,
        'rsi_oversold': 30,
        'stop_loss_pct': 0.02,
        'take_profit_pct': 0.04,
        'risk_percentage': 0.01,
        'max_position_size': 0.1
    }

@pytest.fixture
def sample_market_data():
    # Generate sample market data
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    np.random.seed(42)
    
    data = pd.DataFrame({
        'open': np.random.normal(50000, 1000, 100),
        'high': np.random.normal(50100, 1000, 100),
        'low': np.random.normal(49900, 1000, 100),
        'close': np.random.normal(50000, 1000, 100),
        'volume': np.random.normal(100, 20, 100)
    }, index=dates)
    
    # Ensure OHLCV relationships are valid
    data['high'] = data[['open', 'close']].max(axis=1) + abs(np.random.normal(0, 100, 100))
    data['low'] = data[['open', 'close']].min(axis=1) - abs(np.random.normal(0, 100, 100))
    data['volume'] = abs(data['volume'])
    
    return data

def test_strategy_initialization(strategy_config):
    """Test strategy initialization with config"""
    strategy = MomentumStrategy(strategy_config)
    
    assert strategy.fast_ma_period == strategy_config['fast_ma_period']
    assert strategy.slow_ma_period == strategy_config['slow_ma_period']
    assert strategy.rsi_period == strategy_config['rsi_period']
    assert strategy.rsi_overbought == strategy_config['rsi_overbought']
    assert strategy.rsi_oversold == strategy_config['rsi_oversold']
    assert strategy.stop_loss_pct == strategy_config['stop_loss_pct']
    assert strategy.take_profit_pct == strategy_config['take_profit_pct']

def test_generate_signals(strategy_config, sample_market_data):
    """Test signal generation"""
    strategy = MomentumStrategy(strategy_config)
    signal = strategy.generate_signals(sample_market_data)
    
    # Signal should be either None or a dict with required fields
    assert signal is None or isinstance(signal, dict)
    if signal:
        required_fields = ['action', 'price', 'size', 'confidence', 'timestamp', 'stop_loss', 'take_profit']
        assert all(field in signal for field in required_fields)
        assert signal['action'] in ['buy', 'sell']
        assert signal['price'] > 0
        assert 0 <= signal['confidence'] <= 1

def test_calculate_position_size(strategy_config):
    """Test position size calculation"""
    strategy = MomentumStrategy(strategy_config)
    
    # Test buy signal
    buy_signal = {
        'action': 'buy',
        'price': 50000,
        'stop_loss': 49000,
        'take_profit': 52000
    }
    
    position_size = strategy.calculate_position_size(buy_signal, 100000)
    assert position_size > 0
    assert position_size <= 100000 * strategy_config['max_position_size']
    
    # Test sell signal
    sell_signal = {
        'action': 'sell',
        'price': 50000,
        'stop_loss': 51000,
        'take_profit': 48000
    }
    
    position_size = strategy.calculate_position_size(sell_signal, 100000)
    assert position_size > 0
    assert position_size <= 100000 * strategy_config['max_position_size']

def test_validate_signal(strategy_config):
    """Test signal validation"""
    strategy = MomentumStrategy(strategy_config)
    
    # Valid buy signal
    valid_buy_signal = {
        'action': 'buy',
        'price': 50000,
        'size': 1.0,
        'confidence': 0.8,
        'timestamp': datetime.utcnow(),
        'stop_loss': 49000,
        'take_profit': 52000
    }
    assert strategy.validate_signal(valid_buy_signal)
    
    # Valid sell signal
    valid_sell_signal = {
        'action': 'sell',
        'price': 50000,
        'size': 1.0,
        'confidence': 0.8,
        'timestamp': datetime.utcnow(),
        'stop_loss': 51000,
        'take_profit': 48000
    }
    assert strategy.validate_signal(valid_sell_signal)
    
    # Invalid signals
    invalid_signals = [
        None,  # None signal
        {},  # Empty dict
        {'action': 'invalid'},  # Invalid action
        {'action': 'buy', 'price': 0},  # Invalid price
        {'action': 'buy', 'price': 50000, 'size': 0},  # Invalid size
        {'action': 'buy', 'price': 50000, 'size': 1.0, 'confidence': 1.5},  # Invalid confidence
        {'action': 'buy', 'price': 50000, 'size': 1.0, 'confidence': 0.8, 'stop_loss': 51000, 'take_profit': 49000}  # Invalid SL/TP
    ]
    
    for signal in invalid_signals:
        assert not strategy.validate_signal(signal)

def test_signal_generation_with_trend(strategy_config):
    """Test signal generation with a clear trend"""
    # Create data with a clear uptrend
    dates = pd.date_range(start='2024-01-01', periods=100, freq='1H')
    trend = np.linspace(50000, 55000, 100)
    noise = np.random.normal(0, 100, 100)
    
    data = pd.DataFrame({
        'open': trend + noise,
        'high': trend + noise + abs(np.random.normal(0, 100, 100)),
        'low': trend + noise - abs(np.random.normal(0, 100, 100)),
        'close': trend + noise,
        'volume': np.random.normal(100, 20, 100)
    }, index=dates)
    
    strategy = MomentumStrategy(strategy_config)
    signal = strategy.generate_signals(data)
    
    # Should generate a buy signal in uptrend
    assert signal is not None
    assert signal['action'] == 'buy'
    assert signal['price'] > 0
    assert signal['stop_loss'] < signal['price']
    assert signal['take_profit'] > signal['price'] 