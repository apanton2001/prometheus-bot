#!/usr/bin/env python3
"""
Script to generate synthetic data for backtesting trading strategies
"""
import os
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import subprocess


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Generate synthetic data for backtesting")
    
    parser.add_argument("-p", "--pairs",
                        help="Cryptocurrency pairs to generate (comma-separated). Example: BTC/USD,ETH/USD",
                        type=str,
                        default="BTC/USDT,ETH/USDT")
    
    parser.add_argument("-t", "--timeframe",
                        help="Timeframe to generate data for. Example: 5m, 15m, 1h",
                        type=str,
                        default="5m")
    
    parser.add_argument("-d", "--days",
                        help="Number of days of data to generate",
                        type=int,
                        default=90)
    
    parser.add_argument("-o", "--output-dir",
                        help="Output directory",
                        type=str,
                        default="user_data/data/synthetic")
    
    parser.add_argument("-m", "--mode",
                        help="Data generation mode: synthetic or download",
                        type=str,
                        choices=["synthetic", "download"],
                        default="synthetic")
    
    return parser.parse_args()


def ensure_directory(directory):
    """Ensure the directory exists"""
    os.makedirs(directory, exist_ok=True)
    print(f"Directory ready: {directory}")


def generate_synthetic_data(pair, timeframe, days, output_dir):
    """Generate synthetic price data for backtesting"""
    pair_filename = pair.replace("/", "_")
    
    # Determine number of candles based on timeframe
    timeframe_minutes = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "4h": 240,
        "1d": 1440
    }
    
    minutes = timeframe_minutes.get(timeframe, 5)
    candles_per_day = 24 * 60 // minutes
    total_candles = days * candles_per_day
    
    # Generate timestamps
    end_time = datetime.now()
    timestamps = [(end_time - timedelta(minutes=i * minutes)) for i in range(total_candles)]
    timestamps.reverse()
    
    # Set initial price and parameters for random walk
    start_price = 10000.0 if "BTC" in pair else 1000.0
    volatility = 0.02 if "BTC" in pair else 0.025
    trend = 0.0005  # Small upward trend
    
    # Generate price data using geometric Brownian motion
    prices = [start_price]
    for i in range(1, total_candles):
        daily_volatility = volatility / np.sqrt(candles_per_day)
        daily_return = np.random.normal(trend, daily_volatility)
        price = prices[-1] * np.exp(daily_return)
        prices.append(price)
    
    # Generate OHLCV data
    data = []
    for i in range(total_candles):
        timestamp = int(timestamps[i].timestamp() * 1000)
        close_price = prices[i]
        
        # Generate high, low, open based on close
        candle_volatility = close_price * volatility * 0.1
        high_price = close_price + abs(np.random.normal(0, candle_volatility))
        low_price = close_price - abs(np.random.normal(0, candle_volatility))
        
        # Ensure low <= close <= high
        if low_price > close_price:
            low_price = close_price * 0.998
        if high_price < close_price:
            high_price = close_price * 1.002
            
        # Randomly determine if it's an up or down candle
        if np.random.random() > 0.5:
            open_price = low_price + (close_price - low_price) * np.random.random()
        else:
            open_price = close_price + (high_price - close_price) * np.random.random()
        
        # Generate volume
        volume = np.random.gamma(2.0, close_price / 1000)
        
        data.append([
            timestamp,              # Timestamp
            open_price,             # Open
            high_price,             # High
            low_price,              # Low
            close_price,            # Close
            volume                  # Volume
        ])
    
    # Create DataFrame
    df = pd.DataFrame(data, columns=["date", "open", "high", "low", "close", "volume"])
    
    # Save to CSV
    output_file = f"{output_dir}/{pair_filename}-{timeframe}.json"
    df.to_json(output_file, orient="records")
    print(f"Synthetic data generated for {pair} ({timeframe}) saved to {output_file}")
    
    return df


def download_binance_data(pairs, timeframe, days, output_dir):
    """Download data from Binance"""
    try:
        # Prepare time range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        time_range = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
        
        # Prepare command
        pairs_list = pairs.split(",")
        pairs_args = []
        for pair in pairs_list:
            pairs_args.extend(["--pairs", pair])
        
        command = [
            "freqtrade", "download-data",
            "--exchange", "binance",
            "--timerange", time_range,
            "--timeframes", timeframe,
            "--datadir", "user_data/data"
        ] + pairs_args
        
        # Execute command
        print("Executing command:", " ".join(command))
        subprocess.run(command, check=True)
        print("Binance data download completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading Binance data: {e}")
        return False
    
    return True


def main():
    """Main function"""
    args = parse_args()
    
    print("=== Test Data Generator ===")
    print(f"Pairs: {args.pairs}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Days: {args.days}")
    print(f"Mode: {args.mode}")
    print(f"Output Directory: {args.output_dir}")
    print("==========================")
    
    # Ensure output directory exists
    ensure_directory(args.output_dir)
    
    if args.mode == "synthetic":
        # Generate synthetic data for each pair
        pairs = args.pairs.split(",")
        for pair in pairs:
            generate_synthetic_data(pair, args.timeframe, args.days, args.output_dir)
    else:
        # Download data from Binance
        download_binance_data(args.pairs, args.timeframe, args.days, args.output_dir)
    
    print("\nAll operations completed successfully!")
    print("You can now run backtesting with the generated/downloaded data.")


if __name__ == "__main__":
    main() 