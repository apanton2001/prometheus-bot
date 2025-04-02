#!/usr/bin/env python3
"""
Script to download historical data from Kraken exchange for backtesting
"""
import subprocess
import argparse
import os
import sys
from datetime import datetime, timedelta


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Download historical data from Kraken")
    
    parser.add_argument("-p", "--pairs",
                        help="Cryptocurrency pairs to download (comma-separated). Example: BTC/USD,ETH/USD",
                        type=str,
                        default="BTC/USDT,ETH/USDT,SOL/USDT,ADA/USDT")
    
    parser.add_argument("-t", "--timeframes",
                        help="Timeframes to download (comma-separated). Example: 5m,15m,1h",
                        type=str,
                        default="5m")
    
    parser.add_argument("-d", "--days",
                        help="Number of days to download",
                        type=int,
                        default=90)
    
    parser.add_argument("-o", "--output-dir",
                        help="Output directory",
                        type=str,
                        default="user_data/data/kraken")
    
    return parser.parse_args()


def ensure_directory(directory):
    """Ensure the directory exists"""
    os.makedirs(directory, exist_ok=True)
    print(f"Directory ready: {directory}")


def download_data(pairs, timeframes, days, output_dir):
    """Download data using freqtrade download-data"""
    # Create directory if it doesn't exist
    ensure_directory(output_dir)
    
    # Prepare time range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    time_range = f"{start_date.strftime('%Y%m%d')}-{end_date.strftime('%Y%m%d')}"
    
    # Prepare command
    pairs_list = pairs.split(",")
    timeframes_list = timeframes.split(",")
    
    base_command = [
        "freqtrade", "download-data",
        "--exchange", "kraken",
        "--timerange", time_range,
        "--datadir", os.path.dirname(output_dir),
        "--dl-trades"
    ]
    
    # Add pairs
    pairs_args = []
    for pair in pairs_list:
        pairs_args.extend(["--pairs", pair])
    
    # Add timeframes
    timeframes_args = []
    for timeframe in timeframes_list:
        timeframes_args.extend(["--timeframes", timeframe])
    
    # Full command
    command = base_command + pairs_args + timeframes_args
    
    # Execute command
    print("Executing command:", " ".join(command))
    print("NOTE: Downloading trade data from Kraken may take a long time. Please be patient...")
    try:
        subprocess.run(command, check=True)
        print("Data download completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error downloading data: {e}")
        sys.exit(1)


def backtest_data(strategy, pairs, timeframe):
    """Run backtesting with the downloaded data"""
    pairs_list = pairs.split(",")
    pairs_args = []
    for pair in pairs_list:
        pairs_args.extend(["--pairs", pair])
    
    command = [
        "freqtrade", "backtesting",
        "--strategy", strategy,
        "--timeframe", timeframe,
        "--config", "user_data/config.json"
    ] + pairs_args
    
    print("\nRunning backtesting with command:", " ".join(command))
    try:
        subprocess.run(command, check=True)
        print("Backtesting completed successfully!")
    except subprocess.CalledProcessError as e:
        print(f"Error running backtesting: {e}")
        sys.exit(1)


def main():
    """Main function"""
    args = parse_args()
    
    print("=== Kraken Data Downloader ===")
    print(f"Pairs: {args.pairs}")
    print(f"Timeframes: {args.timeframes}")
    print(f"Days: {args.days}")
    print(f"Output Directory: {args.output_dir}")
    print("============================")
    
    # Download data
    download_data(args.pairs, args.timeframes, args.days, args.output_dir)
    
    # Ask if user wants to run backtesting
    response = input("\nDo you want to run backtesting with the downloaded data? (y/n): ")
    if response.lower() == "y":
        strategy = input("Enter the strategy name (default: EnhancedMAStrategy): ") or "EnhancedMAStrategy"
        timeframe = args.timeframes.split(",")[0]  # Use the first timeframe
        backtest_data(strategy, args.pairs, timeframe)
    
    print("\nAll operations completed successfully!")


if __name__ == "__main__":
    main() 