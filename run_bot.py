#!/usr/bin/env python3
"""
Script to run the trading bot in dry-run mode with monitoring capabilities
"""
import argparse
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timedelta
import json


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Run the trading bot in dry-run mode")
    
    parser.add_argument("-c", "--config",
                        help="Path to the configuration file",
                        type=str,
                        default="user_data/config.json")
    
    parser.add_argument("-s", "--strategy",
                        help="Strategy to use",
                        type=str,
                        default="EnhancedMAStrategy")
    
    parser.add_argument("-l", "--log-level",
                        help="Log level (debug, info, warning, error)",
                        type=str,
                        choices=["debug", "info", "warning", "error"],
                        default="info")
    
    parser.add_argument("--live",
                        help="Run in live mode (real trading)",
                        action="store_true")
    
    parser.add_argument("--no-monitor",
                        help="Do not display real-time monitoring",
                        action="store_true")
    
    return parser.parse_args()


def check_config(config_path, is_live):
    """Check configuration file and update if necessary"""
    try:
        with open(config_path, "r") as f:
            config = json.load(f)
        
        # Check if we're running in live mode
        if is_live and config.get("dry_run", True):
            print("WARNING: Running in live mode but configuration has dry_run=true")
            response = input("Do you want to update the configuration to dry_run=false? (y/n): ")
            if response.lower() == "y":
                config["dry_run"] = False
                with open(config_path, "w") as f:
                    json.dump(config, f, indent=4)
                print("Configuration updated to live mode (dry_run=false)")
        
        # Check if API keys are set for live mode
        if not config.get("dry_run", True):
            if not config.get("exchange", {}).get("key") or not config.get("exchange", {}).get("secret"):
                print("ERROR: Running in live mode but API keys are not set in the configuration")
                sys.exit(1)
        
        return config
    
    except Exception as e:
        print(f"Error checking configuration: {e}")
        sys.exit(1)


def run_bot(config_path, strategy, log_level):
    """Run the bot with the given configuration"""
    command = [
        "freqtrade", "trade",
        "--config", config_path,
        "--strategy", strategy,
        "--logfile", "user_data/logs/bot_run.log",
        "--db-url", "sqlite:///user_data/tradesv3.sqlite"
    ]
    
    if log_level:
        command.extend(["--loglevel", log_level])
    
    print("Starting bot with command:", " ".join(command))
    
    try:
        process = subprocess.Popen(command)
        return process
    except Exception as e:
        print(f"Error starting bot: {e}")
        sys.exit(1)


def show_profits():
    """Show current profit statistics"""
    try:
        # Get trade data from API
        base_url = "http://127.0.0.1:8080"
        
        # TODO: Implement API calls to get profit statistics
        # This would require authentication and API calls to the freqtrade API
        
        # For now, display static message
        print("-" * 50)
        print("PROFIT STATISTICS")
        print("-" * 50)
        print("API connection not implemented yet. Check web UI at http://127.0.0.1:8080")
        print("-" * 50)
    except Exception as e:
        print(f"Error showing profits: {e}")


def monitor_bot():
    """Monitor the bot's operation"""
    try:
        while True:
            # Clear screen
            os.system("cls" if os.name == "nt" else "clear")
            
            # Show title
            print("=" * 50)
            print("PROMETHEUS TRADING BOT MONITOR")
            print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("=" * 50)
            
            # Show profits
            show_profits()
            
            # Sleep for a while
            print("\nPress Ctrl+C to stop the bot...")
            time.sleep(60)
    except KeyboardInterrupt:
        print("\nMonitoring stopped by user")


def main():
    """Main function"""
    args = parse_args()
    
    print("=== Prometheus Trading Bot Runner ===")
    print(f"Configuration: {args.config}")
    print(f"Strategy: {args.strategy}")
    print(f"Log Level: {args.log_level}")
    print(f"Mode: {'LIVE TRADING' if args.live else 'Dry-run (Paper Trading)'}")
    print("====================================")
    
    # Check configuration
    config = check_config(args.config, args.live)
    
    # Confirm if running in live mode
    if args.live:
        print("\n!!! WARNING: RUNNING IN LIVE MODE WITH REAL MONEY !!!")
        print("Are you sure you want to continue?")
        confirmation = input("Type 'yes' to confirm: ")
        if confirmation.lower() != "yes":
            print("Aborted by user")
            sys.exit(0)
    
    # Run the bot
    bot_process = run_bot(args.config, args.strategy, args.log_level)
    
    try:
        # Give the bot a moment to start
        time.sleep(5)
        
        # Monitor the bot if requested
        if not args.no_monitor:
            monitor_bot()
        else:
            print("\nBot is running in the background...")
            print("Press Ctrl+C to stop the bot...")
            # Wait for the bot to finish
            bot_process.wait()
    
    except KeyboardInterrupt:
        print("\nStopping bot...")
        bot_process.send_signal(signal.SIGINT)
        try:
            # Wait for the bot to finish gracefully
            bot_process.wait(timeout=30)
        except subprocess.TimeoutExpired:
            print("Bot didn't stop gracefully, forcing termination...")
            bot_process.terminate()
    
    print("Bot stopped")


if __name__ == "__main__":
    main() 