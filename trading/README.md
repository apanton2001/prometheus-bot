# Trading Bot

This directory contains the trading bot implementation based on Freqtrade with custom strategies.

## Features

- Enhanced Moving Average Crossover strategy with trend filters
- ADX-based trend strength confirmation
- Volume analysis and volatility-based position sizing
- Advanced risk management with trailing stop-loss
- Kraken/KuCoin exchange integration
- Real-time monitoring and control interface

## Setup

1. Install Freqtrade and dependencies
   ```
   ./setup.sh
   ```

2. Download historical data
   ```
   python download_kraken_data.py --pairs BTC/USDT,ETH/USDT --timeframes 5m,1h --days 90
   ```

3. Configure the bot
   ```
   cp user_data/config.example.json user_data/config.json
   # Edit config.json with your exchange API keys
   ```

## Usage

### Backtesting
```
freqtrade backtesting --strategy EnhancedMAStrategy --config user_data/config.json
```

### Paper Trading
```
python run_bot.py --config user_data/config.json --strategy EnhancedMAStrategy
```

### Live Trading
```
freqtrade trade --strategy EnhancedMAStrategy --config user_data/config.json
```

## Strategies

- `EnhancedMAStrategy`: Enhanced Moving Average Crossover strategy (v5.0)
- `EnhancedMAStrategyMTF`: Multi-timeframe version with trend confirmation 