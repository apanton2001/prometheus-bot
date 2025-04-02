@echo off
:: Setup script for Prometheus Trading Bot
:: This script will set up the trading bot environment for Windows users

echo ======================================================
echo      Prometheus Trading Bot - Setup Script           
echo ======================================================
echo.
echo This script will set up the Prometheus Trading Bot environment.
echo It will install dependencies, configure directories, and prepare
echo the bot for backtesting and paper trading.
echo.
echo Press ENTER to continue or CTRL+C to cancel...
pause >nul

:: Check for Python installation
echo.
echo === Checking Prerequisites ===
echo.
python --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓ Python found: [0m
    python --version
) else (
    echo [31m✗ Python not found. Please install Python 3.7 or later.[0m
    exit /b 1
)

:: Check for pip
pip --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓ Pip found: [0m
    pip --version
) else (
    echo [31m✗ Pip not found. Please install pip.[0m
    exit /b 1
)

:: Create necessary directories
echo.
echo === Creating Directories ===
echo.
mkdir user_data\data\kraken 2>nul
mkdir user_data\strategies 2>nul
mkdir user_data\logs 2>nul
echo [32m✓ Directory structure created.[0m

:: Install dependencies
echo.
echo === Installing Dependencies ===
echo.
echo Installing required Python packages...
pip install -r requirements.txt
if %errorlevel% equ 0 (
    echo [32m✓ Dependencies installed successfully.[0m
) else (
    echo [31m✗ Error installing dependencies. Please check the error message and try again.[0m
    exit /b 1
)

:: Check freqtrade installation
freqtrade --version >nul 2>&1
if %errorlevel% equ 0 (
    echo [32m✓ Freqtrade found.[0m
) else (
    echo [33m⚠ Freqtrade not found in PATH. Installing...[0m
    pip install freqtrade
    
    freqtrade --version >nul 2>&1
    if %errorlevel% equ 0 (
        echo [32m✓ Freqtrade installed successfully.[0m
    ) else (
        echo [31m✗ Error installing freqtrade. Please install it manually.[0m
        exit /b 1
    )
)

:: Check for configuration files
echo.
echo === Checking Configuration Files ===
echo.
if exist user_data\config.json (
    echo [32m✓ Configuration file found: user_data\config.json[0m
) else (
    echo [33m⚠ Configuration file not found. Creating default configuration...[0m
    copy user_data\backtest_config.json user_data\config.json >nul
    echo [32m✓ Default configuration created: user_data\config.json[0m
    echo [33m⚠ Please edit user_data\config.json to add your exchange API keys.[0m
)

:: Download sample data for testing
echo.
echo === Downloading Sample Data ===
echo.
set /p download_data=Do you want to download sample data for backtesting? (y/n): 

if /i "%download_data%"=="y" (
    echo Downloading sample data for BTC/USDT and ETH/USDT...
    python download_kraken_data.py --pairs BTC/USDT,ETH/USDT --timeframes 5m --days 30
    
    if %errorlevel% equ 0 (
        echo [32m✓ Sample data downloaded successfully.[0m
    ) else (
        echo [33m⚠ Error downloading sample data. You can download it later using download_kraken_data.py.[0m
    )
) else (
    echo [33m⚠ Skipping sample data download.[0m
)

:: Calculate risk parameters
echo.
echo === Setting Risk Parameters ===
echo.
set /p calculate_risk=Do you want to calculate risk parameters? (y/n): 

if /i "%calculate_risk%"=="y" (
    set /p portfolio_size=Enter your portfolio size (in USDT): 
    
    set /p risk_per_trade=Enter risk percentage per trade (default: 1): 
    if "%risk_per_trade%"=="" set risk_per_trade=1
    
    set /p stop_loss=Enter stop loss percentage (default: 2): 
    if "%stop_loss%"=="" set stop_loss=2
    
    set /p max_open_trades=Enter maximum number of open trades (default: 3): 
    if "%max_open_trades%"=="" set max_open_trades=3
    
    python risk_calculator.py --portfolio-size %portfolio_size% --risk-per-trade %risk_per_trade% --stop-loss %stop_loss% --max-open-trades %max_open_trades% --output user_data/risk_config.json
    
    if %errorlevel% equ 0 (
        echo [32m✓ Risk parameters calculated and saved to user_data\risk_config.json.[0m
    ) else (
        echo [33m⚠ Error calculating risk parameters.[0m
    )
) else (
    echo [33m⚠ Skipping risk parameter calculation.[0m
)

:: Final message
echo.
echo === Setup Complete ===
echo.
echo The Prometheus Trading Bot has been set up successfully.
echo You can now use the following commands:
echo.
echo [33mTo download historical data:[0m
echo   python download_kraken_data.py --pairs BTC/USDT,ETH/USDT --timeframes 5m,1h --days 90
echo.
echo [33mTo calculate risk parameters:[0m
echo   python risk_calculator.py --portfolio-size 1000 --risk-per-trade 1 --stop-loss 2 --max-open-trades 3
echo.
echo [33mTo run backtesting:[0m
echo   freqtrade backtesting --strategy EnhancedMAStrategy --config user_data/config.json
echo.
echo [33mTo run paper trading:[0m
echo   python run_bot.py --config user_data/config.json --strategy EnhancedMAStrategy
echo.
echo [33mTo view performance metrics:[0m
echo   Open http://127.0.0.1:8080 in your browser when the bot is running.
echo.
echo [32mHappy trading![0m

pause 