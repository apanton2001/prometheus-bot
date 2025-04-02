# pragma pylint: disable=missing-docstring, invalid-name, pointless-string-statement
# flake8: noqa: F401

import numpy as np
import pandas as pd
from pandas import DataFrame
from freqtrade.strategy import IStrategy, merge_informative_pair
from freqtrade.exchange import timeframe_to_minutes
import talib.abstract as ta
from typing import Dict, Optional
from datetime import datetime
from .base_strategy import BaseStrategy

class MomentumStrategy(BaseStrategy):
    """
    Basic momentum strategy using moving averages and RSI.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the momentum strategy.
        
        Args:
            config (Dict): Strategy configuration including:
                - fast_ma_period: int (default: 10)
                - slow_ma_period: int (default: 30)
                - rsi_period: int (default: 14)
                - rsi_overbought: float (default: 70)
                - rsi_oversold: float (default: 30)
                - stop_loss_pct: float (default: 0.02)
                - take_profit_pct: float (default: 0.04)
        """
        super().__init__(config)
        self.fast_ma_period = config.get('fast_ma_period', 10)
        self.slow_ma_period = config.get('slow_ma_period', 30)
        self.rsi_period = config.get('rsi_period', 14)
        self.rsi_overbought = config.get('rsi_overbought', 70)
        self.rsi_oversold = config.get('rsi_oversold', 30)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.02)
        self.take_profit_pct = config.get('take_profit_pct', 0.04)
        
    def generate_signals(self, data: pd.DataFrame) -> Optional[Dict]:
        """
        Generate trading signals based on moving average crossover and RSI.
        
        Args:
            data (pd.DataFrame): Market data with OHLCV columns
            
        Returns:
            Optional[Dict]: Trading signal if conditions are met
        """
        # Calculate indicators
        data['fast_ma'] = ta.trend.sma_indicator(data['close'], self.fast_ma_period)
        data['slow_ma'] = ta.trend.sma_indicator(data['close'], self.slow_ma_period)
        data['rsi'] = ta.momentum.rsi(data['close'], self.rsi_period)
        
        # Get latest values
        current_price = data['close'].iloc[-1]
        current_rsi = data['rsi'].iloc[-1]
        prev_fast_ma = data['fast_ma'].iloc[-2]
        prev_slow_ma = data['slow_ma'].iloc[-2]
        current_fast_ma = data['fast_ma'].iloc[-1]
        current_slow_ma = data['slow_ma'].iloc[-1]
        
        # Check for buy signal
        if (prev_fast_ma <= prev_slow_ma and current_fast_ma > current_slow_ma and
            current_rsi < self.rsi_overbought):
            return {
                'action': 'buy',
                'price': current_price,
                'size': 1.0,  # Will be adjusted by calculate_position_size
                'confidence': 0.8,
                'timestamp': datetime.utcnow(),
                'stop_loss': current_price * (1 - self.stop_loss_pct),
                'take_profit': current_price * (1 + self.take_profit_pct)
            }
        
        # Check for sell signal
        elif (prev_fast_ma >= prev_slow_ma and current_fast_ma < current_slow_ma and
              current_rsi > self.rsi_oversold):
            return {
                'action': 'sell',
                'price': current_price,
                'size': 1.0,  # Will be adjusted by calculate_position_size
                'confidence': 0.8,
                'timestamp': datetime.utcnow(),
                'stop_loss': current_price * (1 + self.stop_loss_pct),
                'take_profit': current_price * (1 - self.take_profit_pct)
            }
        
        return None
    
    def calculate_position_size(self, signal: Dict, account_balance: float) -> float:
        """
        Calculate position size based on risk management rules.
        
        Args:
            signal (Dict): Trading signal
            account_balance (float): Current account balance
            
        Returns:
            float: Position size in base currency
        """
        risk_amount = account_balance * (self.config.get('risk_percentage', 0.01))
        price = signal['price']
        stop_loss = signal['stop_loss']
        
        # Calculate position size based on risk
        risk_per_unit = abs(price - stop_loss)
        position_size = risk_amount / risk_per_unit
        
        # Apply maximum position size limit
        max_position = account_balance * self.config.get('max_position_size', 0.1)
        return min(position_size, max_position)
    
    def validate_signal(self, signal: Dict) -> bool:
        """
        Validate if the trading signal meets all criteria.
        
        Args:
            signal (Dict): Trading signal to validate
            
        Returns:
            bool: True if signal is valid, False otherwise
        """
        if not signal:
            return False
            
        # Check required fields
        required_fields = ['action', 'price', 'size', 'confidence', 'timestamp']
        if not all(field in signal for field in required_fields):
            return False
            
        # Validate action
        if signal['action'] not in ['buy', 'sell']:
            return False
            
        # Validate price
        if signal['price'] <= 0:
            return False
            
        # Validate size
        if signal['size'] <= 0:
            return False
            
        # Validate confidence
        if not 0 <= signal['confidence'] <= 1:
            return False
            
        # Validate stop loss and take profit
        if 'stop_loss' not in signal or 'take_profit' not in signal:
            return False
            
        if signal['action'] == 'buy':
            if signal['stop_loss'] >= signal['price'] or signal['take_profit'] <= signal['price']:
                return False
        else:  # sell
            if signal['stop_loss'] <= signal['price'] or signal['take_profit'] >= signal['price']:
                return False
                
        return True

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