#!/usr/bin/env python3
"""
Risk calculator for trading position sizing.
"""
import argparse
import sys
import pandas as pd
import numpy as np
import logging
from typing import Dict, Optional, Union, List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Calculate risk parameters for trading')
    
    parser.add_argument('--portfolio-size', type=float, required=True,
                        help='Total portfolio size in USD')
    
    parser.add_argument('--risk-per-trade', type=float, required=True,
                        help='Percentage of portfolio to risk per trade (1 = 1%)')
    
    parser.add_argument('--stop-loss', type=float, required=True,
                        help='Stop loss percentage (2 = 2%)')
    
    parser.add_argument('--max-open-trades', type=int, required=True,
                        help='Maximum number of open trades')
    
    parser.add_argument('--volatility-file', type=str, default=None,
                        help='CSV file with volatility data for adaptive sizing')
    
    return parser.parse_args()

def calculate_position_size(
    portfolio_size: float,
    risk_percentage: float,
    stop_loss_percentage: float,
    max_open_trades: int,
    volatility_factor: float = 1.0
) -> Dict[str, float]:
    """
    Calculate the position size based on risk parameters.
    
    Args:
        portfolio_size: Total portfolio size in USD
        risk_percentage: Percentage of portfolio to risk per trade (1 = 1%)
        stop_loss_percentage: Stop loss percentage (2 = 2%)
        max_open_trades: Maximum number of open trades
        volatility_factor: Multiplier based on market volatility
        
    Returns:
        Dictionary with calculated risk parameters
    """
    # Calculate dollar risk per trade
    dollar_risk = portfolio_size * (risk_percentage / 100)
    
    # Calculate ideal position size
    ideal_position_size = dollar_risk / (stop_loss_percentage / 100)
    
    # Apply volatility adjustment
    adjusted_position_size = ideal_position_size * volatility_factor
    
    # Consider max open trades constraint
    max_position_size = portfolio_size / max_open_trades
    position_size = min(adjusted_position_size, max_position_size)
    
    # Calculate actual risk with the adjusted position size
    actual_dollar_risk = position_size * (stop_loss_percentage / 100)
    actual_percentage_risk = (actual_dollar_risk / portfolio_size) * 100
    
    # Calculate maximum portfolio risk if all positions hit stop loss
    max_portfolio_risk = actual_percentage_risk * max_open_trades
    
    return {
        "portfolio_size": portfolio_size,
        "position_size": position_size,
        "dollar_risk_per_trade": actual_dollar_risk,
        "percentage_risk_per_trade": actual_percentage_risk,
        "max_portfolio_risk": max_portfolio_risk,
        "volatility_factor": volatility_factor,
        "stop_loss_percentage": stop_loss_percentage,
        "max_open_trades": max_open_trades
    }

def calculate_volatility_factor(volatility_file: str) -> float:
    """
    Calculate volatility factor from historical data.
    
    Args:
        volatility_file: Path to CSV file with volatility data
        
    Returns:
        Volatility factor (lower for high volatility, higher for low volatility)
    """
    try:
        # Load volatility data
        df = pd.read_csv(volatility_file)
        
        # Calculate average ATR percentage
        if 'atr_pct' in df.columns:
            avg_atr_pct = df['atr_pct'].mean()
        elif 'volatility' in df.columns:
            avg_atr_pct = df['volatility'].mean()
        else:
            # If we have just OHLC data, calculate ATR percentage
            if all(col in df.columns for col in ['high', 'low', 'close']):
                # Calculate simple ATR
                df['tr1'] = df['high'] - df['low']
                df['tr2'] = abs(df['high'] - df['close'].shift(1))
                df['tr3'] = abs(df['low'] - df['close'].shift(1))
                df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)
                df['atr'] = df['tr'].rolling(window=14).mean()
                df['atr_pct'] = df['atr'] / df['close'] * 100
                avg_atr_pct = df['atr_pct'].dropna().mean()
            else:
                logger.error(f"Volatility file {volatility_file} does not contain required columns")
                return 1.0
        
        logger.info(f"Average ATR percentage: {avg_atr_pct:.2f}%")
        
        # Transform ATR percentage to volatility factor (inverse relationship)
        # Higher ATR = lower position size
        if avg_atr_pct <= 0.5:  # Very low volatility
            return 1.2
        elif avg_atr_pct <= 1.0:  # Low volatility
            return 1.0
        elif avg_atr_pct <= 2.0:  # Medium volatility
            return 0.8
        elif avg_atr_pct <= 3.0:  # High volatility
            return 0.6
        else:  # Very high volatility
            return 0.4
            
    except Exception as e:
        logger.error(f"Error processing volatility file: {str(e)}")
        return 1.0

def main():
    """Main function."""
    args = parse_args()
    
    # Validate inputs
    if args.portfolio_size <= 0:
        logger.error("Portfolio size must be positive")
        return 1
        
    if args.risk_per_trade <= 0 or args.risk_per_trade > 5:
        logger.error("Risk per trade should be between 0 and 5%")
        return 1
        
    if args.stop_loss <= 0 or args.stop_loss > 20:
        logger.error("Stop loss should be between 0 and 20%")
        return 1
        
    if args.max_open_trades <= 0:
        logger.error("Maximum open trades must be positive")
        return 1
    
    # Calculate volatility factor if file provided
    volatility_factor = 1.0
    if args.volatility_file:
        volatility_factor = calculate_volatility_factor(args.volatility_file)
    
    # Calculate risk parameters
    params = calculate_position_size(
        portfolio_size=args.portfolio_size,
        risk_percentage=args.risk_per_trade,
        stop_loss_percentage=args.stop_loss,
        max_open_trades=args.max_open_trades,
        volatility_factor=volatility_factor
    )
    
    # Print results
    logger.info("Risk Management Parameters:")
    logger.info(f"Portfolio Size: ${params['portfolio_size']:.2f}")
    logger.info(f"Position Size: ${params['position_size']:.2f}")
    logger.info(f"Risk per Trade: ${params['dollar_risk_per_trade']:.2f} ({params['percentage_risk_per_trade']:.2f}%)")
    logger.info(f"Maximum Portfolio Risk: {params['max_portfolio_risk']:.2f}%")
    logger.info(f"Volatility Factor: {params['volatility_factor']:.2f}")
    logger.info(f"Stop Loss: {params['stop_loss_percentage']:.2f}%")
    logger.info(f"Max Open Trades: {params['max_open_trades']}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main()) 