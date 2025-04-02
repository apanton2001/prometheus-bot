@echo off
REM Prometheus Bot Setup Script for Windows
echo Setting up Prometheus Bot...

REM Create Python virtual environment
echo Creating Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

REM Install required packages
echo Installing required packages...
pip install -U pip
pip install pandas numpy matplotlib scikit-learn

REM Clone Freqtrade repository
echo Cloning Freqtrade repository...
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade

REM Install Freqtrade
echo Installing Freqtrade...
pip install -e .

REM Setup Freqtrade
echo Setting up Freqtrade...
python setup.py install

REM Return to root directory
cd ..

REM Install additional requirements
echo Installing additional requirements...
pip install fastapi uvicorn psycopg2-binary

echo Setup complete! 
echo.
echo To use the bot:
echo 1. Activate the virtual environment: venv\Scripts\activate.bat
echo 2. Configure your API keys in trading/config/config.json
echo 3. Run the bot with: freqtrade trade -c trading/config/config.json 