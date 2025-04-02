import pandas as pd
import numpy as np
import talib

class SimpleMomentumStrategy:
    def __init__(self):
        # Parameters for the strategy - make more sensitive to generate more trades
        self.buy_rsi_value = 40  # Increased from 30
        self.buy_ema_short_period = 5  # Reduced from 7
        self.buy_ema_long_period = 15  # Reduced from 25
        self.sell_rsi_value = 60  # Decreased from 70
        
    def populate_indicators(self, dataframe, metadata=None):
        # RSI
        dataframe['rsi'] = talib.RSI(dataframe['close'], timeperiod=14)
        
        # EMAs
        dataframe['ema_short'] = talib.EMA(dataframe['close'], timeperiod=self.buy_ema_short_period)
        dataframe['ema_long'] = talib.EMA(dataframe['close'], timeperiod=self.buy_ema_long_period)
        
        # Add MACD for additional signals
        macd = talib.MACD(dataframe['close'], fastperiod=12, slowperiod=26, signalperiod=9)
        dataframe['macd'] = macd[0]
        dataframe['macdsignal'] = macd[1]
        dataframe['macdhist'] = macd[2]
        
        return dataframe
    
    def populate_entry_trend(self, dataframe, metadata=None):
        dataframe['enter_long'] = 0
        
        # Buy signal: RSI oversold and short EMA > long EMA OR positive MACD crossover
        buy_condition = (
            (
                (dataframe['rsi'] < self.buy_rsi_value) &  # RSI below threshold
                (dataframe['ema_short'] > dataframe['ema_long'])  # Upward trend
            ) |
            (
                (dataframe['macdhist'] > 0) &  # Positive MACD histogram 
                (dataframe['macdhist'].shift(1) < 0)  # Previous was negative (crossover)
            )
        ) & (dataframe['volume'] > 0)  # Make sure volume is not 0
        
        dataframe.loc[buy_condition, 'enter_long'] = 1
        
        return dataframe
    
    def populate_exit_trend(self, dataframe, metadata=None):
        dataframe['exit_long'] = 0
        
        # Sell signal: RSI overbought and short EMA < long EMA OR negative MACD crossover
        sell_condition = (
            (
                (dataframe['rsi'] > self.sell_rsi_value) &  # RSI above threshold 
                (dataframe['ema_short'] < dataframe['ema_long'])  # Downward trend
            ) |
            (
                (dataframe['macdhist'] < 0) &  # Negative MACD histogram
                (dataframe['macdhist'].shift(1) > 0)  # Previous was positive (crossover)
            )
        ) & (dataframe['volume'] > 0)  # Make sure volume is not 0
        
        dataframe.loc[sell_condition, 'exit_long'] = 1
        
        return dataframe 