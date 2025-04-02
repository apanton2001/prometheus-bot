#!/usr/bin/env python3
"""
Risk calculator for optimizing position sizes and risk levels in cryptocurrency trading.
"""
import argparse
import json
import os
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Risk management calculator for cryptocurrency trading")
    
    parser.add_argument("-p", "--portfolio-size",
                        help="Total portfolio size in base currency (e.g., USD, USDT)",
                        type=float,
                        required=True)
    
    parser.add_argument("-r", "--risk-per-trade",
                        help="Risk percentage per trade (e.g., 1 for 1%%)",
                        type=float,
                        default=1.0)
    
    parser.add_argument("-s", "--stop-loss",
                        help="Stop loss percentage (e.g., 2 for 2%%)",
                        type=float,
                        default=2.0)
    
    parser.add_argument("-m", "--max-open-trades",
                        help="Maximum number of open trades",
                        type=int,
                        default=5)
    
    parser.add_argument("-v", "--volatility-file",
                        help="CSV file with volatility data",
                        type=str)
    
    parser.add_argument("-o", "--output",
                        help="Output file for risk configuration",
                        type=str)
    
    return parser.parse_args()


def calculate_position_sizes(portfolio_size, risk_per_trade, stop_loss, max_open_trades):
    """Calculate position sizes based on risk parameters"""
    # Convert percentages to decimals
    risk_per_trade = risk_per_trade / 100
    stop_loss = stop_loss / 100
    
    # Calculate dollar risk per trade
    dollar_risk_per_trade = portfolio_size * risk_per_trade
    
    # Calculate position size per trade (fixed stop loss)
    position_size = dollar_risk_per_trade / stop_loss
    
    # Maximum total position considering max open trades
    max_total_position = position_size * max_open_trades
    
    # Cap total exposure at portfolio size
    if max_total_position > portfolio_size:
        position_size = portfolio_size / max_open_trades
        dollar_risk_per_trade = position_size * stop_loss
        risk_per_trade = dollar_risk_per_trade / portfolio_size * 100
    
    return {
        "portfolio_size": portfolio_size,
        "risk_per_trade_pct": risk_per_trade * 100,
        "stop_loss_pct": stop_loss * 100,
        "dollar_risk_per_trade": dollar_risk_per_trade,
        "position_size": position_size,
        "max_open_trades": max_open_trades,
        "max_total_position": position_size * max_open_trades,
        "portfolio_utilization_pct": (position_size * max_open_trades) / portfolio_size * 100
    }


def calculate_adaptive_position_sizes(portfolio_size, risk_per_trade, volatility_data, max_open_trades):
    """Calculate position sizes based on volatility"""
    # Convert percentages to decimals
    risk_per_trade = risk_per_trade / 100
    
    # Calculate dollar risk per trade
    dollar_risk_per_trade = portfolio_size * risk_per_trade
    
    # Read volatility data
    df = pd.read_csv(volatility_data)
    
    # Calculate position sizes based on volatility
    results = []
    for _, row in df.iterrows():
        symbol = row["symbol"]
        volatility = row["volatility"] / 100  # Convert to decimal
        
        # Use volatility as stop loss percentage
        position_size = dollar_risk_per_trade / volatility
        
        # Adjust position size for max open trades
        adjusted_position_size = min(position_size, portfolio_size / max_open_trades)
        
        results.append({
            "symbol": symbol,
            "volatility_pct": volatility * 100,
            "position_size": adjusted_position_size,
            "dollar_risk": adjusted_position_size * volatility,
            "risk_pct": (adjusted_position_size * volatility) / portfolio_size * 100
        })
    
    return results


def visualize_risk(risk_data):
    """Create visualizations for risk parameters"""
    # Create a new figure
    plt.figure(figsize=(12, 8))
    
    # Bar chart of position sizes
    plt.subplot(2, 2, 1)
    plt.bar(["Position Size", "Portfolio Size"], [risk_data["position_size"], risk_data["portfolio_size"]])
    plt.title("Position Size vs Portfolio Size")
    plt.ylabel("Amount")
    
    # Pie chart of portfolio utilization
    plt.subplot(2, 2, 2)
    utilization = risk_data["portfolio_utilization_pct"]
    plt.pie([utilization, 100 - utilization], 
            labels=["Utilized", "Unused"], 
            autopct="%1.1f%%",
            colors=["#5cb85c", "#f0f0f0"])
    plt.title("Portfolio Utilization")
    
    # Bar chart of risk parameters
    plt.subplot(2, 2, 3)
    plt.bar(["Risk Per Trade", "Stop Loss"], [risk_data["risk_per_trade_pct"], risk_data["stop_loss_pct"]])
    plt.title("Risk Parameters")
    plt.ylabel("Percentage")
    
    # Text summary
    plt.subplot(2, 2, 4)
    plt.axis("off")
    summary = (
        f"Risk Summary\n\n"
        f"Portfolio Size: ${risk_data['portfolio_size']:.2f}\n"
        f"Risk Per Trade: {risk_data['risk_per_trade_pct']:.2f}%\n"
        f"Stop Loss: {risk_data['stop_loss_pct']:.2f}%\n"
        f"Position Size: ${risk_data['position_size']:.2f}\n"
        f"Dollar Risk: ${risk_data['dollar_risk_per_trade']:.2f}\n"
        f"Max Open Trades: {risk_data['max_open_trades']}\n"
        f"Utilization: {risk_data['portfolio_utilization_pct']:.2f}%"
    )
    plt.text(0.1, 0.5, summary, fontsize=12)
    
    plt.tight_layout()
    plt.savefig("risk_analysis.png")
    plt.close()
    
    print(f"Risk visualization saved to risk_analysis.png")


def generate_config(risk_data, output_file):
    """Generate configuration file with risk parameters"""
    config = {
        "max_open_trades": risk_data["max_open_trades"],
        "stake_currency": "USDT",
        "stake_amount": risk_data["position_size"],
        "tradable_balance_ratio": 0.99,
        "stoploss": -risk_data["stop_loss_pct"] / 100,
        "trailing_stop": True,
        "trailing_stop_positive": 0.005,
        "trailing_stop_positive_offset": 0.02,
        "trailing_only_offset_is_reached": True
    }
    
    with open(output_file, "w") as f:
        json.dump(config, f, indent=4)
    
    print(f"Risk configuration saved to {output_file}")


def format_risk_table(risk_data):
    """Format risk data as table"""
    table = []
    table.append("=" * 50)
    table.append(f"{'RISK ANALYSIS':^50}")
    table.append("=" * 50)
    table.append(f"Portfolio Size:         ${risk_data['portfolio_size']:.2f}")
    table.append(f"Risk Per Trade:         {risk_data['risk_per_trade_pct']:.2f}%")
    table.append(f"Stop Loss:              {risk_data['stop_loss_pct']:.2f}%")
    table.append(f"Dollar Risk Per Trade:  ${risk_data['dollar_risk_per_trade']:.2f}")
    table.append(f"Position Size:          ${risk_data['position_size']:.2f}")
    table.append(f"Max Open Trades:        {risk_data['max_open_trades']}")
    table.append(f"Max Total Position:     ${risk_data['max_total_position']:.2f}")
    table.append(f"Portfolio Utilization:  {risk_data['portfolio_utilization_pct']:.2f}%")
    table.append("-" * 50)
    table.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    table.append("=" * 50)
    
    return "\n".join(table)


def format_adaptive_risk_table(adaptive_results, portfolio_size):
    """Format adaptive risk data as table"""
    table = []
    table.append("=" * 70)
    table.append(f"{'ADAPTIVE POSITION SIZING BASED ON VOLATILITY':^70}")
    table.append("=" * 70)
    table.append(f"Portfolio Size: ${portfolio_size:.2f}")
    table.append("-" * 70)
    table.append(f"{'Symbol':<10}{'Volatility':<15}{'Position Size':<20}{'Dollar Risk':<15}{'Risk %':<10}")
    table.append("-" * 70)
    
    for result in adaptive_results:
        table.append(f"{result['symbol']:<10}{result['volatility_pct']:.2f}%{result['position_size']:.2f}{result['dollar_risk']:.2f}{result['risk_pct']:.2f}%")
    
    table.append("-" * 70)
    table.append(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    table.append("=" * 70)
    
    return "\n".join(table)


def main():
    """Main function"""
    args = parse_args()
    
    # Calculate fixed position sizes
    risk_data = calculate_position_sizes(
        args.portfolio_size,
        args.risk_per_trade,
        args.stop_loss,
        args.max_open_trades
    )
    
    # Print fixed risk analysis
    print(format_risk_table(risk_data))
    
    # Generate visualization
    visualize_risk(risk_data)
    
    # Generate configuration file if requested
    if args.output:
        generate_config(risk_data, args.output)
    
    # Calculate adaptive position sizes if volatility data provided
    if args.volatility_file:
        try:
            adaptive_results = calculate_adaptive_position_sizes(
                args.portfolio_size,
                args.risk_per_trade,
                args.volatility_file,
                args.max_open_trades
            )
            
            print("\n\n" + format_adaptive_risk_table(adaptive_results, args.portfolio_size))
        except Exception as e:
            print(f"Error calculating adaptive position sizes: {e}")


if __name__ == "__main__":
    main() 