#!/usr/bin/env python3
"""
Backtest helper script for Prometheus Trading Bot
"""
import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

def get_freqtrade_path():
    """
    Returns the path to the Freqtrade installation.
    Assumes it's installed in the parent directory of this script.
    """
    script_dir = Path(__file__).resolve().parent
    return script_dir.parent.parent / "freqtrade"

def run_backtest(strategy_name, config_file, timerange=None, timeframe=None, pairs=None):
    """
    Run a backtest with the specified parameters.
    
    Args:
        strategy_name (str): Name of the strategy class to use
        config_file (str): Path to the config file
        timerange (str, optional): Timerange to backtest. Format: YYYYMMDD-YYYYMMDD
        timeframe (str, optional): Timeframe to use (overrides strategy default)
        pairs (list, optional): List of pairs to backtest (overrides config)
    """
    freqtrade_path = get_freqtrade_path()
    
    # Build command
    cmd = [
        sys.executable,
        str(freqtrade_path / "freqtrade"),
        "backtesting",
        "--strategy", strategy_name,
        "--config", config_file,
        "--export", "trades",
    ]
    
    if timerange:
        cmd.extend(["--timerange", timerange])
    
    if timeframe:
        cmd.extend(["--timeframe", timeframe])
    
    if pairs:
        cmd.extend(["--pairs"] + pairs)
    
    # Run the command
    print(f"Running command: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
def main():
    parser = argparse.ArgumentParser(description="Run backtests for Prometheus Trading Bot")
    parser.add_argument('--strategy', type=str, required=True, help='Strategy class name')
    parser.add_argument('--config', type=str, default='../config/config.json', help='Config file path')
    parser.add_argument('--timerange', type=str, help='Timerange for backtesting (format: YYYYMMDD-YYYYMMDD)')
    parser.add_argument('--timeframe', type=str, help='Override timeframe')
    parser.add_argument('--pairs', nargs='+', help='Pairs to backtest')
    
    args = parser.parse_args()
    
    run_backtest(
        args.strategy,
        args.config,
        args.timerange,
        args.timeframe,
        args.pairs
    )

if __name__ == "__main__":
    main() 