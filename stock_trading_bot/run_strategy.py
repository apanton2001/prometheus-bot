import pandas as pd
import numpy as np
import argparse
import logging
import os
import json
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import time
from typing import Dict, List, Tuple, Union, Optional

from sp500_strategy import SP500Strategy
from stock_data_handler import StockDataHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("sp500_strategy.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('run_strategy')

class StrategyRunner:
    """
    Runs the S&P 500 trading strategy in either backtest or live mode.
    """
    
    def __init__(
        self,
        symbols: List[str] = None,
        timeframes: List[str] = ['15m', '1h', '4h', '1d'],
        data_dir: str = 'data',
        backtest_days: int = 180,
        initial_capital: float = 100000.0,
        max_positions: int = 5,
        risk_per_trade: float = 0.01,
        live_mode: bool = False,
        update_interval: int = 3600  # 1 hour in seconds
    ):
        """
        Initialize the strategy runner.
        
        Args:
            symbols: List of stock symbols to trade (if None, uses top S&P 500)
            timeframes: List of timeframes to analyze
            data_dir: Directory to store data
            backtest_days: Number of days to backtest
            initial_capital: Initial capital for backtesting
            max_positions: Maximum number of concurrent positions
            risk_per_trade: Maximum risk per trade (as decimal of portfolio)
            live_mode: Whether to run in live mode
            update_interval: Data update interval in seconds (live mode only)
        """
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize data handler
        self.data_handler = StockDataHandler(
            symbols=symbols if symbols else [],
            timeframes=timeframes,
            data_dir=data_dir,
            use_cache=True
        )
        
        # If no symbols provided, use top S&P 500 components
        if not symbols:
            self.symbols = self.data_handler.get_sp500_symbols()[:50]  # Start with top 50 by market cap
            logger.info(f"Using top 50 S&P 500 symbols")
        else:
            self.symbols = symbols
            
        # Update data handler symbols
        self.data_handler.symbols = self.symbols
        
        # Initialize strategy
        self.strategy = SP500Strategy(
            symbols=self.symbols,
            timeframes=timeframes,
            risk_per_trade=risk_per_trade,
            max_open_positions=max_positions
        )
        
        # Runner parameters
        self.timeframes = timeframes
        self.data_dir = data_dir
        self.backtest_days = backtest_days
        self.initial_capital = initial_capital
        self.portfolio_value = initial_capital
        self.live_mode = live_mode
        self.update_interval = update_interval
        
        # Performance tracking
        self.portfolio_history = []
        self.trades_history = []
        self.performance_metrics = {}
        
        logger.info(f"Initialized StrategyRunner with {len(self.symbols)} symbols in {'live' if live_mode else 'backtest'} mode")
        
    def download_data(self) -> None:
        """
        Download all necessary data for the strategy.
        """
        logger.info("Starting data download")
        
        # Download stock data
        self.data_handler.download_all_data()
        
        # Download sector data
        self.data_handler.download_sector_data()
        
        # Download macro data
        self.data_handler.download_macro_data()
        
        logger.info("Data download complete")
        
    def load_data_to_strategy(self) -> None:
        """
        Load all data to the strategy.
        """
        logger.info("Loading data to strategy")
        
        # Load stock data
        for symbol in self.symbols:
            for timeframe in self.timeframes:
                df = self.data_handler.get_data(symbol, timeframe)
                if df is not None:
                    # Preprocess data
                    df = self.data_handler.preprocess_data(df)
                    self.strategy.load_data(symbol, timeframe, df)
        
        # Load sector data
        sector_data = self.data_handler.get_sector_data()
        self.strategy.load_sector_data(sector_data)
        
        # Load macro data
        macro_data = self.data_handler.get_macro_data()
        self.strategy.load_macro_data(macro_data)
        
        logger.info("Data loading complete")
        
    def run_backtest(self) -> Dict[str, any]:
        """
        Run a backtest of the strategy.
        
        Returns:
            Dictionary with backtest results
        """
        logger.info(f"Starting backtest with {self.backtest_days} days of data")
        
        # Download data if necessary
        self.download_data()
        
        # Initialize backtest parameters
        start_date = None
        end_date = None
        
        # Find the common date range for all symbols on the daily timeframe
        date_ranges = {}
        for symbol in self.symbols:
            df = self.data_handler.get_data(symbol, '1d')
            if df is not None and not df.empty:
                date_ranges[symbol] = (df.index.min(), df.index.max())
        
        # Find the common date range
        if date_ranges:
            latest_start = max([start for start, _ in date_ranges.values()])
            earliest_end = min([end for _, end in date_ranges.values()])
            
            # Adjust start date based on backtest_days
            if earliest_end - timedelta(days=self.backtest_days) > latest_start:
                start_date = earliest_end - timedelta(days=self.backtest_days)
            else:
                start_date = latest_start
                
            end_date = earliest_end
            
            logger.info(f"Backtest date range: {start_date} to {end_date}")
        else:
            logger.error("No data available for backtesting")
            return {"error": "No data available"}
        
        # Set initial portfolio value
        self.strategy.update_portfolio_value(self.initial_capital)
        self.portfolio_value = self.initial_capital
        
        # Prepare data slices for backtesting
        data_slices = self._prepare_backtest_data(start_date, end_date)
        
        # Run backtest
        for date, data in data_slices.items():
            logger.info(f"Processing backtest date: {date}")
            
            # Update strategy data
            for symbol, timeframe_data in data.items():
                for timeframe, df in timeframe_data.items():
                    self.strategy.load_data(symbol, timeframe, df)
            
            # Run strategy
            signals = self.strategy.run_strategy()
            
            # Execute trades
            executed_trades = self.strategy.execute_trades(signals)
            
            # Track trades
            for trade in executed_trades:
                self.trades_history.append({
                    **trade,
                    'date': date
                })
            
            # Update portfolio value (simplified for backtest)
            # In a real scenario, this would calculate based on actual price movements
            self._update_portfolio_value(date)
            
            # Track portfolio history
            self.portfolio_history.append({
                'date': date,
                'value': self.portfolio_value,
                'open_positions': len(self.strategy.open_positions)
            })
        
        # Calculate performance metrics
        self.performance_metrics = self._calculate_performance_metrics()
        
        logger.info(f"Backtest complete: {len(self.trades_history)} trades executed")
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'initial_capital': self.initial_capital,
            'final_value': self.portfolio_value,
            'return': (self.portfolio_value / self.initial_capital - 1) * 100,
            'trades': len(self.trades_history),
            'metrics': self.performance_metrics
        }
    
    def _prepare_backtest_data(self, start_date, end_date):
        """
        Prepare data slices for backtesting.
        Each slice represents a point in time with all available data up to that point.
        
        Args:
            start_date: Start date for backtest
            end_date: End date for backtest
            
        Returns:
            Dictionary mapping dates to data slices
        """
        # Create a list of daily dates for backtest
        date_range = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # Prepare data slices
        data_slices = {}
        
        for date in date_range:
            date_str = date.strftime('%Y-%m-%d')
            data_slices[date_str] = {}
            
            for symbol in self.symbols:
                data_slices[date_str][symbol] = {}
                
                for timeframe in self.timeframes:
                    df = self.data_handler.get_data(symbol, timeframe)
                    if df is not None and not df.empty:
                        # Get data up to current date
                        df_slice = df[df.index <= date]
                        if not df_slice.empty:
                            data_slices[date_str][symbol][timeframe] = df_slice
        
        return data_slices
    
    def _update_portfolio_value(self, date):
        """
        Update portfolio value based on open positions.
        This is a simplified implementation for backtesting.
        
        Args:
            date: Current date
        """
        # Start with cash
        new_value = self.strategy.available_capital
        
        # Add value of open positions
        for symbol, position in self.strategy.open_positions.items():
            # Get current price
            df = self.data_handler.get_data(symbol, '1d')
            if df is not None and not df.empty:
                price_data = df[df.index <= pd.Timestamp(date)]
                if not price_data.empty:
                    current_price = price_data['close'].iloc[-1]
                    position_value = position['size'] * self.portfolio_value
                    
                    # Apply simple P&L based on price movement
                    if 'entry_price' in position and position['entry_price'] is not None:
                        price_change = (current_price / position['entry_price'] - 1)
                        if position['direction'] == 'short':
                            price_change = -price_change
                            
                        position_value *= (1 + price_change)
                    
                    new_value += position_value
        
        # Update portfolio value
        self.portfolio_value = new_value
        self.strategy.update_portfolio_value(new_value)
    
    def _calculate_performance_metrics(self):
        """
        Calculate performance metrics for the backtest.
        
        Returns:
            Dictionary with performance metrics
        """
        # Extract portfolio values
        if not self.portfolio_history:
            return {}
            
        values = [entry['value'] for entry in self.portfolio_history]
        dates = [entry['date'] for entry in self.portfolio_history]
        
        # Calculate returns
        returns = [values[i] / values[i-1] - 1 for i in range(1, len(values))]
        daily_returns = pd.Series(returns)
        
        # Calculate metrics
        total_return = (values[-1] / values[0] - 1) * 100
        annualized_return = ((1 + total_return / 100) ** (365 / len(values)) - 1) * 100
        
        # Volatility
        volatility = daily_returns.std() * (252 ** 0.5) * 100  # Annualized
        
        # Drawdown
        cumulative = (1 + daily_returns).cumprod()
        drawdown = 1 - cumulative / cumulative.cummax()
        max_drawdown = drawdown.max() * 100
        
        # Sharpe ratio (assuming risk-free rate of 0 for simplicity)
        sharpe_ratio = annualized_return / volatility if volatility > 0 else 0
        
        # Win rate
        if self.trades_history:
            profitable_trades = sum(1 for trade in self.trades_history if trade.get('profit', 0) > 0)
            win_rate = profitable_trades / len(self.trades_history) * 100
        else:
            win_rate = 0
        
        return {
            'total_return': total_return,
            'annualized_return': annualized_return,
            'volatility': volatility,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'win_rate': win_rate,
            'trade_count': len(self.trades_history)
        }
    
    def run_live(self) -> None:
        """
        Run the strategy in live mode.
        """
        if not self.live_mode:
            logger.warning("Not in live mode. Use run_backtest() instead.")
            return
        
        logger.info("Starting strategy in live mode")
        
        # Initialize portfolio value
        self.strategy.update_portfolio_value(self.initial_capital)
        
        # Main live loop
        try:
            while True:
                logger.info(f"Running strategy update at {datetime.now()}")
                
                # Download latest data
                self.download_data()
                
                # Load data to strategy
                self.load_data_to_strategy()
                
                # Run strategy
                signals = self.strategy.run_strategy()
                
                # Execute trades
                executed_trades = self.strategy.execute_trades(signals)
                
                # Log trades
                for trade in executed_trades:
                    logger.info(f"Executed trade: {trade}")
                    self.trades_history.append({
                        **trade,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
                
                # Wait for next update
                logger.info(f"Waiting for {self.update_interval} seconds until next update")
                time.sleep(self.update_interval)
                
        except KeyboardInterrupt:
            logger.info("Live mode terminated by user")
        except Exception as e:
            logger.error(f"Error in live mode: {e}")
    
    def plot_results(self, save_path: str = None) -> None:
        """
        Plot backtest results.
        
        Args:
            save_path: Path to save the plot (if None, shows the plot)
        """
        if not self.portfolio_history:
            logger.warning("No portfolio history to plot")
            return
        
        # Create figure
        plt.figure(figsize=(14, 10))
        
        # Plot portfolio value
        dates = [pd.Timestamp(entry['date']) for entry in self.portfolio_history]
        values = [entry['value'] for entry in self.portfolio_history]
        
        plt.subplot(3, 1, 1)
        plt.plot(dates, values, label='Portfolio Value')
        plt.title('S&P 500 Strategy Backtest Results')
        plt.ylabel('Portfolio Value ($)')
        plt.grid(True)
        plt.legend()
        
        # Plot drawdown
        returns = pd.Series([values[i] / values[i-1] - 1 for i in range(1, len(values))], index=dates[1:])
        cumulative = (1 + returns).cumprod()
        drawdown = 1 - cumulative / cumulative.cummax()
        
        plt.subplot(3, 1, 2)
        plt.plot(drawdown.index, drawdown * 100)
        plt.fill_between(drawdown.index, drawdown * 100, 0, alpha=0.3, color='red')
        plt.title('Drawdown (%)')
        plt.ylabel('Drawdown (%)')
        plt.grid(True)
        
        # Plot trade points
        plt.subplot(3, 1, 3)
        plt.plot(dates, values, color='gray', alpha=0.6)
        
        # Plot entry points
        entry_dates = [pd.Timestamp(trade['date']) for trade in self.trades_history if trade['action'] == 'entry']
        entry_values = [values[dates.index(date)] if date in dates else None for date in entry_dates]
        entry_values = [v for v in entry_values if v is not None]
        entry_dates = [date for i, date in enumerate(entry_dates) if entry_values[i] is not None]
        
        if entry_dates:
            plt.scatter(entry_dates, entry_values, color='green', marker='^', s=100, label='Entry')
        
        # Plot exit points
        exit_dates = [pd.Timestamp(trade['date']) for trade in self.trades_history if trade['action'] == 'exit']
        exit_values = [values[dates.index(date)] if date in dates else None for date in exit_dates]
        exit_values = [v for v in exit_values if v is not None]
        exit_dates = [date for i, date in enumerate(exit_dates) if exit_values[i] is not None]
        
        if exit_dates:
            plt.scatter(exit_dates, exit_values, color='red', marker='v', s=100, label='Exit')
        
        plt.title('Trades')
        plt.ylabel('Portfolio Value ($)')
        plt.grid(True)
        plt.legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path)
            logger.info(f"Saved plot to {save_path}")
        else:
            plt.show()
    
    def save_results(self, path: str) -> None:
        """
        Save backtest results to a file.
        
        Args:
            path: Path to save results
        """
        results = {
            'portfolio_history': self.portfolio_history,
            'trades_history': self.trades_history,
            'performance_metrics': self.performance_metrics,
            'parameters': {
                'symbols': self.symbols[:10] + ['...'] if len(self.symbols) > 10 else self.symbols,  # Truncate for readability
                'timeframes': self.timeframes,
                'initial_capital': self.initial_capital,
                'backtest_days': self.backtest_days
            }
        }
        
        with open(path, 'w') as f:
            json.dump(results, f, indent=4, default=str)
            
        logger.info(f"Saved results to {path}")

# Command-line interface
def main():
    parser = argparse.ArgumentParser(description='Run S&P 500 trading strategy')
    parser.add_argument('--mode', type=str, choices=['backtest', 'live'], default='backtest', help='Running mode')
    parser.add_argument('--symbols', type=str, nargs='+', help='Symbols to trade (default: top S&P 500)')
    parser.add_argument('--timeframes', type=str, nargs='+', default=['15m', '1h', '4h', '1d'], help='Timeframes to analyze')
    parser.add_argument('--data-dir', type=str, default='../data', help='Data directory')
    parser.add_argument('--backtest-days', type=int, default=180, help='Number of days to backtest')
    parser.add_argument('--initial-capital', type=float, default=100000.0, help='Initial capital for backtesting')
    parser.add_argument('--max-positions', type=int, default=5, help='Maximum number of concurrent positions')
    parser.add_argument('--risk-per-trade', type=float, default=0.01, help='Maximum risk per trade')
    parser.add_argument('--update-interval', type=int, default=3600, help='Data update interval in seconds (live mode only)')
    parser.add_argument('--save-results', type=str, help='Path to save results')
    parser.add_argument('--save-plot', type=str, help='Path to save plot')
    
    args = parser.parse_args()
    
    # Initialize runner
    runner = StrategyRunner(
        symbols=args.symbols,
        timeframes=args.timeframes,
        data_dir=args.data_dir,
        backtest_days=args.backtest_days,
        initial_capital=args.initial_capital,
        max_positions=args.max_positions,
        risk_per_trade=args.risk_per_trade,
        live_mode=(args.mode == 'live'),
        update_interval=args.update_interval
    )
    
    # Run strategy
    if args.mode == 'backtest':
        results = runner.run_backtest()
        print(f"Backtest results:")
        for key, value in results.items():
            if key != 'metrics':
                print(f"  {key}: {value}")
        
        print("Performance metrics:")
        for key, value in results.get('metrics', {}).items():
            print(f"  {key}: {value:.2f}")
        
        # Plot results
        runner.plot_results(args.save_plot)
        
        # Save results
        if args.save_results:
            runner.save_results(args.save_results)
    else:
        runner.run_live()

if __name__ == "__main__":
    main() 