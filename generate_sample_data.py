import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta

# Configuration
pairs = ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'ADA/USDT']
timeframe = '5m'
start_date = datetime(2024, 2, 1)
end_date = datetime(2024, 4, 1)
base_dir = 'user_data/data/binance'

# Ensure directory exists
os.makedirs(base_dir, exist_ok=True)

# Time delta based on timeframe
if timeframe == '5m':
    delta = timedelta(minutes=5)
elif timeframe == '1h':
    delta = timedelta(hours=1)
else:
    delta = timedelta(minutes=5)  # Default to 5m

# Generate data for each pair
for pair in pairs:
    # Clean pair name for filename
    filename = pair.replace('/', '_')
    
    # Create date range
    current_date = start_date
    dates = []
    
    while current_date < end_date:
        dates.append(current_date)
        current_date += delta
    
    # Initialize with random starting price
    if 'BTC' in pair:
        base_price = 50000
        volatility = 1000
    elif 'ETH' in pair:
        base_price = 3000
        volatility = 100
    elif 'BNB' in pair:
        base_price = 500
        volatility = 20
    elif 'SOL' in pair:
        base_price = 150
        volatility = 10
    elif 'ADA' in pair:
        base_price = 0.5
        volatility = 0.05
    else:
        base_price = 100
        volatility = 5
    
    # Generate price data with trends
    n = len(dates)
    trend = np.cumsum(np.random.normal(0, 1, n)) * volatility * 0.01
    
    # Add some cycles and patterns that the strategy could detect
    cycles = np.sin(np.arange(n) * (2 * np.pi / 30)) * volatility * 0.5
    
    # Combine trend and cycles
    price_movements = trend + cycles
    
    # Generate price data
    open_prices = base_price + price_movements
    high_prices = open_prices + np.abs(np.random.normal(0, volatility * 0.01, n))
    low_prices = open_prices - np.abs(np.random.normal(0, volatility * 0.01, n))
    close_prices = (open_prices + high_prices + low_prices + open_prices + np.random.normal(0, volatility * 0.005, n)) / 4
    
    # Ensure prices don't go negative
    if min(low_prices) < 0:
        low_prices = low_prices - min(low_prices) + 0.01
        open_prices = open_prices - min(low_prices) + 0.01
        close_prices = close_prices - min(low_prices) + 0.01
        high_prices = high_prices - min(low_prices) + 0.01
    
    # Generate volume data
    volumes = np.abs(np.random.normal(1000000, 500000, n)) * (1 + np.abs(price_movements/base_price))
    
    # Create DataFrame
    df = pd.DataFrame({
        'date': dates,
        'open': open_prices,
        'high': high_prices,
        'low': low_prices,
        'close': close_prices,
        'volume': volumes
    })
    
    # Set date as index and format
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date')
    
    # Save to CSV
    output_file = os.path.join(base_dir, f"{filename}-{timeframe}.csv")
    df.to_csv(output_file)
    print(f"Generated data for {pair} saved to {output_file}")

print("\nSample data generation complete!")
print("You can now use this data for backtesting with the command:")
print("python -m freqtrade backtesting --config user_data/backtest_config.json --strategy MomentumStrategy") 