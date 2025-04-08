# Prometheus Trading Bot (MVP Stage)

## Project Goal

To develop and operate a personal, automated algorithmic trading bot initially focused on US stocks (AAPL, TSLA) using the Alpaca brokerage API (Paper Trading environment). The ultimate goal is to incorporate machine learning models to identify potentially profitable trading opportunities based on various market indicators, starting with basic execution logic.

*(Self-Correction Note: While the long-term goal involves sophisticated ML, the immediate, validated state is much simpler).*

## Current Status (MVP v0.1 - Local Execution Verified)

*   **Phase:** Phase 1/2 - Incremental Enhancement. Basic MA Crossover logic with risk checks running locally.
*   **Functionality:** The current active script (`simple_alpaca_bot.py`) successfully:
    *   Connects to the Alpaca Paper Trading API using environment variables.
    *   Fetches a window of recent hourly bars for a hardcoded stock (AAPL) using a date range and the IEX feed.
    *   Calculates Simple Moving Averages (10-hour, 30-hour).
    *   Makes trading decisions (BUY/SELL/HOLD) based on MA Crossover logic.
    *   Checks for existing positions before placing BUY/SELL orders.
    *   Includes basic risk checks (buying power) before BUY orders.
    *   Calculates basic position sizing.
    *   Submits market orders to the Alpaca paper trading account if conditions are met.
    *   Runs in a loop with a configurable sleep timer.
    *   Logs actions to console and `trading_log.txt`.
    *   Includes basic API retry logic.
*   **Focus:** This existing MVP validates end-to-end mechanics with simple logic and basic risk management. **It does NOT implement sophisticated strategy or ML yet.** Previous ML validation attempts were **blocked by historical data access issues.**

## Implementation Timeline & Phases (Planned & In Progress)

```mermaid
gantt
    title Prometheus Trading Bot Implementation Timeline
    dateFormat  YYYY-MM-DD
    section Phase 1: MVP Trading Bot
    Basic API Connection & Price Fetching   :done,    des1, 2025-01-01, 2025-01-07
    Simple Trading Logic                    :done,    des2, 2025-01-01, 2025-01-07
    Paper Trading Order Submission          :done,    des3, 2025-01-01, 2025-01-07
    Basic Execution Loop                    :done,    des4, 2025-01-01, 2025-01-07
    Historical data integration             :active,  des5, 2025-01-08, 2025-01-14
    Performance logging                     :active,  des6, 2025-01-08, 2025-01-14

    section Phase 2: Backtesting Framework
    Develop a backtest engine               :planned, des7, 2025-01-15, 2025-01-21
    Calculate performance metrics           :planned, des8, 2025-01-15, 2025-01-21

    section Phase 3: UI Development
    Create a simple, informative dashboard  :planned, des9, 2025-01-22, 2025-02-04

    section Phase 4: Infrastructure
    Setup deployment                        :planned, des10, 2025-02-05, 2025-02-18
    Setup database                          :planned, des11, 2025-02-05, 2025-02-18
    Setup automation                        :planned, des12, 2025-02-05, 2025-02-18
    Setup API                               :planned, des13, 2025-02-05, 2025-02-18
    Setup subscriptions                     :planned, des14, 2025-02-05, 2025-02-18

    section Phase 5: Testing & Launch
    Beta testing                            :planned, des15, 2025-02-19, 2025-03-03
    Performance monitoring                  :planned, des16, 2025-02-19, 2025-03-03
    Refinement                              :planned, des17, 2025-02-19, 2025-03-03
```

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

## Current Development Focus

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