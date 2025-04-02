from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

class BaseStrategy(ABC):
    """
    Base class for all trading strategies.
    Defines the interface that all strategies must implement.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the strategy with configuration parameters.
        
        Args:
            config (Dict): Strategy configuration parameters
        """
        self.config = config
        self.name = self.__class__.__name__
        
        # Trading parameters
        self.risk_per_trade = config.get('risk_per_trade', 0.01)
        self.max_positions = config.get('max_positions', 5)
        self.stop_loss_pct = config.get('stop_loss_pct', 0.02)
        self.take_profit_pct = config.get('take_profit_pct', 0.04)
        
        # State tracking
        self.positions = {}
        self.orders = []
        self.trades = []
        
    @abstractmethod
    def analyze_market(self, data: pd.DataFrame) -> Dict:
        """
        Analyze market data and return analysis results.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            Dictionary with analysis results
        """
        pass
    
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        """
        Generate trading signals based on market analysis.
        
        Args:
            data: DataFrame with OHLCV data
            
        Returns:
            List of signal dictionaries
        """
        pass
    
    @abstractmethod
    def calculate_position_size(self, signal: Dict, portfolio_value: float) -> float:
        """
        Calculate position size based on signal and risk parameters.
        
        Args:
            signal: Signal dictionary
            portfolio_value: Current portfolio value
            
        Returns:
            Position size
        """
        pass
    
    def validate_signal(self, signal: Dict) -> bool:
        """
        Validate a trading signal.
        
        Args:
            signal: Signal dictionary
            
        Returns:
            True if signal is valid, False otherwise
        """
        required_fields = ['symbol', 'direction', 'price', 'timestamp']
        return all(field in signal for field in required_fields)
    
    def update_positions(self, positions: Dict) -> None:
        """
        Update current positions.
        
        Args:
            positions: Dictionary of current positions
        """
        self.positions = positions
    
    def add_trade(self, trade: Dict) -> None:
        """
        Add a trade to the history.
        
        Args:
            trade: Trade dictionary
        """
        self.trades.append({
            **trade,
            'strategy': self.name,
            'timestamp': datetime.now()
        })
    
    def get_performance_metrics(self) -> Dict:
        """
        Calculate strategy performance metrics.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'average_profit': 0,
                'max_drawdown': 0
            }
        
        total_trades = len(self.trades)
        winning_trades = sum(1 for t in self.trades if t.get('pnl', 0) > 0)
        
        profits = sum(t['pnl'] for t in self.trades if t.get('pnl', 0) > 0)
        losses = abs(sum(t['pnl'] for t in self.trades if t.get('pnl', 0) < 0))
        
        return {
            'total_trades': total_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'profit_factor': profits / losses if losses > 0 else float('inf'),
            'average_profit': (profits - losses) / total_trades if total_trades > 0 else 0,
            'max_drawdown': self._calculate_max_drawdown()
        }
    
    def _calculate_max_drawdown(self) -> float:
        """
        Calculate maximum drawdown from trade history.
        
        Returns:
            Maximum drawdown as a percentage
        """
        if not self.trades:
            return 0.0
            
        # Calculate cumulative PnL
        pnls = [t.get('pnl', 0) for t in self.trades]
        cumulative = np.cumsum(pnls)
        
        # Calculate drawdown
        peak = np.maximum.accumulate(cumulative)
        drawdown = (peak - cumulative) / peak
        
        return float(np.max(drawdown)) if len(drawdown) > 0 else 0.0 