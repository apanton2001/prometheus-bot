import os
import sys
import pytest
import pandas as pd
import numpy as np
from pathlib import Path

# Add the project root to path so we can import the strategy
sys.path.append(str(Path(__file__).resolve().parent.parent))

# Import the strategy to test
from trading.strategies.momentum_strategy import MomentumStrategy

class TestMomentumStrategy:
    """
    Tests for the MomentumStrategy.
    """
    
    @pytest.fixture
    def strategy(self):
        """Create a strategy instance for testing."""
        return MomentumStrategy()
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        # Create a sample DataFrame with OHLCV data
        dates = pd.date_range(start='2020-01-01', periods=100, freq='5min')
        
        # Generate some random price data with a slight upward trend
        np.random.seed(42)  # For reproducibility
        
        close = np.random.normal(loc=100, scale=1, size=100).cumsum()
        open_prices = close - np.random.normal(loc=0, scale=0.5, size=100)
        high = np.maximum(close, open_prices) + np.random.normal(loc=0.5, scale=0.5, size=100)
        low = np.minimum(close, open_prices) - np.random.normal(loc=0.5, scale=0.5, size=100)
        volume = np.random.normal(loc=1000, scale=200, size=100).astype(int)
        
        # Create the DataFrame
        df = pd.DataFrame({
            'date': dates,
            'open': open_prices,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
        
        return df
    
    def test_populate_indicators(self, strategy, sample_data):
        """Test that indicators are correctly populated."""
        # Populate the indicators
        df = strategy.populate_indicators(sample_data, {})
        
        # Check that the expected indicators exist
        assert 'rsi' in df.columns
        assert 'ema9' in df.columns
        assert 'ema21' in df.columns
        assert 'ema50' in df.columns
        assert 'macd' in df.columns
        assert 'macdsignal' in df.columns
        assert 'macdhist' in df.columns
        assert 'volume_mean_12' in df.columns
        
        # Check that there are no NaN values in the indicators after the startup period
        startup_period = max(50, strategy.startup_candle_count)
        for col in ['rsi', 'ema9', 'ema21', 'ema50', 'macd', 'macdsignal', 'macdhist', 'volume_mean_12']:
            assert not df.iloc[startup_period:][col].isna().any()
    
    def test_buy_signals(self, strategy, sample_data):
        """Test that buy signals are generated correctly."""
        # Populate indicators
        df = strategy.populate_indicators(sample_data, {})
        
        # Create a situation where we expect a buy signal
        # (RSI < 30, macdhist > 0, ema9 > ema21, volume > volume_mean_12)
        df.loc[50, 'rsi'] = 25  # Oversold
        df.loc[50, 'macdhist'] = 0.1  # MACD rising
        df.loc[50, 'ema9'] = 110  # EMA9 above EMA21
        df.loc[50, 'ema21'] = 105
        df.loc[50, 'volume'] = 1500  # Volume above average
        df.loc[50, 'volume_mean_12'] = 1000
        
        # Populate buy trend
        df = strategy.populate_buy_trend(df, {})
        
        # Check that a buy signal was generated
        assert df.loc[50, 'buy'] == 1
        
        # Create a situation where we do not expect a buy signal
        df.loc[60, 'rsi'] = 35  # Not oversold
        df.loc[60, 'macdhist'] = 0.1  # MACD rising
        df.loc[60, 'ema9'] = 110  # EMA9 above EMA21
        df.loc[60, 'ema21'] = 105
        df.loc[60, 'volume'] = 1500  # Volume above average
        df.loc[60, 'volume_mean_12'] = 1000
        
        # Check that no buy signal was generated (should still be the default value, which is 0 or NaN)
        assert df.loc[60, 'buy'] != 1
    
    def test_sell_signals(self, strategy, sample_data):
        """Test that sell signals are generated correctly."""
        # Populate indicators
        df = strategy.populate_indicators(sample_data, {})
        
        # Create a situation where we expect a sell signal
        # (RSI > 70, macdhist < 0, ema9 < ema21)
        df.loc[70, 'rsi'] = 75  # Overbought
        df.loc[70, 'macdhist'] = -0.1  # MACD falling
        df.loc[70, 'ema9'] = 100  # EMA9 below EMA21
        df.loc[70, 'ema21'] = 105
        
        # Populate sell trend
        df = strategy.populate_sell_trend(df, {})
        
        # Check that a sell signal was generated
        assert df.loc[70, 'sell'] == 1
        
        # Create a situation where we do not expect a sell signal
        df.loc[80, 'rsi'] = 65  # Not overbought
        df.loc[80, 'macdhist'] = -0.1  # MACD falling
        df.loc[80, 'ema9'] = 100  # EMA9 below EMA21
        df.loc[80, 'ema21'] = 105
        
        # Check that no sell signal was generated (should still be the default value, which is 0 or NaN)
        assert df.loc[80, 'sell'] != 1 