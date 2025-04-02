import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from content.generators.trading_report import TradingReportGenerator

@pytest.fixture
def generator_config():
    return {
        'model_name': 'gpt-4',
        'temperature': 0.7,
        'max_tokens': 1000
    }

@pytest.fixture
def sample_positions():
    return {
        'BTC/USDT': {
            'action': 'buy',
            'price': 50000,
            'size': 1.0,
            'stop_loss': 49000,
            'take_profit': 52000
        },
        'ETH/USDT': {
            'action': 'sell',
            'price': 3000,
            'size': 5.0,
            'stop_loss': 3100,
            'take_profit': 2800
        }
    }

@pytest.fixture
def sample_trade_history():
    today = datetime.utcnow().date()
    return [
        {
            'symbol': 'BTC/USDT',
            'action': 'buy',
            'price': 50000,
            'size': 1.0,
            'timestamp': datetime.combine(today, datetime.min.time()),
            'stop_loss': 49000,
            'take_profit': 52000
        },
        {
            'symbol': 'BTC/USDT',
            'action': 'sell',
            'price': 51000,
            'size': 1.0,
            'timestamp': datetime.combine(today, datetime.min.time()) + timedelta(hours=1),
            'stop_loss': 52000,
            'take_profit': 49000,
            'pnl': 1000
        },
        {
            'symbol': 'ETH/USDT',
            'action': 'buy',
            'price': 3000,
            'size': 5.0,
            'timestamp': datetime.combine(today, datetime.min.time()) + timedelta(hours=2),
            'stop_loss': 2900,
            'take_profit': 3200
        }
    ]

@pytest.fixture
def sample_performance_metrics():
    return {
        'total_trades': 100,
        'winning_trades': 60,
        'losing_trades': 40,
        'win_rate': 0.6,
        'total_pnl': 5000,
        'return_pct': 5.0
    }

@pytest.fixture
def sample_market_data():
    # Generate sample market data
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
def trading_report_generator(generator_config):
    return TradingReportGenerator(generator_config)

def test_generator_initialization(trading_report_generator):
    """Test generator initialization"""
    assert trading_report_generator.config == {
        'model_name': 'gpt-4',
        'temperature': 0.7,
        'max_tokens': 1000
    }

def test_calculate_daily_metrics(trading_report_generator, sample_trade_history):
    """Test daily metrics calculation"""
    metrics = trading_report_generator._calculate_daily_metrics(sample_trade_history)
    
    assert metrics['total_trades'] == 3
    assert metrics['winning_trades'] == 1
    assert metrics['losing_trades'] == 0
    assert metrics['win_rate'] == 1/3
    assert metrics['total_pnl'] == 1000
    assert metrics['avg_pnl'] == 1000/3
    assert metrics['max_win'] == 1000
    assert metrics['max_loss'] == 0

def test_calculate_period_metrics(trading_report_generator, sample_trade_history):
    """Test period metrics calculation"""
    metrics = trading_report_generator._calculate_period_metrics(sample_trade_history)
    
    assert metrics['total_trades'] == 3
    assert metrics['winning_trades'] == 1
    assert metrics['losing_trades'] == 0
    assert metrics['win_rate'] == 1/3
    assert metrics['total_pnl'] == 1000
    assert metrics['avg_pnl'] == 1000/3
    assert metrics['max_win'] == 1000
    assert metrics['max_loss'] == 0
    assert metrics['profit_factor'] > 0
    assert isinstance(metrics['sharpe_ratio'], float)

def test_format_positions(trading_report_generator, sample_positions):
    """Test position formatting"""
    formatted = trading_report_generator._format_positions(sample_positions)
    
    assert "BTC/USDT" in formatted
    assert "ETH/USDT" in formatted
    assert "BUY" in formatted
    assert "SELL" in formatted
    assert "$50,000.00" in formatted
    assert "$3,000.00" in formatted

def test_format_trades(trading_report_generator, sample_trade_history):
    """Test trade formatting"""
    formatted = trading_report_generator._format_trades(sample_trade_history)
    
    assert "BTC/USDT" in formatted
    assert "ETH/USDT" in formatted
    assert "BUY" in formatted
    assert "SELL" in formatted
    assert "$50,000.00" in formatted
    assert "$3,000.00" in formatted
    assert "$1,000.00" in formatted

def test_format_market_data(trading_report_generator, sample_market_data):
    """Test market data formatting"""
    formatted = trading_report_generator._format_market_data(sample_market_data)
    
    assert "Current Price" in formatted
    assert "24h Change" in formatted
    assert "24h Volume" in formatted
    assert "24h High" in formatted
    assert "24h Low" in formatted

def test_format_report_prompt(trading_report_generator, sample_positions, sample_trade_history, 
                            sample_performance_metrics, sample_market_data):
    """Test daily report prompt formatting"""
    report_data = {
        'date': datetime.utcnow().date(),
        'positions': sample_positions,
        'trades': sample_trade_history,
        'daily_metrics': trading_report_generator._calculate_daily_metrics(sample_trade_history),
        'performance_metrics': sample_performance_metrics,
        'market_data': sample_market_data
    }
    
    prompt = trading_report_generator._format_report_prompt(report_data)
    
    assert "Date:" in prompt
    assert "Current Positions:" in prompt
    assert "Today's Trades:" in prompt
    assert "Daily Performance:" in prompt
    assert "Overall Performance:" in prompt
    assert "Market Analysis:" in prompt

def test_format_performance_prompt(trading_report_generator, sample_trade_history, 
                                 sample_performance_metrics, sample_market_data):
    """Test performance report prompt formatting"""
    report_data = {
        'period': 'Overall',
        'trades': sample_trade_history,
        'period_metrics': trading_report_generator._calculate_period_metrics(sample_trade_history),
        'performance_metrics': sample_performance_metrics,
        'market_data': sample_market_data
    }
    
    prompt = trading_report_generator._format_performance_prompt(report_data)
    
    assert "Period:" in prompt
    assert "Trading Statistics:" in prompt
    assert "Overall Performance:" in prompt
    assert "Market Analysis:" in prompt

def test_generate_daily_report(trading_report_generator, sample_positions, sample_trade_history,
                             sample_performance_metrics, sample_market_data):
    """Test daily report generation"""
    report = trading_report_generator.generate_daily_report(
        positions=sample_positions,
        trade_history=sample_trade_history,
        performance_metrics=sample_performance_metrics,
        market_data=sample_market_data
    )
    
    assert isinstance(report, str)
    assert len(report) > 0

def test_generate_performance_report(trading_report_generator, sample_trade_history,
                                   sample_performance_metrics, sample_market_data):
    """Test performance report generation"""
    report = trading_report_generator.generate_performance_report(
        trade_history=sample_trade_history,
        performance_metrics=sample_performance_metrics,
        market_data=sample_market_data
    )
    
    assert isinstance(report, str)
    assert len(report) > 0

def test_empty_data_handling(trading_report_generator):
    """Test handling of empty data"""
    # Test with empty positions
    positions = {}
    trade_history = []
    performance_metrics = {
        'total_trades': 0,
        'winning_trades': 0,
        'losing_trades': 0,
        'win_rate': 0,
        'total_pnl': 0,
        'return_pct': 0
    }
    
    # Generate reports with empty data
    daily_report = trading_report_generator.generate_daily_report(
        positions=positions,
        trade_history=trade_history,
        performance_metrics=performance_metrics
    )
    
    performance_report = trading_report_generator.generate_performance_report(
        trade_history=trade_history,
        performance_metrics=performance_metrics
    )
    
    assert isinstance(daily_report, str)
    assert len(daily_report) > 0
    assert isinstance(performance_report, str)
    assert len(performance_report) > 0 