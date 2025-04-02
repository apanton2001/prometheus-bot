#!/bin/bash
# Setup script for Prometheus Trading Bot
# This script will set up the trading bot environment and prepare it for use

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to display section headers
section() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Function to display success messages
success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Function to display warning messages
warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

# Function to display error messages
error() {
    echo -e "${RED}✗ $1${NC}"
}

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if script is run with sudo
if [ "$EUID" -eq 0 ]; then
    error "Please do not run this script with sudo or as root."
    exit 1
fi

# Welcome message
echo -e "${BLUE}"
echo "======================================================"
echo "      Prometheus Trading Bot - Setup Script           "
echo "======================================================"
echo -e "${NC}"
echo "This script will set up the Prometheus Trading Bot environment."
echo "It will install dependencies, configure directories, and prepare"
echo "the bot for backtesting and paper trading."
echo ""
echo "Press ENTER to continue or CTRL+C to cancel..."
read

# Check for Python installation
section "Checking Prerequisites"
if command_exists python3; then
    PYTHON="python3"
    success "Python 3 found: $(python3 --version)"
elif command_exists python; then
    PYTHON="python"
    success "Python found: $(python --version)"
else
    error "Python not found. Please install Python 3.7 or later."
    exit 1
fi

# Check for pip
if command_exists pip3; then
    PIP="pip3"
    success "Pip found: $(pip3 --version)"
elif command_exists pip; then
    PIP="pip"
    success "Pip found: $(pip --version)"
else
    error "Pip not found. Please install pip."
    exit 1
fi

# Check for git
if command_exists git; then
    success "Git found: $(git --version)"
else
    warning "Git not found. Some features may not work properly."
fi

# Create necessary directories
section "Creating Directories"
mkdir -p user_data/data/kraken
mkdir -p user_data/strategies
mkdir -p user_data/logs
success "Directory structure created."

# Install dependencies
section "Installing Dependencies"
echo "Installing required Python packages..."
$PIP install -r requirements.txt

if [ $? -eq 0 ]; then
    success "Dependencies installed successfully."
else
    error "Error installing dependencies. Please check the error message and try again."
    exit 1
fi

# Check freqtrade installation
if command_exists freqtrade; then
    success "Freqtrade found: $(freqtrade --version)"
else
    warning "Freqtrade not found in PATH. Installing..."
    $PIP install freqtrade
    
    if command_exists freqtrade; then
        success "Freqtrade installed successfully."
    else
        error "Error installing freqtrade. Please install it manually."
        exit 1
    fi
fi

# Check for configuration files
section "Checking Configuration Files"
if [ -f "user_data/config.json" ]; then
    success "Configuration file found: user_data/config.json"
else
    warning "Configuration file not found. Creating default configuration..."
    cp user_data/backtest_config.json user_data/config.json
    success "Default configuration created: user_data/config.json"
    warning "Please edit user_data/config.json to add your exchange API keys."
fi

# Set file permissions
chmod +x download_kraken_data.py
chmod +x risk_calculator.py
chmod +x run_bot.py
success "Executable permissions set for scripts."

# Download sample data for testing
section "Downloading Sample Data"
echo "Do you want to download sample data for backtesting? (y/n)"
read download_data

if [ "$download_data" = "y" ] || [ "$download_data" = "Y" ]; then
    echo "Downloading sample data for BTC/USDT and ETH/USDT..."
    $PYTHON download_kraken_data.py --pairs BTC/USDT,ETH/USDT --timeframes 5m --days 30
    
    if [ $? -eq 0 ]; then
        success "Sample data downloaded successfully."
    else
        warning "Error downloading sample data. You can download it later using download_kraken_data.py."
    fi
else
    warning "Skipping sample data download."
fi

# Calculate risk parameters
section "Setting Risk Parameters"
echo "Do you want to calculate risk parameters? (y/n)"
read calculate_risk

if [ "$calculate_risk" = "y" ] || [ "$calculate_risk" = "Y" ]; then
    echo "Enter your portfolio size (in USDT):"
    read portfolio_size
    
    echo "Enter risk percentage per trade (default: 1):"
    read risk_per_trade
    risk_per_trade=${risk_per_trade:-1}
    
    echo "Enter stop loss percentage (default: 2):"
    read stop_loss
    stop_loss=${stop_loss:-2}
    
    echo "Enter maximum number of open trades (default: 3):"
    read max_open_trades
    max_open_trades=${max_open_trades:-3}
    
    $PYTHON risk_calculator.py --portfolio-size $portfolio_size --risk-per-trade $risk_per_trade --stop-loss $stop_loss --max-open-trades $max_open_trades --output user_data/risk_config.json
    
    if [ $? -eq 0 ]; then
        success "Risk parameters calculated and saved to user_data/risk_config.json."
    else
        warning "Error calculating risk parameters."
    fi
else
    warning "Skipping risk parameter calculation."
fi

# Final message
section "Setup Complete"
echo -e "The Prometheus Trading Bot has been set up successfully."
echo -e "You can now use the following commands:"
echo -e ""
echo -e "${YELLOW}To download historical data:${NC}"
echo -e "  python download_kraken_data.py --pairs BTC/USDT,ETH/USDT --timeframes 5m,1h --days 90"
echo -e ""
echo -e "${YELLOW}To calculate risk parameters:${NC}"
echo -e "  python risk_calculator.py --portfolio-size 1000 --risk-per-trade 1 --stop-loss 2 --max-open-trades 3"
echo -e ""
echo -e "${YELLOW}To run backtesting:${NC}"
echo -e "  freqtrade backtesting --strategy EnhancedMAStrategy --config user_data/config.json"
echo -e ""
echo -e "${YELLOW}To run paper trading:${NC}"
echo -e "  python run_bot.py --config user_data/config.json --strategy EnhancedMAStrategy"
echo -e ""
echo -e "${YELLOW}To view performance metrics:${NC}"
echo -e "  Open http://127.0.0.1:8080 in your browser when the bot is running."
echo -e ""
echo -e "${GREEN}Happy trading!${NC}" 