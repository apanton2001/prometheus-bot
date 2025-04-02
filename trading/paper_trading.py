from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
from .strategies.base_strategy import BaseStrategy

class PaperTrading:
    """
    Paper trading module for simulating trades without real money.
    """
    
    def __init__(self, initial_balance: float, strategy: BaseStrategy):
        """
        Initialize paper trading.
        
        Args:
            initial_balance (float): Initial account balance
            strategy (BaseStrategy): Trading strategy to use
        """
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.strategy = strategy
        self.positions: Dict[str, Dict] = {}
        self.trade_history: List[Dict] = []
        self.max_positions = 5  # Maximum number of concurrent positions
        
    def update_market_data(self, symbol: str, data: pd.DataFrame) -> Optional[Dict]:
        """
        Update market data and check for trading signals.
        
        Args:
            symbol (str): Trading pair symbol
            data (pd.DataFrame): Market data
            
        Returns:
            Optional[Dict]: Trading signal if conditions are met
        """
        # Generate trading signal
        signal = self.strategy.generate_signals(data)
        
        if signal and self.strategy.validate_signal(signal):
            # Calculate position size
            signal['size'] = self.strategy.calculate_position_size(signal, self.current_balance)
            
            # Check if we can open a new position
            if len(self.positions) < self.max_positions:
                return self._execute_trade(symbol, signal)
            
        return None
    
    def _execute_trade(self, symbol: str, signal: Dict) -> Dict:
        """
        Execute a paper trade.
        
        Args:
            symbol (str): Trading pair symbol
            signal (Dict): Trading signal
            
        Returns:
            Dict: Trade execution details
        """
        trade = {
            'symbol': symbol,
            'action': signal['action'],
            'price': signal['price'],
            'size': signal['size'],
            'timestamp': datetime.utcnow(),
            'stop_loss': signal['stop_loss'],
            'take_profit': signal['take_profit']
        }
        
        # Calculate trade value
        trade_value = trade['price'] * trade['size']
        
        if trade['action'] == 'buy':
            # Check if we have enough balance
            if trade_value <= self.current_balance:
                self.current_balance -= trade_value
                self.positions[symbol] = trade
                self.trade_history.append(trade)
                return trade
        else:  # sell
            # Check if we have the position
            if symbol in self.positions:
                position = self.positions[symbol]
                # Calculate P&L
                pnl = (trade['price'] - position['price']) * position['size']
                self.current_balance += trade_value + pnl
                del self.positions[symbol]
                trade['pnl'] = pnl
                self.trade_history.append(trade)
                return trade
        
        return None
    
    def check_positions(self, symbol: str, current_price: float) -> List[Dict]:
        """
        Check if any positions need to be closed based on stop-loss or take-profit.
        
        Args:
            symbol (str): Trading pair symbol
            current_price (float): Current market price
            
        Returns:
            List[Dict]: List of closed positions
        """
        closed_positions = []
        
        if symbol in self.positions:
            position = self.positions[symbol]
            
            # Check stop-loss
            if position['action'] == 'buy' and current_price <= position['stop_loss']:
                closed_positions.append(self._close_position(symbol, current_price, 'stop_loss'))
            
            # Check take-profit
            elif position['action'] == 'buy' and current_price >= position['take_profit']:
                closed_positions.append(self._close_position(symbol, current_price, 'take_profit'))
            
            # Check stop-loss for short positions
            elif position['action'] == 'sell' and current_price >= position['stop_loss']:
                closed_positions.append(self._close_position(symbol, current_price, 'stop_loss'))
            
            # Check take-profit for short positions
            elif position['action'] == 'sell' and current_price <= position['take_profit']:
                closed_positions.append(self._close_position(symbol, current_price, 'take_profit'))
        
        return closed_positions
    
    def _close_position(self, symbol: str, current_price: float, reason: str) -> Dict:
        """
        Close an existing position.
        
        Args:
            symbol (str): Trading pair symbol
            current_price (float): Current market price
            reason (str): Reason for closing the position
            
        Returns:
            Dict: Closed position details
        """
        position = self.positions[symbol]
        trade_value = current_price * position['size']
        
        # Calculate P&L
        if position['action'] == 'buy':
            pnl = (current_price - position['price']) * position['size']
        else:  # sell
            pnl = (position['price'] - current_price) * position['size']
        
        # Update balance
        self.current_balance += trade_value + pnl
        
        # Create close trade
        close_trade = {
            'symbol': symbol,
            'action': 'close',
            'price': current_price,
            'size': position['size'],
            'timestamp': datetime.utcnow(),
            'pnl': pnl,
            'reason': reason
        }
        
        # Update history and remove position
        self.trade_history.append(close_trade)
        del self.positions[symbol]
        
        return close_trade
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Get current position for a symbol.
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            Optional[Dict]: Position details if exists
        """
        return self.positions.get(symbol)
    
    def get_all_positions(self) -> Dict[str, Dict]:
        """
        Get all current positions.
        
        Returns:
            Dict[str, Dict]: All current positions
        """
        return self.positions
    
    def get_trade_history(self) -> List[Dict]:
        """
        Get trade history.
        
        Returns:
            List[Dict]: List of all trades
        """
        return self.trade_history
    
    def get_balance(self) -> float:
        """
        Get current account balance.
        
        Returns:
            float: Current balance
        """
        return self.current_balance
    
    def get_performance_metrics(self) -> Dict:
        """
        Calculate performance metrics.
        
        Returns:
            Dict: Performance metrics
        """
        if not self.trade_history:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'return_pct': 0
            }
        
        # Calculate metrics
        total_trades = len(self.trade_history)
        winning_trades = sum(1 for trade in self.trade_history if trade.get('pnl', 0) > 0)
        losing_trades = sum(1 for trade in self.trade_history if trade.get('pnl', 0) < 0)
        total_pnl = sum(trade.get('pnl', 0) for trade in self.trade_history)
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'return_pct': (total_pnl / self.initial_balance) * 100
        } 