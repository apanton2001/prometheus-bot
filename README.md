# Prometheus Trading Bot (MVP Stage)

## Project Goal

To develop and operate a personal, automated algorithmic trading bot initially focused on US stocks (AAPL, TSLA) using the Alpaca brokerage API (Paper Trading environment). The ultimate goal is to incorporate machine learning models to identify potentially profitable trading opportunities based on various market indicators, starting with basic execution logic.

*(Self-Correction Note: While the long-term goal involves sophisticated ML, the immediate, validated state is much simpler).*

## Current Status (MVP v0.1 - Local Execution Verified)

*   **Phase:** Phase 1 Complete - Local Execution Verified.
*   **Functionality:** The current active script (`simple_alpaca_bot.py`) successfully:
    *   Connects to the Alpaca Paper Trading API using environment variables.
    *   Fetches the latest trade price for a hardcoded stock (AAPL).
    *   Applies basic threshold logic (Buy > X, Sell < Y) to make a decision (BUY/SELL/HOLD).
    *   Submits a market order for 1 share to the Alpaca paper trading account if a BUY/SELL decision is made.
    *   Runs in a loop with a configurable sleep timer.
    *   Logs basic actions to the console.
*   **Focus:** This existing MVP purely validates the end-to-end mechanics: API connection -> Data Fetch -> Basic Logic -> Paper Order Execution -> Logging. **It does NOT implement any sophisticated strategy or validated ML yet.** Previous attempts to validate ML hypotheses (e.g., tariff analysis) were **blocked by data availability issues.**

## Implementation Timeline & Phases (Planned - Not Yet Implemented)

*Note: This outlines the intended roadmap. Development beyond Phase 1 MVP is pending resolution of data access issues and validation of core trading hypotheses.*

### PHASE 1: MVP Trading Bot (Weeks 1-2) - LARGELY COMPLETE (Local)
- ✓ Basic API Connection & Price Fetching (`simple_alpaca_bot.py`)
- ✓ Simple Trading Logic (Threshold-based in `simple_alpaca_bot.py`)
- ✓ Paper Trading Order Submission (`simple_alpaca_bot.py`)
- ✓ Basic Execution Loop (`simple_alpaca_bot.py`)
- **Next Deliverables (Requires modifying `simple_alpaca_bot.py` or creating new structure):**
  ```python
  # Historical data integration (Placeholder)
  def fetch_historical_data(symbol, start, end):
      # TODO: Implement robust Alpaca historical data fetch (daily/hourly)
      # Needs to handle potential data source limitations (IEX vs SIP)
      pass

  # Performance logging (Placeholder)
  def log_performance(trade_details):
      # TODO: Basic trade tracking to console or simple file/DB
      pass
  ```

### PHASE 2: Backtesting Framework (Weeks 3-4) - FUTURE
```python
# Key Components (Placeholder):
class BacktestEngine:
    def __init__(self, strategy, data):
        self.historical_data = data
        self.strategy = strategy # Requires defining a strategy class

    def run_backtest(self):
        # TODO: Implement walk-forward or simple backtest loop
        pass

class PerformanceMetrics:
    def calculate_metrics(self, trade_log):
        # TODO: Calculate Sharpe ratio, drawdown, win rate, etc. from trade log
        pass
```

### PHASE 3: UI Development (Weeks 5-8) - FUTURE
- Target: Simple, informative dashboard (potentially Raya-inspired).
  ```typescript
  // React/Next.js components (Placeholder)
  interface DashboardProps {
    performanceMetrics: Metrics; // From BacktestEngine/PerformanceMetrics
    tradeHistory: Trade[]; // From Logger
    // TODO: Implement basic data visualization (charts)
  }
  ```

### PHASE 4: Infrastructure (Weeks 9-12) - FUTURE
```typescript
// Target Tech Stack Integration (Placeholder)
const infrastructure = {
    deployment: 'Vercel (for UI)', // Simple script might use PythonAnywhere/EC2/local cron
    database: 'Supabase (Postgres)', // Alternative: Local SQLite first
    automation: 'n8n / cron / EventBridge', // If needed for scheduling/workflows
    api: 'Internal API (if UI needs it)', // Potentially FastAPI
    subscriptions: 'Stripe (If productized)' // Not applicable for personal bot
}
```

### PHASE 5: Testing & Launch (Weeks 13-16) - FUTURE
- Beta Testing (Self-testing in paper/live micro).
- Performance Monitoring (Requires logging/metrics).
- Refinement based on paper trading results.

## Modified Setup Instructions

1.  **Environment Setup**
    ```bash
    # Clone repository (Replace with your actual repo URL)
    git clone https://github.com/apanton2001/prometheus-bot.git # Or your current repo
    cd prometheus-bot

    # Create virtual environment
    python -m venv venv
    # Activate (Examples)
    # source venv/Scripts/activate  # Git Bash on Windows
    # .\venv\Scripts\Activate.ps1   # PowerShell on Windows
    # source venv/bin/activate      # Linux/macOS

    # Install dependencies (Update requirements.txt first)
    # Example: pip install -r requirements.txt
    # For current MVP:
    pip install alpaca-trade-api python-dotenv
    ```

2.  **Configuration**
    ```bash
    # Create .env file in the project root
    # Add your Alpaca Paper Trading Keys:
    ALPACA_KEY=your_key_here
    ALPACA_SECRET=your_secret_here
    ```

3.  **Running the Bot (Current MVP)**
    ```bash
    # Start the bot (ensure venv is active)
    python simple_alpaca_bot.py

    # To stop the bot: Press CTRL+C in the terminal
    ```
    *(Note: Logging currently goes only to console. `tail` command requires a log file, which isn't implemented yet).*

## Current Development Focus (Immediate Next Steps)

1.  **Immediate Tasks (Based on completed MVP):**
    *   **Validate Basic Functionality:** Let `simple_alpaca_bot.py` run for a period (e.g., 1 hour) and confirm paper trades appear correctly in the Alpaca dashboard when thresholds are met.
    *   **Implement Historical Fetch:** Modify `simple_alpaca_bot.py` (or create `src/bot/historical_data.py`) to fetch a window of historical data (e.g., 200 bars) needed for future feature calculation, addressing Alpaca/IEX data limitations as best possible.
    *   **Implement Basic Logging:** Modify `simple_alpaca_bot.py` (or create `src/bot/performance_logger.py`) to log trades and decisions to a simple CSV or SQLite database instead of just the console.
    *   **(Defer)** Do *not* start the backtesting framework (Phase 2) until basic historical data fetching and logging are working reliably in the core bot script.
2.  **Success Metrics (for this immediate focus):**
    *   Confirmed paper trades executed via Alpaca dashboard match bot logs.
    *   Script reliably fetches the last N bars of data for AAPL/TSLA without crashing.
    *   Decisions and simulated/paper trades are logged persistently (e.g., to a file or simple DB).
    *   Bot runs stably for at least an hour locally.

## Project Structure (Target - Based on Plan)

```
prometheus-bot/
├── api/
│   └── Tarriff Data.csv     # Asset from previous analysis (Archived/Separate?)
├── src/                     # Main source code
│   ├── bot/                 # Core bot logic
│   │   ├── __init__.py
│   │   ├── simple_alpaca_bot.py # Current MVP / Evolving bot script
│   │   ├── historical_data.py   # FUTURE: Module for data fetching
│   │   └── performance_logger.py  # FUTURE: Module for logging trades/performance
│   ├── backtesting/         # FUTURE: Backtesting components
│   │   ├── __init__.py
│   │   ├── engine.py
│   │   └── metrics.py
│   └── utils/               # FUTURE: Utility functions (e.g., config loading)
│       ├── __init__.py
│       └── config.py
├── tests/                   # FUTURE: Automated tests
├── user_data/               # Potential location for logs, models, db?
│   └── models/              # From previous ML attempts
│   └── data/                # From previous ML attempts
├── venv/                    # Virtual environment
├── .env                     # Environment variables (API Keys)
├── .env.example             # Example environment file
├── .gitignore
├── requirements.txt         # Project dependencies
├── tariff_analysis.py       # Script from previous validation MVP (Archive?)
└── README.md                # This file
```

## Known Issues / Challenges

*   **Historical Data Access:** The primary blocker for implementing ML or robust backtesting remains the difficulty in accessing sufficient historical daily/intraday data for key periods via free/low-cost Alpaca feeds (IEX). `yfinance` was also unreliable due to network issues. **This MUST be resolved before ML/backtesting is feasible.**
*   **Simple Logic:** The current BUY/SELL logic in `simple_alpaca_bot.py` is arbitrary and not a real strategy.
*   **No Backtesting:** The current MVP has no backtesting capability.
*   **Minimal Error Handling:** Needs improvement for API errors, data inconsistencies, etc.

## Configuration

The application is configured through environment variables. See `.env.example` for all available options.

Key configuration areas:
- API settings
- Database connection
- Redis configuration
- Trading parameters
- Content generation
- Monitoring setup

## Testing

Run the test suite:
```bash
pytest
```

For coverage report:
```bash
pytest --cov=.
```

## Deployment

See `deployment_checklist.md` for detailed deployment instructions.

Key deployment steps:
1. Configure environment
2. Set up infrastructure
3. Deploy services
4. Initialize database
5. Configure monitoring
6. Verify functionality

## Monitoring

The application includes comprehensive monitoring:

- **Prometheus**: Collects metrics
- **Grafana**: Visualizes metrics
- **Logging**: Structured JSON logs
- **Alerts**: Email & Slack notifications

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository. 