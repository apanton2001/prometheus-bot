#!/usr/bin/env python3
"""
Prometheus Bot - An automated trading, content generation, and service delivery system
"""
import os
import sys
import argparse
import subprocess
import time
import logging
import signal
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging_level = os.getenv("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, logging_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('prometheus.log')
    ]
)

logger = logging.getLogger("PrometheusBot")

# Flag to control running state
running = True

def signal_handler(sig, frame):
    """Handle termination signals"""
    global running
    logger.info("Received termination signal. Shutting down...")
    running = False

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def start_api_server():
    """Start the API server"""
    logger.info("Starting API server...")
    
    api_process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    logger.info("API server started")
    return api_process

def start_trading_bot(config_file, strategy):
    """Start the trading bot"""
    logger.info("Starting trading bot...")
    
    trading_process = subprocess.Popen(
        ["freqtrade", "trade", "--config", config_file, "--strategy", strategy],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    logger.info("Trading bot started")
    return trading_process

def start_content_scheduler():
    """Start the content generation scheduler"""
    logger.info("Starting content generation scheduler...")
    
    # This would be implemented to periodically generate and distribute content
    # For now, we'll just simulate it with a placeholder process
    content_process = subprocess.Popen(
        [sys.executable, "-c", "import time; print('Content scheduler starting'); time.sleep(3600)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    logger.info("Content generation scheduler started")
    return content_process

def start_service_scheduler():
    """Start the service delivery scheduler"""
    logger.info("Starting service delivery scheduler...")
    
    # This would be implemented to handle service delivery workflows
    # For now, we'll just simulate it with a placeholder process
    service_process = subprocess.Popen(
        [sys.executable, "-c", "import time; print('Service scheduler starting'); time.sleep(3600)"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    logger.info("Service delivery scheduler started")
    return service_process

def initialize_database():
    """Initialize the database"""
    logger.info("Initializing database...")
    
    # Import database initialization function
    from database.connection import init_db
    
    # Initialize the database
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False
    
    return True

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Prometheus Bot - Automated trading, content, and service system")
    parser.add_argument('--trading', action='store_true', help='Start the trading bot')
    parser.add_argument('--content', action='store_true', help='Start the content generation scheduler')
    parser.add_argument('--service', action='store_true', help='Start the service delivery scheduler')
    parser.add_argument('--api', action='store_true', help='Start the API server')
    parser.add_argument('--all', action='store_true', help='Start all components')
    parser.add_argument('--config', type=str, default='trading/config/config.json', help='Trading bot config file')
    parser.add_argument('--strategy', type=str, default='MomentumStrategy', help='Trading bot strategy')
    
    args = parser.parse_args()
    
    # If no arguments provided, show help and exit
    if not (args.trading or args.content or args.service or args.api or args.all):
        parser.print_help()
        return
    
    # Initialize the database first
    if not initialize_database():
        logger.error("Failed to initialize database. Exiting.")
        return
    
    processes = []
    
    # Start components based on arguments
    if args.api or args.all:
        api_process = start_api_server()
        processes.append(api_process)
    
    if args.trading or args.all:
        trading_process = start_trading_bot(args.config, args.strategy)
        processes.append(trading_process)
    
    if args.content or args.all:
        content_process = start_content_scheduler()
        processes.append(content_process)
    
    if args.service or args.all:
        service_process = start_service_scheduler()
        processes.append(service_process)
    
    logger.info("All components started. Press Ctrl+C to exit.")
    
    # Monitor processes and keep the main thread alive
    while running:
        # Check if any process has terminated
        for process in processes:
            if process.poll() is not None:
                logger.warning(f"Process {process.args} terminated with code {process.returncode}")
                
                # Read any output or error from the process
                stdout, stderr = process.communicate()
                if stdout:
                    logger.info(f"Process output: {stdout}")
                if stderr:
                    logger.error(f"Process error: {stderr}")
        
        # Sleep to reduce CPU usage
        time.sleep(5)
    
    # Terminate all processes when shutting down
    logger.info("Shutting down all components...")
    for process in processes:
        if process.poll() is None:
            process.terminate()
    
    logger.info("Shutdown complete")

if __name__ == "__main__":
    main() 