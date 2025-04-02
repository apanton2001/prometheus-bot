import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# Import our enhanced strategy
from enhanced_ma_strategy import EnhancedMAStrategy

# Create a class to simplify testing
class StrategyTester:
    def __init__(self, strategy_class, data_path, pairs):
        self.strategy = strategy_class()
        self.data_path = data_path
        self.pairs = pairs
        self.results = {}
        
    def load_data(self):
        """Load data for each pair"""
        self.data = {}
        for pair in self.pairs:
            filename = pair.replace('/', '_')
            file_path = os.path.join(self.data_path, f"{filename}-5m.csv")
            if os.path.exists(file_path):
                print(f"Loading data for {pair} from {file_path}")
                df = pd.read_csv(file_path, index_col='date', parse_dates=True)
                self.data[pair] = df
            else:
                print(f"Warning: Data file not found for {pair} at {file_path}")
        
        return len(self.data) > 0
    
    def test_strategy(self):
        """Test strategy on each pair"""
        if not self.data:
            return False
            
        for pair, df in self.data.items():
            print(f"\nTesting strategy on {pair}...")
            
            # Copy the dataframe to avoid modifying original data
            dataframe = df.copy()
            
            # Apply strategy indicators
            dataframe = self.strategy.populate_indicators(dataframe, {'pair': pair})
            
            # Apply entry/exit logic
            dataframe = self.strategy.populate_entry_trend(dataframe, {'pair': pair})
            dataframe = self.strategy.populate_exit_trend(dataframe, {'pair': pair})
            
            # Calculate trades and returns with improved risk management
            initial_balance = 1000.0  # Start with $1000
            balance = initial_balance
            position = 0
            entry_price = 0
            trades = []
            balance_history = [balance]
            drawdown = 0
            peak_balance = initial_balance
            highest_price_since_entry = 0
            trade_risk = 0.02  # 2% risk per trade
            
            for i in range(1, len(dataframe)):
                # Get current row data
                current = dataframe.iloc[i]
                prev_row = dataframe.iloc[i-1]
                
                # Update peak balance
                if balance > peak_balance:
                    peak_balance = balance
                
                # Calculate current drawdown if in a position
                if position > 0:
                    current_value = position * current['close']
                    if current_value < peak_balance:
                        drawdown = (peak_balance - current_value) / peak_balance
                
                # Check for entry signal if not in a position
                if position == 0 and current.get('enter_long', 0) == 1:
                    # Calculate position size based on risk and volatility
                    atr = current['atr']
                    position_size = self.strategy.calculate_position_size(balance, current['close'], atr)
                    
                    # Enter position
                    entry_price = current['close']
                    position = position_size
                    trade_cost = position * entry_price
                    balance -= trade_cost
                    
                    # Track highest price for trailing stop
                    highest_price_since_entry = entry_price
                    
                    trades.append({
                        'type': 'entry',
                        'time': dataframe.index[i],
                        'price': entry_price,
                        'position': position,
                        'balance': balance,
                        'trade_value': trade_cost
                    })
                    print(f"ENTRY at {dataframe.index[i]} price: ${entry_price:.2f}, position: {position:.6f}, value: ${trade_cost:.2f}")
                
                # Update highest price if in a position (for trailing stop)
                elif position > 0:
                    if current['close'] > highest_price_since_entry:
                        highest_price_since_entry = current['close']
                    
                    # Check for trailing stop hit
                    stop_triggered, stop_price = self.strategy.trailing_stop(
                        entry_price, current['close'], highest_price_since_entry
                    )
                    
                    # Exit on trailing stop or exit signal
                    if stop_triggered or current.get('exit_long', 0) == 1:
                        # Exit position
                        exit_price = current['close']
                        trade_value = position * exit_price
                        balance += trade_value
                        profit_pct = (exit_price / entry_price - 1) * 100
                        
                        trades.append({
                            'type': 'exit',
                            'time': dataframe.index[i],
                            'price': exit_price,
                            'profit_pct': profit_pct,
                            'balance': balance,
                            'trade_value': trade_value,
                            'exit_reason': 'stop_loss' if stop_triggered else 'signal'
                        })
                        
                        exit_reason = 'STOP' if stop_triggered else 'SIGNAL'
                        print(f"EXIT ({exit_reason}) at {dataframe.index[i]} price: ${exit_price:.2f}, profit: {profit_pct:.2f}%, balance: ${balance:.2f}")
                        position = 0
                
                # Track balance history (for position, use the current market value)
                if position > 0:
                    current_value = position * current['close'] + balance
                    balance_history.append(current_value)
                else:
                    balance_history.append(balance)
                
                # Check max drawdown threshold and exit if exceeded
                if drawdown > self.strategy.max_drawdown and position > 0:
                    # Force exit position due to max drawdown
                    exit_price = current['close']
                    trade_value = position * exit_price
                    balance += trade_value
                    profit_pct = (exit_price / entry_price - 1) * 100
                    
                    trades.append({
                        'type': 'exit',
                        'time': dataframe.index[i],
                        'price': exit_price,
                        'profit_pct': profit_pct,
                        'balance': balance,
                        'trade_value': trade_value,
                        'exit_reason': 'max_drawdown'
                    })
                    
                    print(f"EXIT (MAX DRAWDOWN) at {dataframe.index[i]} price: ${exit_price:.2f}, profit: {profit_pct:.2f}%, balance: ${balance:.2f}")
                    position = 0
            
            # Close any open positions using the last price
            if position > 0:
                last_price = dataframe.iloc[-1]['close']
                trade_value = position * last_price
                balance += trade_value
                profit_pct = (last_price / entry_price - 1) * 100
                
                trades.append({
                    'type': 'exit_end',
                    'time': dataframe.index[-1],
                    'price': last_price,
                    'profit_pct': profit_pct,
                    'balance': balance,
                    'trade_value': trade_value,
                    'exit_reason': 'end_of_data'
                })
                
                print(f"FINAL EXIT at {dataframe.index[-1]} price: ${last_price:.2f}, profit: {profit_pct:.2f}%, balance: ${balance:.2f}")
            
            # Calculate overall statistics
            total_trades = len([t for t in trades if t['type'] == 'exit' or t['type'] == 'exit_end'])
            profitable_trades = len([t for t in trades if (t['type'] == 'exit' or t['type'] == 'exit_end') and t.get('profit_pct', 0) > 0])
            
            if total_trades > 0:
                win_rate = profitable_trades / total_trades * 100
                profit_trades = [t.get('profit_pct', 0) for t in trades if (t['type'] == 'exit' or t['type'] == 'exit_end') and t.get('profit_pct', 0) > 0]
                loss_trades = [abs(t.get('profit_pct', 0)) for t in trades if (t['type'] == 'exit' or t['type'] == 'exit_end') and t.get('profit_pct', 0) < 0]
                
                avg_profit = sum(profit_trades) / len(profit_trades) if profit_trades else 0
                avg_loss = sum(loss_trades) / len(loss_trades) if loss_trades else 0
                
                if avg_loss > 0:
                    profit_factor = avg_profit / avg_loss
                else:
                    profit_factor = float('inf')  # No losing trades
            else:
                win_rate = 0
                avg_profit = 0
                avg_loss = 0
                profit_factor = 0
                
            total_profit_pct = (balance / initial_balance - 1) * 100
            
            # Calculate max drawdown
            peak = initial_balance
            max_drawdown = 0
            
            for value in balance_history:
                if value > peak:
                    peak = value
                drawdown = (peak - value) / peak
                max_drawdown = max(max_drawdown, drawdown)
            
            # Calculate Sharpe Ratio (simplified)
            returns = []
            for i in range(1, len(balance_history)):
                daily_return = (balance_history[i] / balance_history[i-1]) - 1
                returns.append(daily_return)
            
            if returns:
                mean_return = np.mean(returns)
                std_return = np.std(returns)
                if std_return > 0:
                    sharpe_ratio = mean_return / std_return * np.sqrt(252)  # Annualized
                else:
                    sharpe_ratio = 0
            else:
                sharpe_ratio = 0
            
            print(f"\nResults for {pair}:")
            print(f"Initial balance: ${initial_balance:.2f}")
            print(f"Final balance: ${balance:.2f}")
            print(f"Total profit: {total_profit_pct:.2f}%")
            print(f"Total trades: {total_trades}")
            print(f"Profitable trades: {profitable_trades}")
            print(f"Win rate: {win_rate:.2f}%")
            print(f"Average profit: {avg_profit:.2f}%")
            print(f"Average loss: {avg_loss:.2f}%")
            print(f"Profit factor: {profit_factor:.2f}")
            print(f"Maximum drawdown: {max_drawdown*100:.2f}%")
            print(f"Sharpe ratio: {sharpe_ratio:.2f}")
            
            # Store results
            self.results[pair] = {
                'initial_balance': initial_balance,
                'final_balance': balance,
                'total_profit_pct': total_profit_pct,
                'total_trades': total_trades,
                'profitable_trades': profitable_trades,
                'win_rate': win_rate,
                'avg_profit': avg_profit,
                'avg_loss': avg_loss,
                'profit_factor': profit_factor,
                'max_drawdown': max_drawdown,
                'sharpe_ratio': sharpe_ratio,
                'trades': trades,
                'balance_history': balance_history,
                'dataframe': dataframe
            }
            
        return True
    
    def plot_results(self, pair):
        """Plot the strategy results for a specific pair"""
        if pair not in self.results:
            print(f"No results found for {pair}")
            return
            
        results = self.results[pair]
        dataframe = results['dataframe']
        
        # Create a figure with 3 subplots - price chart, indicators, and balance
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(15, 15), sharex=True)
        
        # Plot the price and moving averages
        ax1.plot(dataframe.index, dataframe['close'], label='Close Price', color='black', alpha=0.6)
        ax1.plot(dataframe.index, dataframe['fast_ma'], label=f'Fast MA ({self.strategy.fast_ma_period})', color='blue')
        ax1.plot(dataframe.index, dataframe['medium_ma'], label=f'Medium MA ({self.strategy.medium_ma_period})', color='green')
        ax1.plot(dataframe.index, dataframe['slow_ma'], label=f'Slow MA ({self.strategy.slow_ma_period})', color='red')
        
        # Plot Bollinger Bands
        ax1.plot(dataframe.index, dataframe['bb_upper'], 'k--', alpha=0.3)
        ax1.plot(dataframe.index, dataframe['bb_middle'], 'k--', alpha=0.3)
        ax1.plot(dataframe.index, dataframe['bb_lower'], 'k--', alpha=0.3)
        
        ax1.set_title(f'Price Chart and Strategy Performance for {pair}')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True)
        
        # Add buy and sell markers
        for trade in results['trades']:
            if trade['type'] == 'entry':
                ax1.scatter(trade['time'], trade['price'], color='green', marker='^', s=100)
            elif trade['type'] in ['exit', 'exit_end']:
                exit_color = 'red'
                if trade.get('exit_reason') == 'stop_loss':
                    exit_color = 'purple'
                elif trade.get('exit_reason') == 'max_drawdown':
                    exit_color = 'black'
                    
                ax1.scatter(trade['time'], trade['price'], color=exit_color, marker='v', s=100)
        
        # Plot indicators (ADX and RSI)
        ax2.plot(dataframe.index, dataframe['adx'], label='ADX', color='purple')
        ax2.axhline(y=self.strategy.adx_threshold, color='purple', linestyle='--', alpha=0.3)
        ax2.plot(dataframe.index, dataframe['rsi'], label='RSI', color='orange')
        ax2.axhline(y=30, color='orange', linestyle='--', alpha=0.3)
        ax2.axhline(y=70, color='orange', linestyle='--', alpha=0.3)
        
        # Plot volume
        volume_color = np.where(dataframe['volume_ratio'] > self.strategy.volume_factor, 'green', 'gray')
        ax2.bar(dataframe.index, dataframe['volume_ratio'], label='Volume Ratio', color=volume_color, alpha=0.3)
        ax2.axhline(y=self.strategy.volume_factor, color='blue', linestyle='--', alpha=0.3)
        
        ax2.set_title(f'Technical Indicators')
        ax2.set_ylabel('Value')
        ax2.legend()
        ax2.grid(True)
        
        # Plot the balance
        ax3.plot(dataframe.index, results['balance_history'], label='Account Balance', color='blue')
        
        # Calculate and plot drawdown
        balance_hist = np.array(results['balance_history'])
        peak = np.maximum.accumulate(balance_hist)
        drawdown = (peak - balance_hist) / peak
        ax3.fill_between(dataframe.index, 0, drawdown * 100, alpha=0.3, color='red', label='Drawdown %')
        
        ax3.set_title(f'Account Balance and Drawdown')
        ax3.set_xlabel('Date')
        ax3.set_ylabel('Balance / Drawdown %')
        ax3.legend()
        ax3.grid(True)
        
        # Add performance metrics as text
        metrics_text = (
            f"Total Profit: {results['total_profit_pct']:.2f}%\n"
            f"Win Rate: {results['win_rate']:.2f}%\n"
            f"Profit Factor: {results['profit_factor']:.2f}\n"
            f"Max Drawdown: {results['max_drawdown']*100:.2f}%\n"
            f"Sharpe Ratio: {results['sharpe_ratio']:.2f}"
        )
        fig.text(0.15, 0.01, metrics_text, ha='left', fontsize=12)
        
        plt.tight_layout()
        plt.subplots_adjust(bottom=0.1)
        
        # Save the figure
        output_dir = os.path.join(self.data_path, '../plots_enhanced')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{pair.replace('/', '_')}_enhanced_results.png")
        plt.savefig(output_file)
        print(f"Plot saved to {output_file}")
        
        plt.close(fig)


if __name__ == "__main__":
    # Test our EnhancedMAStrategy
    pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
    data_path = 'user_data/data/binance'
    
    print("Starting enhanced strategy test...")
    tester = StrategyTester(EnhancedMAStrategy, data_path, pairs)
    
    if tester.load_data():
        tester.test_strategy()
        
        # Plot results for each pair
        for pair in pairs:
            if pair in tester.results:
                tester.plot_results(pair)
    else:
        print("Failed to load data. Please check the data files exist at the specified path.")
    
    print("\nEnhanced strategy testing complete!") 