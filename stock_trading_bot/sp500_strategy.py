import pandas as pd
import numpy as np
import pandas_ta as ta
from datetime import datetime, timedelta
import logging
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from typing import Dict, List, Tuple, Union, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('sp500_strategy')

class SP500Strategy:
    """
    Sophisticated S&P 500 trading strategy with multi-timeframe analysis,
    sector rotation intelligence, and macroeconomic indicator integration.
    """
    
    def __init__(
        self,
        symbols: List[str],
        timeframes: List[str] = ['15m', '1h', '4h', '1d'],
        risk_per_trade: float = 0.01,
        max_open_positions: int = 5,
        sector_exposure_limit: float = 0.30,
        lookback_periods: int = 100,
        use_ml_features: bool = False
    ):
        """
        Initialize the S&P 500 trading strategy.
        
        Args:
            symbols: List of stock symbols to trade
            timeframes: List of timeframes to analyze
            risk_per_trade: Maximum risk per trade (as decimal of portfolio)
            max_open_positions: Maximum number of concurrent positions
            sector_exposure_limit: Maximum exposure to any single sector (as decimal)
            lookback_periods: Number of periods to look back for pattern recognition
            use_ml_features: Whether to use machine learning enhanced features
        """
        self.symbols = symbols
        self.timeframes = timeframes
        self.risk_per_trade = risk_per_trade
        self.max_open_positions = max_open_positions
        self.sector_exposure_limit = sector_exposure_limit
        self.lookback_periods = lookback_periods
        self.use_ml_features = use_ml_features
        
        # Data storage
        self.data = {symbol: {tf: None for tf in timeframes} for symbol in symbols}
        self.indicators = {symbol: {tf: {} for tf in timeframes} for symbol in symbols}
        self.sector_data = {}
        self.macro_data = {}
        self.market_regime = "unknown"
        
        # State tracking
        self.open_positions = {}
        self.historical_trades = []
        self.portfolio_value = 0
        self.available_capital = 0
        
        # Strategy parameters (adaptive based on market regime)
        self.strategy_params = {
            "bullish": {
                "fast_ma": 8,
                "medium_ma": 21,
                "slow_ma": 50,
                "trend_strength_threshold": 25,
                "profit_target_multiplier": 2.5,
                "stoploss_multiplier": 1.0,
                "volume_threshold": 1.5,
                "rsi_oversold": 40,
                "rsi_overbought": 70
            },
            "bearish": {
                "fast_ma": 5,
                "medium_ma": 15,
                "slow_ma": 35,
                "trend_strength_threshold": 35,
                "profit_target_multiplier": 1.5,
                "stoploss_multiplier": 0.8,
                "volume_threshold": 2.0,
                "rsi_oversold": 30,
                "rsi_overbought": 60
            },
            "ranging": {
                "fast_ma": 5,
                "medium_ma": 13,
                "slow_ma": 30,
                "trend_strength_threshold": 20,
                "profit_target_multiplier": 1.2,
                "stoploss_multiplier": 0.7,
                "volume_threshold": 1.8,
                "rsi_oversold": 35,
                "rsi_overbought": 65
            }
        }
        
        logger.info(f"Initialized SP500Strategy with {len(symbols)} symbols and {len(timeframes)} timeframes")

    def load_data(self, symbol: str, timeframe: str, data: pd.DataFrame) -> None:
        """
        Load price data for a specific symbol and timeframe.
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe of the data
            data: DataFrame with OHLCV data
        """
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in data.columns]
        
        if missing_columns:
            logger.error(f"Missing required columns: {missing_columns}")
            return
            
        self.data[symbol][timeframe] = data.copy()
        logger.info(f"Loaded data for {symbol} on {timeframe} timeframe: {len(data)} candles")
        
    def load_sector_data(self, sector_data: Dict[str, pd.DataFrame]) -> None:
        """
        Load sector performance data.
        
        Args:
            sector_data: Dictionary mapping sector names to performance DataFrames
        """
        self.sector_data = sector_data
        logger.info(f"Loaded data for {len(sector_data)} sectors")
        
    def load_macro_data(self, macro_data: Dict[str, pd.DataFrame]) -> None:
        """
        Load macroeconomic indicator data.
        
        Args:
            macro_data: Dictionary mapping indicator names to DataFrames
        """
        self.macro_data = macro_data
        logger.info(f"Loaded {len(macro_data)} macroeconomic indicators")
        
    def compute_indicators(self, symbol: str, timeframe: str) -> None:
        """
        Compute technical indicators for a specific symbol and timeframe.
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe to compute indicators for
        """
        df = self.data[symbol][timeframe]
        if df is None or df.empty:
            logger.warning(f"No data available for {symbol} on {timeframe} timeframe")
            return
            
        # Moving averages
        params = self.strategy_params[self.market_regime]
        df[f'ma_fast'] = ta.sma(df['close'], length=params['fast_ma'])
        df[f'ma_medium'] = ta.sma(df['close'], length=params['medium_ma'])
        df[f'ma_slow'] = ta.sma(df['close'], length=params['slow_ma'])
        df['ma_200'] = ta.sma(df['close'], length=200)
        
        # RSI
        df['rsi'] = ta.rsi(df['close'], length=14)
        
        # MACD
        macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
        df['macd'] = macd['MACD_12_26_9']
        df['macd_signal'] = macd['MACDs_12_26_9']
        df['macd_hist'] = macd['MACDh_12_26_9']
        
        # Bollinger Bands
        bollinger = ta.bbands(df['close'], length=20, std=2)
        df['bb_upper'] = bollinger['BBU_20_2.0']
        df['bb_middle'] = bollinger['BBM_20_2.0']
        df['bb_lower'] = bollinger['BBL_20_2.0']
        
        # ATR for volatility
        df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=14)
        
        # Volume indicators
        df['volume_sma'] = ta.sma(df['volume'], length=20)
        df['volume_ratio'] = df['volume'] / df['volume_sma']
        
        # Trend strength (ADX)
        adx = ta.adx(df['high'], df['low'], df['close'], length=14)
        df['adx'] = adx['ADX_14']
        df['di_plus'] = adx['DMP_14']
        df['di_minus'] = adx['DMN_14']
        
        # Store computed indicators
        self.indicators[symbol][timeframe] = {
            'ma_fast': df['ma_fast'],
            'ma_medium': df['ma_medium'],
            'ma_slow': df['ma_slow'],
            'ma_200': df['ma_200'],
            'rsi': df['rsi'],
            'macd': df['macd'],
            'macd_signal': df['macd_signal'],
            'macd_hist': df['macd_hist'],
            'bb_upper': df['bb_upper'],
            'bb_middle': df['bb_middle'],
            'bb_lower': df['bb_lower'],
            'atr': df['atr'],
            'volume_ratio': df['volume_ratio'],
            'adx': df['adx'],
            'di_plus': df['di_plus'],
            'di_minus': df['di_minus']
        }
        
        logger.info(f"Computed indicators for {symbol} on {timeframe} timeframe")

    def detect_market_regime(self) -> str:
        """
        Detect the current market regime (bullish, bearish, or ranging).
        Uses market index data, volatility, and trend strength.
        
        Returns:
            String indicating market regime
        """
        # For demonstration - typically would use SPY or market index data
        spy_data = self.data.get('SPY', {}).get('1d')
        if spy_data is None or spy_data.empty:
            logger.warning("No SPY data available for market regime detection")
            return "unknown"
            
        # Get the most recent indicators
        latest = spy_data.iloc[-1]
        
        # Trend direction
        trend_up = latest['ma_fast'] > latest['ma_slow']
        above_200ma = latest['close'] > latest['ma_200']
        
        # Trend strength
        strong_trend = latest['adx'] > 25
        
        # Volatility (using ATR)
        high_volatility = latest['atr'] > spy_data['atr'].mean() * 1.5
        
        # Determine regime
        if trend_up and above_200ma and strong_trend:
            regime = "bullish"
        elif not trend_up and not above_200ma and strong_trend:
            regime = "bearish"
        else:
            regime = "ranging"
            
        logger.info(f"Current market regime detected: {regime}")
        self.market_regime = regime
        return regime
        
    def analyze_sector_rotation(self) -> Dict[str, float]:
        """
        Analyze sector rotation to identify strong and weak sectors.
        
        Returns:
            Dictionary mapping sectors to strength scores
        """
        if not self.sector_data:
            logger.warning("No sector data available for rotation analysis")
            return {}
            
        sector_strength = {}
        
        for sector, data in self.sector_data.items():
            if data is None or data.empty:
                continue
                
            # Calculate metrics (last 20 periods)
            recent = data.iloc[-20:]
            
            # Relative strength vs market
            if 'SPY' in self.data and '1d' in self.data['SPY']:
                spy_data = self.data['SPY']['1d'].iloc[-20:]
                relative_strength = recent['close'].pct_change().mean() / spy_data['close'].pct_change().mean()
            else:
                relative_strength = 1.0
                
            # Trend strength
            trend_strength = recent['adx'].mean() if 'adx' in recent.columns else 25.0
            
            # Momentum
            momentum = recent['close'].pct_change(5).mean() * 100
            
            # Volume trend
            volume_trend = recent['volume'].pct_change().mean() * 100
            
            # Combined sector strength score (normalized 0-100)
            strength_score = (
                (relative_strength * 40) + 
                (trend_strength / 100 * 30) + 
                (momentum * 20) + 
                (volume_trend * 10)
            )
            
            sector_strength[sector] = min(max(strength_score, 0), 100)
            
        logger.info(f"Sector rotation analysis complete. Strongest sector: {max(sector_strength, key=sector_strength.get)}")
        return sector_strength
        
    def get_stock_signals(self, symbol: str) -> Dict[str, any]:
        """
        Generate trading signals for a specific stock using multi-timeframe analysis.
        
        Args:
            symbol: Stock symbol to analyze
            
        Returns:
            Dictionary containing trading signals and analysis
        """
        signals = {
            'symbol': symbol,
            'entry': False,
            'exit': False,
            'direction': None,
            'strength': 0,
            'risk_score': 0,
            'target_price': None,
            'stop_loss': None,
            'timeframe_alignment': 0
        }
        
        # Check if we have data for this symbol
        if symbol not in self.data:
            logger.warning(f"No data available for {symbol}")
            return signals
            
        # Get current market regime parameters
        params = self.strategy_params[self.market_regime]
        
        # Multi-timeframe trend alignment check
        timeframe_signals = {}
        timeframe_weights = {
            '15m': 0.1,
            '1h': 0.3,
            '4h': 0.4,
            '1d': 0.2
        }
        
        alignment_score = 0
        for tf in self.timeframes:
            if tf not in self.data[symbol] or self.data[symbol][tf] is None:
                continue
                
            df = self.data[symbol][tf]
            if df.empty or len(df) < 50:
                continue
            
            # Get latest data point
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            # Check for bullish pattern
            bullish = (
                latest['ma_fast'] > latest['ma_medium'] and
                prev['ma_fast'] <= prev['ma_medium'] and
                latest['adx'] > params['trend_strength_threshold'] and
                latest['volume_ratio'] > params['volume_threshold'] and
                latest['rsi'] < params['rsi_overbought']
            )
            
            # Check for bearish pattern
            bearish = (
                latest['ma_fast'] < latest['ma_medium'] and
                prev['ma_fast'] >= prev['ma_medium'] and
                latest['adx'] > params['trend_strength_threshold'] and
                latest['volume_ratio'] > params['volume_threshold'] and
                latest['rsi'] > params['rsi_oversold']
            )
            
            # Trend direction
            if bullish:
                timeframe_signals[tf] = 1  # Bullish
                alignment_score += timeframe_weights.get(tf, 0.25) * 1
            elif bearish:
                timeframe_signals[tf] = -1  # Bearish
                alignment_score += timeframe_weights.get(tf, 0.25) * -1
            else:
                timeframe_signals[tf] = 0  # Neutral
            
        # Calculate overall signal based on primary timeframe (1h)
        primary_tf = '1h'
        if primary_tf in self.data[symbol] and self.data[symbol][primary_tf] is not None:
            df = self.data[symbol][primary_tf]
            if not df.empty and len(df) >= 50:
                latest = df.iloc[-1]
                prev = df.iloc[-2]
                
                # Entry signals
                bullish_entry = (
                    latest['ma_fast'] > latest['ma_medium'] and
                    prev['ma_fast'] <= prev['ma_medium'] and
                    latest['close'] > latest['ma_200'] and
                    latest['adx'] > params['trend_strength_threshold'] and
                    latest['volume_ratio'] > params['volume_threshold'] and
                    latest['macd_hist'] > 0 and
                    prev['macd_hist'] <= 0 and
                    latest['rsi'] < params['rsi_overbought'] and
                    alignment_score > 0.3  # Require positive alignment across timeframes
                )
                
                bearish_entry = (
                    latest['ma_fast'] < latest['ma_medium'] and
                    prev['ma_fast'] >= prev['ma_medium'] and
                    latest['close'] < latest['ma_200'] and
                    latest['adx'] > params['trend_strength_threshold'] and
                    latest['volume_ratio'] > params['volume_threshold'] and
                    latest['macd_hist'] < 0 and
                    prev['macd_hist'] >= 0 and
                    latest['rsi'] > params['rsi_oversold'] and
                    alignment_score < -0.3  # Require negative alignment across timeframes
                )
                
                # Exit signals
                bullish_exit = (
                    latest['ma_fast'] < latest['ma_medium'] and
                    prev['ma_fast'] >= prev['ma_medium']
                )
                
                bearish_exit = (
                    latest['ma_fast'] > latest['ma_medium'] and
                    prev['ma_fast'] <= prev['ma_medium']
                )
                
                # Set signal values
                if bullish_entry:
                    signals['entry'] = True
                    signals['direction'] = 'long'
                    signals['strength'] = min(alignment_score * 100, 100)
                    
                    # Set target and stop loss
                    atr = latest['atr']
                    signals['target_price'] = latest['close'] + (atr * params['profit_target_multiplier'])
                    signals['stop_loss'] = latest['close'] - (atr * params['stoploss_multiplier'])
                    
                elif bearish_entry:
                    signals['entry'] = True
                    signals['direction'] = 'short'
                    signals['strength'] = min(abs(alignment_score) * 100, 100)
                    
                    # Set target and stop loss
                    atr = latest['atr']
                    signals['target_price'] = latest['close'] - (atr * params['profit_target_multiplier'])
                    signals['stop_loss'] = latest['close'] + (atr * params['stoploss_multiplier'])
                    
                # Exit signals for existing positions
                if symbol in self.open_positions:
                    current_position = self.open_positions[symbol]
                    if current_position['direction'] == 'long' and bullish_exit:
                        signals['exit'] = True
                    elif current_position['direction'] == 'short' and bearish_exit:
                        signals['exit'] = True
                
                # Calculate risk score (0-100, lower is better)
                vix_value = 15  # Default - ideally would get from market data
                if 'VIX' in self.data and '1d' in self.data['VIX']:
                    vix_data = self.data['VIX']['1d']
                    if not vix_data.empty:
                        vix_value = vix_data['close'].iloc[-1]
                        
                # Risk score components
                volatility_risk = min(vix_value / 50 * 100, 100)  # VIX normalized
                trend_strength = min(latest['adx'] * 2, 100)  # ADX normalized
                momentum_risk = abs(latest['rsi'] - 50) / 50 * 100  # RSI distance from middle
                
                # Lower risk score is better (less risky)
                signals['risk_score'] = (
                    (volatility_risk * 0.4) + 
                    (100 - trend_strength) * 0.4 + 
                    momentum_risk * 0.2
                )
                
                # Timeframe alignment score (higher is better)
                signals['timeframe_alignment'] = alignment_score * 100
                
        return signals
        
    def calculate_position_size(self, symbol: str, signal: Dict[str, any]) -> float:
        """
        Calculate position size based on risk parameters and volatility.
        
        Args:
            symbol: Stock symbol
            signal: Trading signal dictionary
            
        Returns:
            Position size as a percentage of portfolio
        """
        if not signal['entry'] or signal['stop_loss'] is None:
            return 0.0
            
        # Get current price
        current_price = None
        for tf in ['15m', '1h', '4h', '1d']:
            if tf in self.data[symbol] and self.data[symbol][tf] is not None:
                df = self.data[symbol][tf]
                if not df.empty:
                    current_price = df['close'].iloc[-1]
                    break
                    
        if current_price is None:
            logger.warning(f"Cannot calculate position size for {symbol}: no price data")
            return 0.0
            
        # Calculate risk per share
        stop_distance = abs(current_price - signal['stop_loss'])
        if stop_distance <= 0:
            logger.warning(f"Invalid stop distance for {symbol}")
            return 0.0
            
        # Risk amount in dollars
        risk_amount = self.portfolio_value * self.risk_per_trade
        
        # Number of shares
        shares = risk_amount / stop_distance
        
        # Position size as percentage of portfolio
        position_size = (shares * current_price) / self.portfolio_value
        
        # Adjust based on risk score, timeframe alignment and market regime
        if signal['risk_score'] > 50:  # Higher risk, reduce position
            position_size *= (100 - signal['risk_score']) / 100
            
        if signal['timeframe_alignment'] < 50:  # Lower alignment, reduce position
            position_size *= signal['timeframe_alignment'] / 100
            
        # Check sector exposure limit
        sector = self.get_stock_sector(symbol)
        current_sector_exposure = self.get_sector_exposure(sector)
        available_sector_exposure = max(0, self.sector_exposure_limit - current_sector_exposure)
        position_size = min(position_size, available_sector_exposure)
        
        # Ensure we don't exceed available capital
        position_size = min(position_size, self.available_capital / self.portfolio_value)
        
        logger.info(f"Calculated position size for {symbol}: {position_size:.2%}")
        return position_size
        
    def get_stock_sector(self, symbol: str) -> str:
        """
        Get the sector for a given stock symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Sector name
        """
        # This would typically come from a mapping file or external data source
        # For demonstration, return placeholder
        return "Technology"
        
    def get_sector_exposure(self, sector: str) -> float:
        """
        Calculate current exposure to a specific sector.
        
        Args:
            sector: Sector name
            
        Returns:
            Current exposure as a percentage of portfolio
        """
        sector_exposure = sum(
            pos['size'] 
            for sym, pos in self.open_positions.items() 
            if self.get_stock_sector(sym) == sector
        )
        return sector_exposure
        
    def run_strategy(self) -> List[Dict[str, any]]:
        """
        Run the strategy across all symbols and generate trading decisions.
        
        Returns:
            List of trading decisions
        """
        # First detect market regime
        self.detect_market_regime()
        
        # Analyze sector rotation
        sector_strength = self.analyze_sector_rotation()
        
        # Generate signals for each symbol
        all_signals = []
        for symbol in self.symbols:
            # Compute indicators for all timeframes
            for tf in self.timeframes:
                if tf in self.data[symbol] and self.data[symbol][tf] is not None:
                    self.compute_indicators(symbol, tf)
            
            # Get trading signals
            signal = self.get_stock_signals(symbol)
            
            # If we have a valid entry signal, calculate position size
            if signal['entry']:
                position_size = self.calculate_position_size(symbol, signal)
                signal['position_size'] = position_size
                
                # Store the complete decision
                if position_size > 0:
                    all_signals.append({
                        **signal,
                        'timestamp': datetime.now(),
                        'market_regime': self.market_regime,
                        'sector': self.get_stock_sector(symbol),
                        'sector_strength': sector_strength.get(self.get_stock_sector(symbol), 0)
                    })
        
        # Sort by signal strength and risk score (higher strength, lower risk is better)
        if all_signals:
            all_signals.sort(key=lambda x: (x['strength'] - x['risk_score']), reverse=True)
            
        logger.info(f"Strategy run complete. Generated {len(all_signals)} trading signals")
        return all_signals
        
    def execute_trades(self, signals: List[Dict[str, any]]) -> List[Dict[str, any]]:
        """
        Execute trades based on the generated signals.
        
        Args:
            signals: List of trading signals
            
        Returns:
            List of executed trades
        """
        executed_trades = []
        
        # First handle exits
        for symbol, position in list(self.open_positions.items()):
            matching_signals = [s for s in signals if s['symbol'] == symbol and s['exit']]
            
            if matching_signals:
                # Exit position
                trade = {
                    'symbol': symbol,
                    'action': 'exit',
                    'direction': position['direction'],
                    'timestamp': datetime.now(),
                    'price': None,  # Would come from execution system
                    'size': position['size'],
                    'reason': 'signal'
                }
                executed_trades.append(trade)
                
                # Update available capital
                self.available_capital += self.portfolio_value * position['size']
                
                # Remove from open positions
                del self.open_positions[symbol]
                
                logger.info(f"Exited position in {symbol}")
        
        # Then handle entries (limited by max open positions)
        available_positions = self.max_open_positions - len(self.open_positions)
        
        for signal in signals[:available_positions]:
            if signal['entry'] and not signal['exit'] and signal.get('position_size', 0) > 0:
                # Open new position
                trade = {
                    'symbol': signal['symbol'],
                    'action': 'entry',
                    'direction': signal['direction'],
                    'timestamp': datetime.now(),
                    'price': None,  # Would come from execution system
                    'size': signal['position_size'],
                    'target': signal['target_price'],
                    'stop_loss': signal['stop_loss'],
                    'reason': 'signal'
                }
                executed_trades.append(trade)
                
                # Update open positions and available capital
                self.open_positions[signal['symbol']] = {
                    'direction': signal['direction'],
                    'size': signal['position_size'],
                    'entry_time': datetime.now(),
                    'entry_price': None,  # Would come from execution system
                    'target': signal['target_price'],
                    'stop_loss': signal['stop_loss']
                }
                
                self.available_capital -= self.portfolio_value * signal['position_size']
                
                logger.info(f"Entered new position in {signal['symbol']}")
        
        return executed_trades
        
    def update_portfolio_value(self, new_value: float) -> None:
        """
        Update the portfolio value.
        
        Args:
            new_value: New portfolio value
        """
        self.portfolio_value = new_value
        self.available_capital = new_value - sum(pos['size'] * new_value for pos in self.open_positions.values())
        
    def visualize_strategy(self, symbol: str, timeframe: str, periods: int = 100) -> None:
        """
        Create visualization of the strategy for a specific symbol and timeframe.
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe to visualize
            periods: Number of periods to include in visualization
        """
        if symbol not in self.data or timeframe not in self.data[symbol]:
            logger.warning(f"No data available for {symbol} on {timeframe} timeframe")
            return
            
        df = self.data[symbol][timeframe]
        if df is None or df.empty or len(df) < periods:
            logger.warning(f"Insufficient data for visualization")
            return
            
        # Get subset of data
        df = df.iloc[-periods:]
        
        # Create figure
        plt.figure(figsize=(14, 10))
        
        # Plot price and MAs
        ax1 = plt.subplot(3, 1, 1)
        ax1.plot(df.index, df['close'], label='Close', color='black')
        ax1.plot(df.index, df['ma_fast'], label=f"Fast MA", color='blue')
        ax1.plot(df.index, df['ma_medium'], label=f"Medium MA", color='green')
        ax1.plot(df.index, df['ma_slow'], label=f"Slow MA", color='red')
        ax1.fill_between(df.index, df['bb_upper'], df['bb_lower'], alpha=0.2, color='gray')
        ax1.set_title(f"{symbol} - {timeframe} Strategy Visualization")
        ax1.legend()
        ax1.grid(True)
        
        # Plot RSI
        ax2 = plt.subplot(3, 1, 2)
        ax2.plot(df.index, df['rsi'], color='purple')
        ax2.axhline(y=70, color='red', linestyle='--')
        ax2.axhline(y=30, color='green', linestyle='--')
        ax2.set_title("RSI")
        ax2.grid(True)
        
        # Plot MACD
        ax3 = plt.subplot(3, 1, 3)
        ax3.plot(df.index, df['macd'], label='MACD', color='blue')
        ax3.plot(df.index, df['macd_signal'], label='Signal', color='red')
        ax3.bar(df.index, df['macd_hist'], label='Histogram', color='green', alpha=0.5)
        ax3.axhline(y=0, color='black', linestyle='-')
        ax3.set_title("MACD")
        ax3.legend()
        ax3.grid(True)
        
        plt.tight_layout()
        plt.show()
        
    def generate_performance_report(self) -> Dict[str, any]:
        """
        Generate a performance report for the strategy.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.historical_trades:
            return {"error": "No historical trades available for performance analysis"}
            
        # Calculate performance metrics
        total_trades = len(self.historical_trades)
        winning_trades = sum(1 for trade in self.historical_trades if trade.get('profit', 0) > 0)
        losing_trades = sum(1 for trade in self.historical_trades if trade.get('profit', 0) <= 0)
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        profits = sum(trade.get('profit', 0) for trade in self.historical_trades if trade.get('profit', 0) > 0)
        losses = sum(abs(trade.get('profit', 0)) for trade in self.historical_trades if trade.get('profit', 0) < 0)
        
        avg_profit = profits / winning_trades if winning_trades > 0 else 0
        avg_loss = losses / losing_trades if losing_trades > 0 else 0
        
        profit_factor = profits / losses if losses > 0 else float('inf')
        
        # Maximum drawdown calculation would be more complex
        max_drawdown = 0.0  # Placeholder
        
        return {
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": losing_trades,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "average_profit": avg_profit,
            "average_loss": avg_loss,
            "maximum_drawdown": max_drawdown,
            "market_regime_breakdown": self._get_regime_breakdown(),
            "sector_performance": self._get_sector_performance()
        }
        
    def _get_regime_breakdown(self) -> Dict[str, any]:
        """
        Get performance breakdown by market regime.
        
        Returns:
            Dictionary with regime performance metrics
        """
        regimes = {}
        
        for regime in ["bullish", "bearish", "ranging"]:
            regime_trades = [t for t in self.historical_trades if t.get('market_regime') == regime]
            
            if not regime_trades:
                regimes[regime] = {"trades": 0, "win_rate": 0, "avg_profit": 0}
                continue
                
            total = len(regime_trades)
            winners = sum(1 for t in regime_trades if t.get('profit', 0) > 0)
            win_rate = winners / total if total > 0 else 0
            avg_profit = sum(t.get('profit', 0) for t in regime_trades) / total if total > 0 else 0
            
            regimes[regime] = {
                "trades": total,
                "win_rate": win_rate,
                "avg_profit": avg_profit
            }
            
        return regimes
        
    def _get_sector_performance(self) -> Dict[str, any]:
        """
        Get performance breakdown by sector.
        
        Returns:
            Dictionary with sector performance metrics
        """
        sectors = {}
        
        # Group trades by sector
        sector_trades = {}
        for trade in self.historical_trades:
            sector = trade.get('sector', 'Unknown')
            if sector not in sector_trades:
                sector_trades[sector] = []
            sector_trades[sector].append(trade)
            
        # Calculate metrics for each sector
        for sector, trades in sector_trades.items():
            total = len(trades)
            winners = sum(1 for t in trades if t.get('profit', 0) > 0)
            win_rate = winners / total if total > 0 else 0
            avg_profit = sum(t.get('profit', 0) for t in trades) / total if total > 0 else 0
            
            sectors[sector] = {
                "trades": total,
                "win_rate": win_rate,
                "avg_profit": avg_profit
            }
            
        return sectors 