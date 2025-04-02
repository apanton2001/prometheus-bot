# S&P 500 Advanced Trading Bot

A sophisticated trading system for the S&P 500 market with multi-timeframe analysis, sector rotation intelligence, and adaptive market regime detection.

## Features

- **Multi-Timeframe Analysis**: Combines signals from 15m, 1h, 4h, and daily timeframes
- **Sector Rotation Intelligence**: Identifies strong and weak sectors to improve trade selectivity
- **Market Regime Detection**: Adapts trading parameters based on bullish, bearish, or ranging conditions
- **Proprietary Risk Scoring**: Evaluates trade opportunities based on 15+ risk metrics
- **Risk-Based Position Sizing**: Dynamically adjusts position size based on volatility and risk metrics
- **Advanced Visualization**: Comprehensive dashboard for performance monitoring
- **Institutional-Grade Risk Management**: Sophisticated stops and exposure controls

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/sp500-trading-bot.git
cd sp500-trading-bot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Getting Started

### Basic Usage

1. Run a backtest of the strategy on default settings:
```bash
python run_strategy.py --mode backtest
```

2. Run with specific symbols:
```bash
python run_strategy.py --mode backtest --symbols SPY AAPL MSFT GOOGL META
```

3. Customize the backtest parameters:
```bash
python run_strategy.py --mode backtest --backtest-days 90 --initial-capital 50000 --max-positions 3 --risk-per-trade 0.02 --save-results backtest_results.json --save-plot backtest_plot.png
```

4. Run in live trading mode:
```bash
python run_strategy.py --mode live --update-interval 1800
```

### Configuration Options

| Parameter | Description | Default |
|-----------|-------------|---------|
| --mode | Running mode ('backtest' or 'live') | backtest |
| --symbols | List of symbols to trade | Top 50 S&P 500 components |
| --timeframes | List of timeframes to analyze | ['15m', '1h', '4h', '1d'] |
| --data-dir | Directory to store data | ../data |
| --backtest-days | Number of days to backtest | 180 |
| --initial-capital | Initial capital for backtesting | 100000.0 |
| --max-positions | Maximum number of concurrent positions | 5 |
| --risk-per-trade | Maximum risk per trade (as decimal) | 0.01 |
| --update-interval | Data update interval in seconds (live mode) | 3600 |
| --save-results | Path to save backtest results | None |
| --save-plot | Path to save backtest plot | None |

## Strategy Details

The SP500Strategy combines several advanced concepts in algorithmic trading:

### 1. Multi-Timeframe Analysis
The strategy analyzes price data across multiple timeframes to confirm trends and identify high-probability entry points. By requiring alignment across timeframes, the system filters out lower-quality signals and reduces false entries.

### 2. Market Regime Detection
The system identifies the current market regime (bullish, bearish, or ranging) by analyzing:
- Trend direction and strength (using ADX and moving average relationships)
- Volatility patterns (using ATR)
- Price relative to long-term moving averages

Each regime uses optimized parameters for entries, exits, and risk management.

### 3. Sector Rotation Analysis
The strategy analyzes the relative strength of different market sectors to:
- Identify leading and lagging sectors
- Adjust exposure to different sectors
- Prioritize trades in stronger sectors during bullish regimes
- Focus on weaker sectors during bearish regimes

### 4. Risk Management
The strategy implements sophisticated risk management rules:
- Position sizing based on volatility (ATR)
- Maximum sector exposure limits
- Risk score calculation for each trade opportunity
- Adaptive stop losses based on market conditions
- Portfolio-level diversification controls

## Project Structure

- `sp500_strategy.py`: Core strategy implementation with trading logic
- `stock_data_handler.py`: Data acquisition and preprocessing
- `run_strategy.py`: Main script for running backtest or live trading
- `requirements.txt`: Package dependencies
- `data/`: Directory for storing market data

## Performance Visualization

The backtest results include comprehensive visualizations:
- Portfolio equity curve
- Drawdown chart
- Entry/exit points
- Performance metrics (Sharpe, win rate, max drawdown, etc.)

## Disclaimer

This trading bot is for educational and research purposes only. Trading financial markets involves substantial risk of loss. Past performance of any trading system is not necessarily indicative of future results.

## License

MIT 