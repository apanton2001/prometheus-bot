# Stock Analysis Tool

This directory contains the AI-powered system for analyzing long-term stock investment opportunities based on user preferences and fundamental analysis.

## Features

- Industry/sector-based filtering (healthcare, tech, plastic surgery, etc.)
- Fundamental analysis with financial health metrics
- Competitive landscape assessment
- Risk-reward scoring
- Long-term growth potential evaluation

## Setup

1. Install dependencies
   ```
   pip install -r requirements.txt
   ```

2. Configure API keys
   ```
   cp .env.example .env
   # Add your financial data API keys to .env
   ```

3. Initialize the database
   ```
   python setup_database.py
   ```

## Usage

### Run Full Analysis
```
python analyze_stocks.py --sector "Technology" --market-cap "Large" --metrics "growth,value,momentum"
```

### Screen Stocks by Criteria
```
python screen_stocks.py --min-pe 5 --max-pe 20 --min-dividend 2.0 --min-roe 15
```

### Generate Investment Report
```
python generate_report.py --ticker AAPL --timeframe "5y" --output pdf
```

## Data Sources

- **Financial Data**: Yahoo Finance, Alpha Vantage
- **Fundamental Data**: SEC EDGAR, Financial Modeling Prep API
- **News & Sentiment**: News API, Twitter API
- **Industry Analysis**: Custom web scraping and analysis

## Evaluation Metrics

- Financial health score (0-100)
- Growth potential score (0-100)
- Risk assessment score (0-100)
- Competitive position score (0-100)
- Overall investment score (0-100)

## Output Formats

- CSV reports
- PDF reports
- Interactive web dashboard
- Email alerts 