from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import datetime
from ..base_generator import BaseContentGenerator
import ta

class MarketAnalysisGenerator(BaseContentGenerator):
    """
    Generates market analysis content based on technical indicators and market data.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the market analysis generator.
        
        Args:
            config (Dict): Generator configuration including:
                - model_name: str (default: 'gpt-4')
                - temperature: float (default: 0.7)
                - max_tokens: int (default: 1000)
                - rsi_period: int (default: 14)
                - ma_periods: list (default: [20, 50, 200])
        """
        super().__init__(config)
        self.rsi_period = config.get('rsi_period', 14)
        self.ma_periods = config.get('ma_periods', [20, 50, 200])
        
    def generate_content(self, data: pd.DataFrame, context: Optional[Dict] = None) -> str:
        """
        Generate market analysis content.
        
        Args:
            data (pd.DataFrame): Market data with OHLCV columns
            context (Optional[Dict]): Additional context for content generation
            
        Returns:
            str: Generated market analysis content
        """
        # Calculate technical indicators
        analysis = self._analyze_market_data(data)
        
        # Prepare prompt with analysis results
        prompt = self._format_prompt(analysis, context)
        
        # Generate content using the base generator
        content = super().generate_content(prompt)
        
        return content
    
    def _analyze_market_data(self, data: pd.DataFrame) -> Dict:
        """
        Analyze market data using technical indicators.
        
        Args:
            data (pd.DataFrame): Market data with OHLCV columns
            
        Returns:
            Dict: Analysis results
        """
        # Calculate RSI
        data['rsi'] = ta.momentum.rsi(data['close'], self.rsi_period)
        
        # Calculate moving averages
        for period in self.ma_periods:
            data[f'ma_{period}'] = ta.trend.sma_indicator(data['close'], period)
        
        # Calculate MACD
        macd = ta.trend.macd_diff(data['close'])
        data['macd'] = macd
        
        # Calculate Bollinger Bands
        bollinger = ta.volatility.BollingerBands(data['close'])
        data['bb_upper'] = bollinger.bollinger_hband()
        data['bb_lower'] = bollinger.bollinger_lband()
        
        # Get latest values
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        # Determine trend
        trend = self._determine_trend(data)
        
        # Identify key levels
        key_levels = self._identify_key_levels(data)
        
        return {
            'current_price': latest['close'],
            'rsi': latest['rsi'],
            'macd': latest['macd'],
            'trend': trend,
            'key_levels': key_levels,
            'moving_averages': {
                f'ma_{period}': latest[f'ma_{period}']
                for period in self.ma_periods
            },
            'bollinger_bands': {
                'upper': latest['bb_upper'],
                'lower': latest['bb_lower']
            },
            'price_change_24h': self._calculate_price_change(data),
            'volume_change_24h': self._calculate_volume_change(data)
        }
    
    def _determine_trend(self, data: pd.DataFrame) -> str:
        """
        Determine the current market trend.
        
        Args:
            data (pd.DataFrame): Market data with OHLCV columns
            
        Returns:
            str: Trend description
        """
        latest = data.iloc[-1]
        
        # Check moving average alignment
        ma_aligned = all(
            latest[f'ma_{period}'] > latest[f'ma_{self.ma_periods[i-1]}']
            for i, period in enumerate(self.ma_periods[1:], 1)
        )
        
        # Check price position relative to MAs
        price_above_ma = all(
            latest['close'] > latest[f'ma_{period}']
            for period in self.ma_periods
        )
        
        if ma_aligned and price_above_ma:
            return 'strong_uptrend'
        elif ma_aligned:
            return 'uptrend'
        elif price_above_ma:
            return 'weak_uptrend'
        else:
            return 'downtrend'
    
    def _identify_key_levels(self, data: pd.DataFrame) -> Dict:
        """
        Identify key support and resistance levels.
        
        Args:
            data (pd.DataFrame): Market data with OHLCV columns
            
        Returns:
            Dict: Key price levels
        """
        # Use recent highs and lows
        recent_highs = data['high'].rolling(window=20).max().iloc[-1]
        recent_lows = data['low'].rolling(window=20).min().iloc[-1]
        
        # Use Bollinger Bands
        bb_upper = data['bb_upper'].iloc[-1]
        bb_lower = data['bb_lower'].iloc[-1]
        
        return {
            'support': [recent_lows, bb_lower],
            'resistance': [recent_highs, bb_upper]
        }
    
    def _calculate_price_change(self, data: pd.DataFrame) -> float:
        """
        Calculate 24-hour price change percentage.
        
        Args:
            data (pd.DataFrame): Market data with OHLCV columns
            
        Returns:
            float: Price change percentage
        """
        if len(data) >= 24:
            current_price = data['close'].iloc[-1]
            price_24h_ago = data['close'].iloc[-24]
            return ((current_price - price_24h_ago) / price_24h_ago) * 100
        return 0.0
    
    def _calculate_volume_change(self, data: pd.DataFrame) -> float:
        """
        Calculate 24-hour volume change percentage.
        
        Args:
            data (pd.DataFrame): Market data with OHLCV columns
            
        Returns:
            float: Volume change percentage
        """
        if len(data) >= 24:
            current_volume = data['volume'].iloc[-1]
            volume_24h_ago = data['volume'].iloc[-24]
            return ((current_volume - volume_24h_ago) / volume_24h_ago) * 100
        return 0.0
    
    def _format_prompt(self, analysis: Dict, context: Optional[Dict] = None) -> str:
        """
        Format the prompt for content generation.
        
        Args:
            analysis (Dict): Market analysis results
            context (Optional[Dict]): Additional context
            
        Returns:
            str: Formatted prompt
        """
        prompt = f"""
        Generate a comprehensive market analysis based on the following data:
        
        Current Price: ${analysis['current_price']:,.2f}
        24h Change: {analysis['price_change_24h']:.2f}%
        24h Volume Change: {analysis['volume_change_24h']:.2f}%
        
        Technical Indicators:
        - RSI: {analysis['rsi']:.2f}
        - MACD: {analysis['macd']:.2f}
        - Moving Averages:
        {chr(10).join(f'  - {period}MA: ${value:,.2f}' for period, value in analysis['moving_averages'].items())}
        
        Market Structure:
        - Trend: {analysis['trend'].replace('_', ' ').title()}
        - Key Support Levels: ${', '.join(f'{level:,.2f}' for level in analysis['key_levels']['support'])}
        - Key Resistance Levels: ${', '.join(f'{level:,.2f}' for level in analysis['key_levels']['resistance'])}
        
        Please provide:
        1. A brief market overview
        2. Technical analysis interpretation
        3. Key support and resistance levels
        4. Short-term outlook
        5. Risk factors to consider
        """
        
        if context:
            prompt += f"\n\nAdditional Context:\n{context.get('additional_info', '')}"
        
        return prompt 