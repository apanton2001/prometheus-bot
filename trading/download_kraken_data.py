#!/usr/bin/env python3
"""
Script to download historical data from Kraken exchange.
"""
import argparse
import os
import sys
from datetime import datetime, timedelta
import ccxt
import pandas as pd
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Download historical data from Kraken')
    
    parser.add_argument('--pairs', type=str, required=True,
                        help='Comma-separated list of trading pairs (e.g., BTC/USDT,ETH/USDT)')
    
    parser.add_argument('--timeframes', type=str, required=True,
                        help='Comma-separated list of timeframes (e.g., 5m,1h,4h,1d)')
    
    parser.add_argument('--days', type=int, default=90,
                        help='Number of days of historical data to download')
    
    parser.add_argument('--output-dir', type=str, default='./data',
                        help='Directory to save the downloaded data')
    
    return parser.parse_args()

def download_data(exchange, pair, timeframe, days, output_dir):
    """Download historical data for a specific pair and timeframe."""
    logger.info(f"Downloading {pair} data for {timeframe} timeframe ({days} days)")
    
    # Calculate start time
    now = datetime.now()
    start_time = int((now - timedelta(days=days)).timestamp() * 1000)
    
    # Fetch OHLCV data
    try:
        ohlcv = exchange.fetch_ohlcv(pair, timeframe, since=start_time)
        
        # Convert to DataFrame
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        
        # Convert timestamp to datetime
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save to CSV
        filename = f"{output_dir}/{pair.replace('/', '_')}_{timeframe}.csv"
        df.to_csv(filename, index=False)
        logger.info(f"Saved {len(df)} candles to {filename}")
        
        return True
    except Exception as e:
        logger.error(f"Error downloading {pair} {timeframe} data: {str(e)}")
        return False

def main():
    """Main function."""
    args = parse_args()
    
    # Create exchange instance
    exchange = ccxt.kraken({
        'enableRateLimit': True,  # Be nice to the exchange API
    })
    
    # Parse pairs and timeframes
    pairs = [pair.strip() for pair in args.pairs.split(',')]
    timeframes = [tf.strip() for tf in args.timeframes.split(',')]
    
    # Validate timeframes
    supported_timeframes = list(exchange.timeframes.keys())
    for tf in timeframes:
        if tf not in supported_timeframes:
            logger.error(f"Timeframe {tf} not supported by Kraken. Supported timeframes: {supported_timeframes}")
            sys.exit(1)
    
    # Download data for each pair and timeframe
    success_count = 0
    total_downloads = len(pairs) * len(timeframes)
    
    for pair in pairs:
        for timeframe in timeframes:
            if download_data(exchange, pair, timeframe, args.days, args.output_dir):
                success_count += 1
    
    # Report results
    logger.info(f"Downloaded {success_count}/{total_downloads} datasets")
    
    if success_count < total_downloads:
        logger.warning("Some downloads failed. Check logs for details.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 