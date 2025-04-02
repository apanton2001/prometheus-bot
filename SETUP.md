# Prometheus Bot Setup Guide

This guide provides comprehensive instructions for setting up the Prometheus Bot system for development and deployment.

## Prerequisites

### System Requirements
- Python 3.9+
- Node.js 18+ and npm 9+
- PostgreSQL 14+
- Redis (optional, for caching)
- Git

### Accounts Required
- GitHub account
- Exchange accounts (Kraken, KuCoin) with API access
- OpenAI API account
- Alpha Vantage/Yahoo Finance API keys for stock data
- Vercel account (for web deployment)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/prometheus-bot.git
cd prometheus-bot
```

### 2. Set Up Python Environment
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Set Up Database
```bash
# Log in to PostgreSQL
sudo -u postgres psql

# Create database and user
CREATE DATABASE prometheus;
CREATE USER prometheus_user WITH ENCRYPTED PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE prometheus TO prometheus_user;
```

### 4. Environment Configuration
```bash
# Copy example environment file
cp .env.example .env

# Edit .env file with your configuration
nano .env
```

Required environment variables:
```
# Database
DATABASE_URL=postgresql://prometheus_user:your_password@localhost/prometheus

# API Security
SECRET_KEY=your-random-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

# Exchange APIs
KRAKEN_API_KEY=your-kraken-api-key
KRAKEN_API_SECRET=your-kraken-api-secret
KUCOIN_API_KEY=your-kucoin-api-key
KUCOIN_API_SECRET=your-kucoin-api-secret
KUCOIN_API_PASSPHRASE=your-kucoin-passphrase

# OpenAI for Content Generation
OPENAI_API_KEY=your-openai-api-key

# Stock Data APIs
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-api-key

# Monitoring and Notifications
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

### 5. Database Migrations
```bash
# Run database migrations
alembic upgrade head
```

### 6. Frontend Setup
```bash
# Navigate to dashboard directory
cd dashboard

# Install dependencies
npm install

# Configure environment
cp .env.example .env.local
nano .env.local
```

## Component Setup

### Trading Bot
```bash
# Navigate to trading directory
cd trading

# Download historical data
python download_kraken_data.py --pairs BTC/USDT,ETH/USDT --timeframes 5m,1h --days 90

# Configure trading bot
cp user_data/config.example.json user_data/config.json
nano user_data/config.json

# Run backtesting to verify
freqtrade backtesting --strategy EnhancedMAStrategy --config user_data/config.json
```

### Content Bot
```bash
# Navigate to content directory
cd content

# Configure content templates
cp templates/config.example.json templates/config.json
nano templates/config.json

# Test content generation
python generate_content.py --type blog --topic "Cryptocurrency Trading" --length medium
```

### Service Bot
```bash
# Navigate to service directory
cd service

# Configure workflows
cp workflows/config.example.json workflows/config.json
nano workflows/config.json

# Initialize service database tables
python setup_database.py
```

### Stock Analysis
```bash
# Navigate to stock-analysis directory
cd stock-analysis

# Configure data sources
cp data_sources/config.example.json data_sources/config.json
nano data_sources/config.json

# Test analysis
python analyze_stocks.py --sector "Technology" --market-cap "Large" --metrics "growth,value,momentum"
```

## API Setup
```bash
# Navigate to api directory
cd api

# Run API server in development mode
uvicorn main:app --reload

# Test API endpoint
curl http://localhost:8000/health
```

## Running the System

### Start Backend Services
```bash
# Start API server
cd api
uvicorn main:app --host 0.0.0.0 --port 8000
```

### Start Frontend
```bash
# Start dashboard
cd dashboard
npm run dev
```

### Start Trading Bot
```bash
# Start trading bot in paper trading mode
cd trading
python run_bot.py --config user_data/config.json --strategy EnhancedMAStrategy
```

### Start Content Bot
```bash
# Start content generation service
cd content
python service.py
```

### Start Service Bot
```bash
# Start service automation
cd service
python service_bot.py
```

## Development Workflow

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make changes and write tests

3. Run tests:
   ```bash
   pytest
   ```

4. Commit changes:
   ```bash
   git add .
   git commit -m "Add your feature description"
   ```

5. Push changes:
   ```bash
   git push origin feature/your-feature-name
   ```

6. Create a pull request on GitHub

## Deployment

Refer to `DEPLOYMENT_CHECKLIST.md` for detailed deployment instructions.

## Troubleshooting

### Common Issues

#### Database Connection Issues
```bash
# Check PostgreSQL is running
systemctl status postgresql

# Test connection
psql -U prometheus_user -d prometheus -c "SELECT 1"
```

#### API Connection Issues
```bash
# Check API status
curl http://localhost:8000/health

# Check logs
cat logs/api.log
```

#### Trading Bot Issues
```bash
# Check exchange connection
python -c "import ccxt; kraken = ccxt.kraken({'apiKey': 'YOUR_API_KEY', 'secret': 'YOUR_SECRET'}); print(kraken.fetch_balance())"

# Check logs
cat logs/trading_bot.log
```

## Support

For assistance, please contact:
- Technical Support: [Email Address]
- Discord Channel: [Discord Link] 