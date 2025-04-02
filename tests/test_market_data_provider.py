import pytest
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
from ...data.provider import MarketDataProvider

@pytest.fixture
def mock_exchange():
    """Create a mock exchange for testing."""
    with patch('ccxt.binance') as mock:
        # Configure mock exchange
        exchange = Mock()
        exchange.id = 'binance'
        exchange.name = 'Binance'
        exchange.version = '1.0.0'
        exchange.timeframes = {'1h': 3600, '1d': 86400}
        exchange.has = {'fetchOHLCV': True, 'fetchTicker': True}
        exchange.rateLimit = 1000
        exchange.urls = {'api': {'public': 'https://api.binance.com/api/v3'}}
        exchange.markets = {
            'BTC/USDT': {'id': 'BTCUSDT', 'symbol': 'BTC/USDT'},
            'ETH/USDT': {'id': 'ETHUSDT', 'symbol': 'ETH/USDT'}
        }
        
        # Configure mock methods
        exchange.fetch_ohlcv.return_value = [
            [1625097600000, 35000, 35100, 34900, 35050, 100],
            [1625097900000, 35050, 35200, 35000, 35150, 150]
        ]
        
        exchange.fetch_ticker.return_value = {
            'symbol': 'BTC/USDT',
            'last': 35000,
            'bid': 34950,
            'ask': 35050,
            'baseVolume': 1000,
            'timestamp': 1625097600000
        }
        
        exchange.fetch_order_book.return_value = {
            'bids': [[34950, 1], [34900, 2]],
            'asks': [[35050, 1], [35100, 2]],
            'timestamp': 1625097600000
        }
        
        exchange.fetch_trades.return_value = [
            {
                'id': '123',
                'timestamp': 1625097600000,
                'price': 35000,
                'amount': 0.1,
                'side': 'buy',
                'cost': 3500
            }
        ]
        
        mock.return_value = exchange
        yield exchange

@pytest.fixture
def provider(mock_exchange):
    """Create a market data provider instance."""
    return MarketDataProvider(exchange_id='binance')

def test_initialization(provider):
    """Test provider initialization."""
    assert provider.exchange is not None
    assert provider._cache == {}
    assert provider._cache_timestamps == {}
    assert provider._cache_duration == timedelta(minutes=5)

def test_get_ohlcv(provider):
    """Test fetching OHLCV data."""
    # Test without cache
    df = provider.get_ohlcv('BTC/USDT', timeframe='1h')
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume'])
    assert isinstance(df.index, pd.DatetimeIndex)
    
    # Test with cache
    df_cached = provider.get_ohlcv('BTC/USDT', timeframe='1h')
    assert isinstance(df_cached, pd.DataFrame)
    assert len(df_cached) == 2
    
    # Test with different timeframe
    df_daily = provider.get_ohlcv('BTC/USDT', timeframe='1d')
    assert isinstance(df_daily, pd.DataFrame)
    assert len(df_daily) == 2

def test_get_ticker(provider):
    """Test fetching ticker data."""
    ticker = provider.get_ticker('BTC/USDT')
    assert isinstance(ticker, dict)
    assert all(key in ticker for key in ['symbol', 'last', 'bid', 'ask', 'volume', 'timestamp'])
    assert isinstance(ticker['timestamp'], datetime)

def test_get_orderbook(provider):
    """Test fetching order book data."""
    orderbook = provider.get_orderbook('BTC/USDT')
    assert isinstance(orderbook, dict)
    assert all(key in orderbook for key in ['symbol', 'bids', 'asks', 'timestamp'])
    assert isinstance(orderbook['timestamp'], datetime)
    assert len(orderbook['bids']) == 2
    assert len(orderbook['asks']) == 2

def test_get_recent_trades(provider):
    """Test fetching recent trades."""
    trades = provider.get_recent_trades('BTC/USDT')
    assert isinstance(trades, list)
    assert len(trades) == 1
    assert all(key in trades[0] for key in ['id', 'timestamp', 'price', 'amount', 'side', 'cost'])
    assert isinstance(trades[0]['timestamp'], datetime)

def test_get_symbols(provider):
    """Test fetching available symbols."""
    symbols = provider.get_symbols()
    assert isinstance(symbols, list)
    assert len(symbols) == 2
    assert all(symbol in symbols for symbol in ['BTC/USDT', 'ETH/USDT'])

def test_cache_validation(provider):
    """Test cache validation."""
    # Add data to cache
    provider._cache['test_key'] = pd.DataFrame()
    provider._cache_timestamps['test_key'] = datetime.utcnow()
    
    # Test valid cache
    assert provider._is_cache_valid('test_key')
    
    # Test expired cache
    provider._cache_timestamps['test_key'] = datetime.utcnow() - timedelta(minutes=6)
    assert not provider._is_cache_valid('test_key')
    
    # Test non-existent cache
    assert not provider._is_cache_valid('non_existent')

def test_clear_cache(provider):
    """Test clearing cache."""
    # Add data to cache
    provider._cache['test_key'] = pd.DataFrame()
    provider._cache_timestamps['test_key'] = datetime.utcnow()
    
    # Clear cache
    provider.clear_cache()
    
    assert provider._cache == {}
    assert provider._cache_timestamps == {}

def test_get_exchange_info(provider):
    """Test fetching exchange information."""
    info = provider.get_exchange_info()
    assert isinstance(info, dict)
    assert all(key in info for key in ['id', 'name', 'version', 'timeframes', 'has', 'rateLimit', 'urls'])
    assert info['id'] == 'binance'
    assert info['name'] == 'Binance'

def test_error_handling(provider, mock_exchange):
    """Test error handling."""
    # Test OHLCV error
    mock_exchange.fetch_ohlcv.side_effect = Exception("API Error")
    with pytest.raises(Exception):
        provider.get_ohlcv('BTC/USDT')
    
    # Test ticker error
    mock_exchange.fetch_ticker.side_effect = Exception("API Error")
    with pytest.raises(Exception):
        provider.get_ticker('BTC/USDT')
    
    # Test orderbook error
    mock_exchange.fetch_order_book.side_effect = Exception("API Error")
    with pytest.raises(Exception):
        provider.get_orderbook('BTC/USDT')
    
    # Test trades error
    mock_exchange.fetch_trades.side_effect = Exception("API Error")
    with pytest.raises(Exception):
        provider.get_recent_trades('BTC/USDT')
    
    # Test symbols error
    mock_exchange.markets = None
    with pytest.raises(Exception):
        provider.get_symbols()

def test_data_formatting(provider):
    """Test data formatting."""
    # Test OHLCV formatting
    df = provider.get_ohlcv('BTC/USDT')
    assert isinstance(df.index, pd.DatetimeIndex)
    assert all(isinstance(df[col].iloc[0], (int, float)) for col in ['open', 'high', 'low', 'close', 'volume'])
    
    # Test ticker formatting
    ticker = provider.get_ticker('BTC/USDT')
    assert isinstance(ticker['last'], (int, float))
    assert isinstance(ticker['volume'], (int, float))
    
    # Test orderbook formatting
    orderbook = provider.get_orderbook('BTC/USDT')
    assert all(isinstance(price, (int, float)) for price, _ in orderbook['bids'])
    assert all(isinstance(amount, (int, float)) for _, amount in orderbook['bids'])
    
    # Test trades formatting
    trades = provider.get_recent_trades('BTC/USDT')
    assert all(isinstance(trade['price'], (int, float)) for trade in trades)
    assert all(isinstance(trade['amount'], (int, float)) for trade in trades) 