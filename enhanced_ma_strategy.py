import pandas as pd
import numpy as np
import talib

class EnhancedMAStrategy:
    def __init__(self):
        # Moving Average periods
        self.fast_ma_period = 9
        self.medium_ma_period = 21
        self.slow_ma_period = 50
        
        # ADX settings for trend strength
        self.adx_period = 14
        self.adx_threshold = 25  # Minimum ADX value for strong trend
        
        # Volume settings
        self.volume_ma_period = 20
        self.volume_factor = 1.5  # Volume should be this times the average
        
        # Volatility settings for position sizing
        self.atr_period = 14
        self.risk_per_trade = 0.02  # 2% risk per trade
        
        # Risk management
        self.max_drawdown = 0.15  # 15% max drawdown allowed
        self.trailing_stop_pct = 0.02  # 2% trailing stop
        
    def populate_indicators(self, dataframe, metadata=None):
        # Moving Averages
        dataframe['fast_ma'] = talib.EMA(dataframe['close'], timeperiod=self.fast_ma_period)
        dataframe['medium_ma'] = talib.EMA(dataframe['close'], timeperiod=self.medium_ma_period)
        dataframe['slow_ma'] = talib.EMA(dataframe['close'], timeperiod=self.slow_ma_period)
        
        # ADX for trend strength
        dataframe['adx'] = talib.ADX(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=self.adx_period)
        
        # Volume indicators
        dataframe['volume_ma'] = talib.SMA(dataframe['volume'], timeperiod=self.volume_ma_period)
        dataframe['volume_ratio'] = dataframe['volume'] / dataframe['volume_ma']
        
        # ATR for volatility measurement and position sizing
        dataframe['atr'] = talib.ATR(dataframe['high'], dataframe['low'], dataframe['close'], timeperiod=self.atr_period)
        
        # RSI for additional confirmation
        dataframe['rsi'] = talib.RSI(dataframe['close'], timeperiod=14)
        
        # MACD for additional confirmation
        macd = talib.MACD(dataframe['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd[0]
        dataframe['macdsignal'] = macd[1]
        dataframe['macdhist'] = macd[2]
        
        # Bollinger Bands for volatility and potential reversal points
        upperband, middleband, lowerband = talib.BBANDS(dataframe['close'], timeperiod=20, nbdevup=2, nbdevdn=2)
        dataframe['bb_upper'] = upperband
        dataframe['bb_middle'] = middleband
        dataframe['bb_lower'] = lowerband
        
        return dataframe
    
    def populate_entry_trend(self, dataframe, metadata=None):
        dataframe['enter_long'] = 0
        dataframe['enter_short'] = 0
        
        # Long entry conditions
        long_conditions = (
            # Moving Average Crossover: fast MA crosses above medium MA
            (dataframe['fast_ma'] > dataframe['medium_ma']) &
            # Trend confirmation: medium MA above slow MA
            (dataframe['medium_ma'] > dataframe['slow_ma']) &
            # Strong trend filter
            (dataframe['adx'] > self.adx_threshold) &
            # Volume confirmation
            (dataframe['volume_ratio'] > self.volume_factor) &
            # Additional RSI Filter: avoid overbought
            (dataframe['rsi'] < 70) &
            # MACD confirming uptrend
            (dataframe['macdhist'] > 0) &
            # Price is above the middle Bollinger Band
            (dataframe['close'] > dataframe['bb_middle'])
        )
        
        # Short entry conditions for futures trading (if applicable)
        short_conditions = (
            # Moving Average Crossover: fast MA crosses below medium MA
            (dataframe['fast_ma'] < dataframe['medium_ma']) &
            # Trend confirmation: medium MA below slow MA
            (dataframe['medium_ma'] < dataframe['slow_ma']) &
            # Strong trend filter
            (dataframe['adx'] > self.adx_threshold) &
            # Volume confirmation
            (dataframe['volume_ratio'] > self.volume_factor) &
            # Additional RSI Filter: avoid oversold
            (dataframe['rsi'] > 30) &
            # MACD confirming downtrend
            (dataframe['macdhist'] < 0) &
            # Price is below the middle Bollinger Band
            (dataframe['close'] < dataframe['bb_middle'])
        )
        
        # Set entry signals
        dataframe.loc[long_conditions, 'enter_long'] = 1
        dataframe.loc[short_conditions, 'enter_short'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe, metadata=None):
        dataframe['exit_long'] = 0
        dataframe['exit_short'] = 0
        
        # Long exit conditions
        long_exit_conditions = (
            # Moving Average Crossover: fast MA crosses below medium MA
            (dataframe['fast_ma'] < dataframe['medium_ma']) |
            # RSI overbought
            (dataframe['rsi'] > 80) |
            # MACD crossover to negative
            ((dataframe['macdhist'] < 0) & (dataframe['macdhist'].shift(1) > 0)) |
            # Price hits upper Bollinger Band
            (dataframe['close'] > dataframe['bb_upper'])
        )
        
        # Short exit conditions
        short_exit_conditions = (
            # Moving Average Crossover: fast MA crosses above medium MA
            (dataframe['fast_ma'] > dataframe['medium_ma']) |
            # RSI oversold
            (dataframe['rsi'] < 20) |
            # MACD crossover to positive
            ((dataframe['macdhist'] > 0) & (dataframe['macdhist'].shift(1) < 0)) |
            # Price hits lower Bollinger Band
            (dataframe['close'] < dataframe['bb_lower'])
        )
        
        # Set exit signals
        dataframe.loc[long_exit_conditions, 'exit_long'] = 1
        dataframe.loc[short_exit_conditions, 'exit_short'] = 1
        
        return dataframe
    
    def calculate_position_size(self, capital, current_price, atr):
        """
        Calculate position size based on risk per trade and volatility (ATR)
        
        Args:
            capital: Available capital
            current_price: Current asset price
            atr: Average True Range (volatility measure)
            
        Returns:
            position_size: Amount of asset to buy/sell
        """
        # Risk amount in currency
        risk_amount = capital * self.risk_per_trade
        
        # Set stop loss at 2 * ATR away from entry
        stop_distance = 2 * atr
        
        # Calculate position size based on risk
        position_size = risk_amount / stop_distance
        
        # Adjust position size based on price
        position_value = position_size * current_price
        
        # Ensure we don't exceed available capital
        if position_value > capital:
            position_size = capital / current_price
            
        return position_size
    
    def trailing_stop(self, entry_price, current_price, highest_price, is_long=True):
        """
        Calculate trailing stop price
        
        Args:
            entry_price: Entry price of the trade
            current_price: Current price of the asset
            highest_price: Highest price reached since entry (for long)
            is_long: True for long trades, False for short trades
            
        Returns:
            stop_triggered: Boolean indicating if stop is triggered
            stop_price: The trailing stop price
        """
        if is_long:
            # Initial stop loss
            initial_stop = entry_price * (1 - self.trailing_stop_pct)
            
            # Trailing stop based on highest price reached
            trailing_stop = highest_price * (1 - self.trailing_stop_pct)
            
            # Use the higher of the two stops
            stop_price = max(initial_stop, trailing_stop)
            
            # Check if stop is triggered
            stop_triggered = current_price < stop_price
        else:
            # For short trades (reverse logic)
            initial_stop = entry_price * (1 + self.trailing_stop_pct)
            trailing_stop = highest_price * (1 + self.trailing_stop_pct)
            stop_price = min(initial_stop, trailing_stop)
            stop_triggered = current_price > stop_price
            
        return stop_triggered, stop_price 