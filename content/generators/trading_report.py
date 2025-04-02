from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
from ..base_generator import BaseContentGenerator

class TradingReportGenerator(BaseContentGenerator):
    """
    Generates trading reports and performance summaries.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize the trading report generator.
        
        Args:
            config (Dict): Generator configuration including:
                - model_name: str (default: 'gpt-4')
                - temperature: float (default: 0.7)
                - max_tokens: int (default: 1000)
        """
        super().__init__(config)
        
    def generate_daily_report(self, 
                            positions: Dict[str, Dict],
                            trade_history: List[Dict],
                            performance_metrics: Dict,
                            market_data: Optional[pd.DataFrame] = None) -> str:
        """
        Generate a daily trading report.
        
        Args:
            positions (Dict[str, Dict]): Current positions
            trade_history (List[Dict]): Trade history
            performance_metrics (Dict): Performance metrics
            market_data (Optional[pd.DataFrame]): Market data for analysis
            
        Returns:
            str: Generated report content
        """
        # Get today's trades
        today = datetime.utcnow().date()
        today_trades = [
            trade for trade in trade_history
            if trade['timestamp'].date() == today
        ]
        
        # Calculate daily metrics
        daily_metrics = self._calculate_daily_metrics(today_trades)
        
        # Prepare report data
        report_data = {
            'date': today,
            'positions': positions,
            'trades': today_trades,
            'daily_metrics': daily_metrics,
            'performance_metrics': performance_metrics,
            'market_data': market_data
        }
        
        # Generate report content
        prompt = self._format_report_prompt(report_data)
        content = super().generate_content(prompt)
        
        return content
    
    def generate_performance_report(self,
                                  trade_history: List[Dict],
                                  performance_metrics: Dict,
                                  market_data: Optional[pd.DataFrame] = None) -> str:
        """
        Generate a performance report.
        
        Args:
            trade_history (List[Dict]): Trade history
            performance_metrics (Dict): Performance metrics
            market_data (Optional[pd.DataFrame]): Market data for analysis
            
        Returns:
            str: Generated report content
        """
        # Calculate period metrics
        period_metrics = self._calculate_period_metrics(trade_history)
        
        # Prepare report data
        report_data = {
            'period': 'Overall',
            'trades': trade_history,
            'period_metrics': period_metrics,
            'performance_metrics': performance_metrics,
            'market_data': market_data
        }
        
        # Generate report content
        prompt = self._format_performance_prompt(report_data)
        content = super().generate_content(prompt)
        
        return content
    
    def _calculate_daily_metrics(self, trades: List[Dict]) -> Dict:
        """
        Calculate daily trading metrics.
        
        Args:
            trades (List[Dict]): List of trades for the day
            
        Returns:
            Dict: Daily metrics
        """
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'max_win': 0,
                'max_loss': 0
            }
        
        # Calculate metrics
        total_trades = len(trades)
        winning_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
        losing_trades = sum(1 for trade in trades if trade.get('pnl', 0) < 0)
        total_pnl = sum(trade.get('pnl', 0) for trade in trades)
        pnls = [trade.get('pnl', 0) for trade in trades]
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / total_trades if total_trades > 0 else 0,
            'max_win': max(pnls) if pnls else 0,
            'max_loss': min(pnls) if pnls else 0
        }
    
    def _calculate_period_metrics(self, trades: List[Dict]) -> Dict:
        """
        Calculate period trading metrics.
        
        Args:
            trades (List[Dict]): List of trades for the period
            
        Returns:
            Dict: Period metrics
        """
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'avg_pnl': 0,
                'max_win': 0,
                'max_loss': 0,
                'profit_factor': 0,
                'sharpe_ratio': 0
            }
        
        # Calculate basic metrics
        total_trades = len(trades)
        winning_trades = sum(1 for trade in trades if trade.get('pnl', 0) > 0)
        losing_trades = sum(1 for trade in trades if trade.get('pnl', 0) < 0)
        total_pnl = sum(trade.get('pnl', 0) for trade in trades)
        pnls = [trade.get('pnl', 0) for trade in trades]
        
        # Calculate profit factor
        gross_profit = sum(pnl for pnl in pnls if pnl > 0)
        gross_loss = abs(sum(pnl for pnl in pnls if pnl < 0))
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        
        # Calculate Sharpe ratio (assuming daily returns)
        returns = pd.Series(pnls).pct_change().dropna()
        sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(252) if len(returns) > 1 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': winning_trades / total_trades if total_trades > 0 else 0,
            'total_pnl': total_pnl,
            'avg_pnl': total_pnl / total_trades if total_trades > 0 else 0,
            'max_win': max(pnls) if pnls else 0,
            'max_loss': min(pnls) if pnls else 0,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio
        }
    
    def _format_report_prompt(self, data: Dict) -> str:
        """
        Format the daily report prompt.
        
        Args:
            data (Dict): Report data
            
        Returns:
            str: Formatted prompt
        """
        prompt = f"""
        Generate a comprehensive daily trading report based on the following data:
        
        Date: {data['date']}
        
        Current Positions:
        {self._format_positions(data['positions'])}
        
        Today's Trades:
        {self._format_trades(data['trades'])}
        
        Daily Performance:
        - Total Trades: {data['daily_metrics']['total_trades']}
        - Winning Trades: {data['daily_metrics']['winning_trades']}
        - Losing Trades: {data['daily_metrics']['losing_trades']}
        - Win Rate: {data['daily_metrics']['win_rate']:.2%}
        - Total P&L: ${data['daily_metrics']['total_pnl']:,.2f}
        - Average P&L: ${data['daily_metrics']['avg_pnl']:,.2f}
        - Max Win: ${data['daily_metrics']['max_win']:,.2f}
        - Max Loss: ${data['daily_metrics']['max_loss']:,.2f}
        
        Overall Performance:
        - Total Trades: {data['performance_metrics']['total_trades']}
        - Win Rate: {data['performance_metrics']['win_rate']:.2%}
        - Total P&L: ${data['performance_metrics']['total_pnl']:,.2f}
        - Return: {data['performance_metrics']['return_pct']:.2f}%
        
        Please provide:
        1. A summary of today's trading activity
        2. Analysis of current positions
        3. Performance analysis
        4. Risk assessment
        5. Recommendations for tomorrow
        """
        
        if data['market_data'] is not None:
            prompt += f"\n\nMarket Analysis:\n{self._format_market_data(data['market_data'])}"
        
        return prompt
    
    def _format_performance_prompt(self, data: Dict) -> str:
        """
        Format the performance report prompt.
        
        Args:
            data (Dict): Report data
            
        Returns:
            str: Formatted prompt
        """
        prompt = f"""
        Generate a comprehensive performance report based on the following data:
        
        Period: {data['period']}
        
        Trading Statistics:
        - Total Trades: {data['period_metrics']['total_trades']}
        - Winning Trades: {data['period_metrics']['winning_trades']}
        - Losing Trades: {data['period_metrics']['losing_trades']}
        - Win Rate: {data['period_metrics']['win_rate']:.2%}
        - Total P&L: ${data['period_metrics']['total_pnl']:,.2f}
        - Average P&L: ${data['period_metrics']['avg_pnl']:,.2f}
        - Max Win: ${data['period_metrics']['max_win']:,.2f}
        - Max Loss: ${data['period_metrics']['max_loss']:,.2f}
        - Profit Factor: {data['period_metrics']['profit_factor']:.2f}
        - Sharpe Ratio: {data['period_metrics']['sharpe_ratio']:.2f}
        
        Overall Performance:
        - Total Trades: {data['performance_metrics']['total_trades']}
        - Win Rate: {data['performance_metrics']['win_rate']:.2%}
        - Total P&L: ${data['performance_metrics']['total_pnl']:,.2f}
        - Return: {data['performance_metrics']['return_pct']:.2f}%
        
        Please provide:
        1. Overall performance analysis
        2. Trading strategy effectiveness
        3. Risk management assessment
        4. Areas for improvement
        5. Future recommendations
        """
        
        if data['market_data'] is not None:
            prompt += f"\n\nMarket Analysis:\n{self._format_market_data(data['market_data'])}"
        
        return prompt
    
    def _format_positions(self, positions: Dict[str, Dict]) -> str:
        """
        Format current positions for the report.
        
        Args:
            positions (Dict[str, Dict]): Current positions
            
        Returns:
            str: Formatted positions
        """
        if not positions:
            return "No open positions"
        
        formatted = []
        for symbol, position in positions.items():
            formatted.append(
                f"- {symbol}: {position['action'].upper()} @ ${position['price']:,.2f} "
                f"(SL: ${position['stop_loss']:,.2f}, TP: ${position['take_profit']:,.2f})"
            )
        
        return "\n".join(formatted)
    
    def _format_trades(self, trades: List[Dict]) -> str:
        """
        Format trades for the report.
        
        Args:
            trades (List[Dict]): List of trades
            
        Returns:
            str: Formatted trades
        """
        if not trades:
            return "No trades today"
        
        formatted = []
        for trade in trades:
            formatted.append(
                f"- {trade['symbol']}: {trade['action'].upper()} @ ${trade['price']:,.2f} "
                f"(P&L: ${trade.get('pnl', 0):,.2f})"
            )
        
        return "\n".join(formatted)
    
    def _format_market_data(self, data: pd.DataFrame) -> str:
        """
        Format market data for the report.
        
        Args:
            data (pd.DataFrame): Market data
            
        Returns:
            str: Formatted market data
        """
        if data is None or data.empty:
            return "No market data available"
        
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        return f"""
        Market Overview:
        - Current Price: ${latest['close']:,.2f}
        - 24h Change: {((latest['close'] - prev['close']) / prev['close'] * 100):.2f}%
        - 24h Volume: {latest['volume']:,.2f}
        - 24h High: ${latest['high']:,.2f}
        - 24h Low: ${latest['low']:,.2f}
        """ 