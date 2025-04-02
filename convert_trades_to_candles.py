#!/usr/bin/env python3
"""
Script to convert downloaded trade data to candle data format for backtesting
"""
import os
import glob
import json
import pandas as pd
import argparse
from datetime import datetime, timedelta
import numpy as np


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Convert trade data to candle data")
    
    parser.add_argument("-s", "--source-dir",
                        help="Source directory containing trade data",
                        type=str,
                        default="user_data/data/kraken")
    
    parser.add_argument("-t", "--timeframe",
                        help="Timeframe for candle conversion",
                        type=str,
                        default="5m")
    
    parser.add_argument("-p", "--pair",
                        help="Trading pair to convert",
                        type=str,
                        default="BTC/USDT")
    
    return parser.parse_args()


def timeframe_to_minutes(timeframe):
    """Convert timeframe string to minutes"""
    if timeframe.endswith('m'):
        return int(timeframe[:-1])
    elif timeframe.endswith('h'):
        return int(timeframe[:-1]) * 60
    elif timeframe.endswith('d'):
        return int(timeframe[:-1]) * 1440
    else:
        raise ValueError(f"Unsupported timeframe: {timeframe}")


def find_trade_files(source_dir, pair):
    """Find trade data files for a pair"""
    pair_normalized = pair.replace('/', '_')
    files = glob.glob(f"{source_dir}/kraken-trades-{pair_normalized}-*.json")
    return files


def load_trade_data(files):
    """Load and combine trade data from multiple files"""
    trades = []
    
    for file in files:
        try:
            with open(file, 'r') as f:
                file_trades = json.load(f)
                trades.extend(file_trades)
        except Exception as e:
            print(f"Error loading {file}: {e}")
    
    if not trades:
        raise ValueError("No trade data found in files")
    
    print(f"Loaded {len(trades)} trades from {len(files)} files")
    return trades


def create_synthetic_candles(trades, pair, timeframe):
    """Create candles from trade data"""
    # Convert trades to dataframe
    df_trades = pd.DataFrame(trades)
    
    # Ensure timestamp is in the correct format
    df_trades['timestamp'] = pd.to_datetime(df_trades['timestamp'], unit='ms')
    
    # Rename columns to match expected format
    df_trades = df_trades.rename(columns={
        'timestamp': 'date',
        'price': 'price',
        'amount': 'volume'
    })
    
    # Convert timeframe to minutes
    minutes = timeframe_to_minutes(timeframe)
    
    # Group by time intervals and calculate OHLCV
    df_trades['date'] = df_trades['date'].dt.floor(f'{minutes}min')
    
    # Create candles
    candles = df_trades.groupby('date').agg({
        'price': ['first', 'max', 'min', 'last'],
        'volume': 'sum'
    })
    
    # Flatten the multi-level columns
    candles.columns = ['open', 'high', 'low', 'close', 'volume']
    
    # Reset index to make date a column
    candles = candles.reset_index()
    
    # Convert date to milliseconds for freqtrade format
    candles['date'] = candles['date'].astype(np.int64) // 10**6
    
    return candles


def save_candles(candles, output_dir, pair, timeframe):
    """Save candles to a JSON file in the format expected by freqtrade"""
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Normalize pair name for filename
    pair_normalized = pair.replace('/', '_')
    
    # Create output filename
    filename = f"{output_dir}/{pair_normalized}-{timeframe}.json"
    
    # Convert dataframe to list of records and save as JSON
    candles_json = candles.to_json(orient='records')
    
    with open(filename, 'w') as f:
        f.write(candles_json)
    
    print(f"Saved {len(candles)} candles to {filename}")


def main():
    """Main function"""
    args = parse_args()
    
    print("=== Trade to Candle Converter ===")
    print(f"Pair: {args.pair}")
    print(f"Timeframe: {args.timeframe}")
    print(f"Source Directory: {args.source_dir}")
    print("================================")
    
    # Find trade files
    files = find_trade_files(args.source_dir, args.pair)
    
    if not files:
        print(f"No trade files found for {args.pair}")
        return
    
    # Load trade data
    try:
        trades = load_trade_data(files)
    except ValueError as e:
        print(f"Error: {e}")
        return
    
    # Create candles
    candles = create_synthetic_candles(trades, args.pair, args.timeframe)
    
    # Save candles
    output_dir = os.path.join(args.source_dir, "data")
    save_candles(candles, output_dir, args.pair, args.timeframe)
    
    print("Conversion completed successfully!")


if __name__ == "__main__":
    main() 