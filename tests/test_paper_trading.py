import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from trading.paper_trading import PaperTrading
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
    # Generate sample market data with a clear trend
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
    
    # Ensure OHLCV relationships are valid
    data['high'] = data[['open', 'close']].max(axis=1) + abs(np.random.normal(0, 100, 100))
    data['low'] = data[['open', 'close']].min(axis=1) - abs(np.random.normal(0, 100, 100))
    data['volume'] = abs(data['volume'])
    
    return data

@pytest.fixture
def paper_trading(strategy_config):
    strategy = MomentumStrategy(strategy_config)
    return PaperTrading(initial_balance=100000, strategy=strategy)

def test_initialization(paper_trading):
    """Test paper trading initialization"""
    assert paper_trading.initial_balance == 100000
    assert paper_trading.current_balance == 100000
    assert len(paper_trading.positions) == 0
    assert len(paper_trading.trade_history) == 0
    assert paper_trading.max_positions == 5

def test_update_market_data(paper_trading, sample_market_data):
    """Test market data update and signal generation"""
    signal = paper_trading.update_market_data('BTC/USDT', sample_market_data)
    
    # Signal should be either None or a dict with required fields
    assert signal is None or isinstance(signal, dict)
    if signal:
        required_fields = ['symbol', 'action', 'price', 'size', 'timestamp', 'stop_loss', 'take_profit']
        assert all(field in signal for field in required_fields)
        assert signal['symbol'] == 'BTC/USDT'
        assert signal['action'] in ['buy', 'sell']
        assert signal['price'] > 0
        assert signal['size'] > 0

def test_execute_trade(paper_trading):
    """Test trade execution"""
    # Create a buy signal
    buy_signal = {
        'action': 'buy',
        'price': 50000,
        'size': 1.0,
        'stop_loss': 49000,
        'take_profit': 52000
    }
    
    # Execute buy trade
    trade = paper_trading._execute_trade('BTC/USDT', buy_signal)
    assert trade is not None
    assert trade['action'] == 'buy'
    assert trade['price'] == 50000
    assert trade['size'] == 1.0
    assert 'BTC/USDT' in paper_trading.positions
    
    # Create a sell signal
    sell_signal = {
        'action': 'sell',
        'price': 51000,
        'size': 1.0,
        'stop_loss': 52000,
        'take_profit': 49000
    }
    
    # Execute sell trade
    trade = paper_trading._execute_trade('BTC/USDT', sell_signal)
    assert trade is not None
    assert trade['action'] == 'sell'
    assert trade['price'] == 51000
    assert trade['size'] == 1.0
    assert 'pnl' in trade
    assert 'BTC/USDT' not in paper_trading.positions

def test_check_positions(paper_trading):
    """Test position checking"""
    # Open a buy position
    buy_signal = {
        'action': 'buy',
        'price': 50000,
        'size': 1.0,
        'stop_loss': 49000,
        'take_profit': 52000
    }
    paper_trading._execute_trade('BTC/USDT', buy_signal)
    
    # Test stop-loss hit
    closed_positions = paper_trading.check_positions('BTC/USDT', 48000)
    assert len(closed_positions) == 1
    assert closed_positions[0]['reason'] == 'stop_loss'
    assert closed_positions[0]['pnl'] < 0
    
    # Open another buy position
    paper_trading._execute_trade('BTC/USDT', buy_signal)
    
    # Test take-profit hit
    closed_positions = paper_trading.check_positions('BTC/USDT', 53000)
    assert len(closed_positions) == 1
    assert closed_positions[0]['reason'] == 'take_profit'
    assert closed_positions[0]['pnl'] > 0

def test_get_position(paper_trading):
    """Test position retrieval"""
    # Open a position
    buy_signal = {
        'action': 'buy',
        'price': 50000,
        'size': 1.0,
        'stop_loss': 49000,
        'take_profit': 52000
    }
    paper_trading._execute_trade('BTC/USDT', buy_signal)
    
    # Get position
    position = paper_trading.get_position('BTC/USDT')
    assert position is not None
    assert position['action'] == 'buy'
    assert position['price'] == 50000
    
    # Get non-existent position
    position = paper_trading.get_position('ETH/USDT')
    assert position is None

def test_get_all_positions(paper_trading):
    """Test getting all positions"""
    # Open multiple positions
    buy_signal = {
        'action': 'buy',
        'price': 50000,
        'size': 1.0,
        'stop_loss': 49000,
        'take_profit': 52000
    }
    
    paper_trading._execute_trade('BTC/USDT', buy_signal)
    paper_trading._execute_trade('ETH/USDT', buy_signal)
    
    positions = paper_trading.get_all_positions()
    assert len(positions) == 2
    assert 'BTC/USDT' in positions
    assert 'ETH/USDT' in positions

def test_get_trade_history(paper_trading):
    """Test trade history retrieval"""
    # Execute some trades
    buy_signal = {
        'action': 'buy',
        'price': 50000,
        'size': 1.0,
        'stop_loss': 49000,
        'take_profit': 52000
    }
    
    paper_trading._execute_trade('BTC/USDT', buy_signal)
    paper_trading._execute_trade('BTC/USDT', {
        'action': 'sell',
        'price': 51000,
        'size': 1.0,
        'stop_loss': 52000,
        'take_profit': 49000
    })
    
    history = paper_trading.get_trade_history()
    assert len(history) == 2
    assert history[0]['action'] == 'buy'
    assert history[1]['action'] == 'sell'

def test_get_balance(paper_trading):
    """Test balance tracking"""
    initial_balance = paper_trading.get_balance()
    
    # Execute a profitable trade
    buy_signal = {
        'action': 'buy',
        'price': 50000,
        'size': 1.0,
        'stop_loss': 49000,
        'take_profit': 52000
    }
    paper_trading._execute_trade('BTC/USDT', buy_signal)
    
    # Check balance after buy
    balance_after_buy = paper_trading.get_balance()
    assert balance_after_buy < initial_balance
    
    # Execute sell at profit
    paper_trading._execute_trade('BTC/USDT', {
        'action': 'sell',
        'price': 51000,
        'size': 1.0,
        'stop_loss': 52000,
        'take_profit': 49000
    })
    
    # Check balance after sell
    balance_after_sell = paper_trading.get_balance()
    assert balance_after_sell > balance_after_buy

def test_get_performance_metrics(paper_trading):
    """Test performance metrics calculation"""
    # Execute some trades
    buy_signal = {
        'action': 'buy',
        'price': 50000,
        'size': 1.0,
        'stop_loss': 49000,
        'take_profit': 52000
    }
    
    # Execute profitable trade
    paper_trading._execute_trade('BTC/USDT', buy_signal)
    paper_trading._execute_trade('BTC/USDT', {
        'action': 'sell',
        'price': 51000,
        'size': 1.0,
        'stop_loss': 52000,
        'take_profit': 49000
    })
    
    # Execute losing trade
    paper_trading._execute_trade('ETH/USDT', buy_signal)
    paper_trading._execute_trade('ETH/USDT', {
        'action': 'sell',
        'price': 49000,
        'size': 1.0,
        'stop_loss': 52000,
        'take_profit': 49000
    })
    
    metrics = paper_trading.get_performance_metrics()
    assert metrics['total_trades'] == 4
    assert metrics['winning_trades'] == 1
    assert metrics['losing_trades'] == 1
    assert 0 <= metrics['win_rate'] <= 1
    assert metrics['total_pnl'] != 0
    assert metrics['return_pct'] != 0 