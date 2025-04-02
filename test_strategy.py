import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta

# Import our simplified strategy
from simple_momentum_strategy import SimpleMomentumStrategy

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
            
            # Calculate trades and returns
            balance = 1000.0  # Start with $1000
            position = 0
            entry_price = 0
            trades = []
            balance_history = [balance]
            
            for i in range(1, len(dataframe)):
                # Get current row data
                current = dataframe.iloc[i]
                prev_balance = balance
                
                # Check for entry signal
                if position == 0 and current.get('enter_long', 0) == 1:
                    # Enter position
                    entry_price = current['close']
                    position = balance / entry_price
                    balance = 0
                    trades.append({
                        'type': 'entry',
                        'time': dataframe.index[i],
                        'price': entry_price,
                        'position': position
                    })
                    print(f"ENTRY at {dataframe.index[i]} price: ${entry_price:.2f}, position: {position:.6f}")
                
                # Check for exit signal
                elif position > 0 and current.get('exit_long', 0) == 1:
                    # Exit position
                    exit_price = current['close']
                    balance = position * exit_price
                    profit_pct = (exit_price / entry_price - 1) * 100
                    trades.append({
                        'type': 'exit',
                        'time': dataframe.index[i],
                        'price': exit_price,
                        'profit_pct': profit_pct,
                        'balance': balance
                    })
                    print(f"EXIT at {dataframe.index[i]} price: ${exit_price:.2f}, profit: {profit_pct:.2f}%, balance: ${balance:.2f}")
                    position = 0
                
                # Track balance history (for position, use the current market value)
                if position > 0:
                    current_value = position * current['close']
                    balance_history.append(current_value)
                else:
                    balance_history.append(balance)
            
            # Close any open positions using the last price
            if position > 0:
                last_price = dataframe.iloc[-1]['close']
                balance = position * last_price
                profit_pct = (last_price / entry_price - 1) * 100
                trades.append({
                    'type': 'exit_end',
                    'time': dataframe.index[-1],
                    'price': last_price,
                    'profit_pct': profit_pct,
                    'balance': balance
                })
                print(f"FINAL EXIT at {dataframe.index[-1]} price: ${last_price:.2f}, profit: {profit_pct:.2f}%, balance: ${balance:.2f}")
            
            # Calculate overall statistics
            total_trades = len([t for t in trades if t['type'] == 'exit' or t['type'] == 'exit_end'])
            profitable_trades = len([t for t in trades if (t['type'] == 'exit' or t['type'] == 'exit_end') and t.get('profit_pct', 0) > 0])
            
            if total_trades > 0:
                win_rate = profitable_trades / total_trades * 100
            else:
                win_rate = 0
                
            initial_balance = 1000.0
            total_profit_pct = (balance / initial_balance - 1) * 100
            
            print(f"\nResults for {pair}:")
            print(f"Initial balance: ${initial_balance:.2f}")
            print(f"Final balance: ${balance:.2f}")
            print(f"Total profit: {total_profit_pct:.2f}%")
            print(f"Total trades: {total_trades}")
            print(f"Profitable trades: {profitable_trades}")
            print(f"Win rate: {win_rate:.2f}%")
            
            # Store results
            self.results[pair] = {
                'initial_balance': initial_balance,
                'final_balance': balance,
                'total_profit_pct': total_profit_pct,
                'total_trades': total_trades,
                'profitable_trades': profitable_trades,
                'win_rate': win_rate,
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
        
        # Create a figure with 2 subplots - price chart and balance
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10), sharex=True)
        
        # Plot the price
        ax1.plot(dataframe.index, dataframe['close'], label='Close Price')
        ax1.set_title(f'Price Chart and Strategy Performance for {pair}')
        ax1.set_ylabel('Price')
        ax1.legend()
        ax1.grid(True)
        
        # Add buy and sell markers
        for trade in results['trades']:
            if trade['type'] == 'entry':
                ax1.scatter(trade['time'], trade['price'], color='green', marker='^', s=100)
            elif trade['type'] in ['exit', 'exit_end']:
                ax1.scatter(trade['time'], trade['price'], color='red', marker='v', s=100)
        
        # Plot the balance
        ax2.plot(dataframe.index, results['balance_history'], label='Account Balance')
        ax2.set_title(f'Account Balance Over Time')
        ax2.set_xlabel('Date')
        ax2.set_ylabel('Balance')
        ax2.legend()
        ax2.grid(True)
        
        # Add profit/loss information
        profit_text = f"Total Profit: {results['total_profit_pct']:.2f}%, Win Rate: {results['win_rate']:.2f}%"
        fig.text(0.5, 0.01, profit_text, ha='center', fontsize=12)
        
        plt.tight_layout()
        
        # Save the figure
        output_dir = os.path.join(self.data_path, '../plots')
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{pair.replace('/', '_')}_strategy_results.png")
        plt.savefig(output_file)
        print(f"Plot saved to {output_file}")
        
        plt.close(fig)


if __name__ == "__main__":
    # Test our MomentumStrategy
    pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
    data_path = 'user_data/data/binance'
    
    print("Starting strategy test...")
    tester = StrategyTester(SimpleMomentumStrategy, data_path, pairs)
    
    if tester.load_data():
        tester.test_strategy()
        
        # Plot results for each pair
        for pair in pairs:
            if pair in tester.results:
                tester.plot_results(pair)
    else:
        print("Failed to load data. Please check the data files exist at the specified path.")
    
    print("\nStrategy testing complete!") 