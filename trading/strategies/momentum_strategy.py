# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401

import numpy as np
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import IStrategy, merge_informative_pair
from freqtrade.exchange import timeframe_to_minutes
import talib.abstract as ta

class MomentumStrategy(IStrategy):
    """
    Momentum-based strategy.
    Uses RSI and moving averages to identify momentum trends.
    """

    # Strategy interface version - allow new iterations of the strategy interface.
    INTERFACE_VERSION = 2

    # Minimal ROI designed for the strategy.
    minimal_roi = {
        "0": 0.1,
        "30": 0.05,
        "60": 0.025,
        "120": 0.01
    }

    # Optimal stoploss designed for the strategy.
    stoploss = -0.05

    # Trailing stoploss
    trailing_stop = True
    trailing_stop_positive = 0.01
    trailing_stop_positive_offset = 0.02
    trailing_only_offset_is_reached = True

    # Optimal timeframe for the strategy.
    timeframe = '5m'

    # Run "populate_indicators()" only for new candle.
    process_only_new_candles = True

    # Number of candles the strategy requires before producing valid signals
    startup_candle_count: int = 30

    # Optional order type mapping.
    order_types = {
        'buy': 'limit',
        'sell': 'limit',
        'stoploss': 'market',
        'stoploss_on_exchange': False
    }

    def informative_pairs(self):
        """
        Define additional, informative pair/interval combinations to be cached from the exchange.
        """
        return []

    def populate_indicators(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Adds several different TA indicators to the given DataFrame

        Performance Note: For the best performance be frugal on the number of indicators
        you are using. Let uncomment only the indicator you are using in your strategies
        or your hyperopt configuration, otherwise you will waste your memory and CPU usage.
        """
        
        # RSI
        dataframe['rsi'] = ta.RSI(dataframe, timeperiod=14)
        
        # Moving Averages
        dataframe['ema9'] = ta.EMA(dataframe, timeperiod=9)
        dataframe['ema21'] = ta.EMA(dataframe, timeperiod=21)
        dataframe['ema50'] = ta.EMA(dataframe, timeperiod=50)
        
        # MACD
        macd = ta.MACD(dataframe)
        dataframe['macd'] = macd['macd']
        dataframe['macdsignal'] = macd['macdsignal']
        dataframe['macdhist'] = macd['macdhist']
        
        # Volume
        dataframe['volume_mean_12'] = dataframe['volume'].rolling(12).mean()
        
        return dataframe

    def populate_buy_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the buy signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with buy column
        """
        dataframe.loc[
            (
                # RSI oversold
                (dataframe['rsi'] < 30) &
                # MACD rising
                (dataframe['macdhist'] > 0) &
                # EMA 9 crossing above EMA 21
                (dataframe['ema9'] > dataframe['ema21']) &
                # Volume increasing
                (dataframe['volume'] > dataframe['volume_mean_12'])
            ),
            'buy'] = 1

        return dataframe

    def populate_sell_trend(self, dataframe: DataFrame, metadata: dict) -> DataFrame:
        """
        Based on TA indicators, populates the sell signal for the given dataframe
        :param dataframe: DataFrame populated with indicators
        :param metadata: Additional information, like the currently traded pair
        :return: DataFrame with sell column
        """
        dataframe.loc[
            (
                # RSI overbought
                (dataframe['rsi'] > 70) &
                # MACD falling
                (dataframe['macdhist'] < 0) &
                # EMA 9 crossing below EMA 21
                (dataframe['ema9'] < dataframe['ema21']) 
            ),
            'sell'] = 1
        return dataframe 