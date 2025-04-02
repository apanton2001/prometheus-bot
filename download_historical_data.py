#!/usr/bin/env python3
"""
Script to download historical data from cryptocurrency exchanges for backtesting
"""
import argparse
import sys
import os
from datetime import datetime, timedelta
import subprocess
import time


def parse_args():
    """
    Parses input arguments
    """
    parser = argparse.ArgumentParser(description='Download historical data for backtesting')
    
    parser.add_argument('-e', '--exchange', 
                      help='Exchange to download from',
                      type=str, required=True)
    
    parser.add_argument('-p', '--pairs', 
                      help='Pairs to download, comma separated (e.g. BTC/USDT,ETH/USDT)',
                      type=str, required=True)
    
    parser.add_argument('-t', '--timeframes',
                      help='Timeframes to download, comma separated (e.g. 5m,1h,1d)',
                      type=str, default='5m',
                      required=False)
    
    parser.add_argument('-d', '--days',
                      help='Number of days to download',
                      type=int, default=90,
                      required=False)
    
    parser.add_argument('-o', '--output-dir',
                      help='Output directory',
                      type=str, default='user_data/data',
                      required=False)
    
    return parser.parse_args()


def download_data(exchange, pairs, timeframes, days_ago, output_dir):
    """
    Downloads data from exchange using freqtrade download-data command
    """
    pairs_list = pairs.split(',')
    timeframes_list = timeframes.split(',')
    
    # Create timerange string (e.g., 20210101-20210201)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_ago)
    timerange = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
    
    # Ensure output directory exists
    os.makedirs(os.path.join(output_dir, exchange), exist_ok=True)
    
    # Construct and execute command
    cmd = [
        "freqtrade", "download-data",
        "--exchange", exchange,
        "--pairs"] + pairs_list + [
        "--timeframes"] + timeframes_list + [
        "--timerange", timerange,
        "--datadir", output_dir
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Successfully downloaded data for {exchange}.")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading data: {e}")
        sys.exit(1)


def run_backtest(exchange, pairs, timeframes, strategy, output_dir):
    """
    Runs backtest with downloaded data
    """
    pairs_list = pairs.split(',')
    timeframes_list = timeframes.split(',')[0]  # Use the first timeframe for backtest
    
    cmd = [
        "freqtrade", "backtesting",
        "--strategy", strategy,
        "--config", "user_data/backtest_config.json",
        "--timeframe", timeframes_list,
        "--timerange", "",  # Use all available data
        "--export", "signals",
        "--pairs"] + pairs_list
    
    print(f"Executing backtest: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
        print(f"Backtest completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running backtest: {e}")
        sys.exit(1)


if __name__ == "__main__":
    args = parse_args()
    
    # Download historical data
    download_data(
        args.exchange,
        args.pairs,
        args.timeframes,
        args.days,
        args.output_dir
    )
    
    print("\nData download complete. To run backtesting, use:")
    print(f"freqtrade backtesting --strategy [YourStrategy] --timeframe {args.timeframes.split(',')[0]} --config user_data/backtest_config.json")
    print("\nOr you can modify this script to automatically run backtesting after download.")
    
    # Uncomment to automatically run backtest
    # run_backtest(
    #     args.exchange,
    #     args.pairs,
    #     args.timeframes,
    #     "EnhancedMAStrategy",  # Replace with your strategy class name
    #     args.output_dir
    # ) 