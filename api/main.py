from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import subprocess
from pathlib import Path
import os
import sys

# Add the project root to path so we can import trading modules
sys.path.append(str(Path(__file__).resolve().parent.parent))

app = FastAPI(
    title="Prometheus Bot API",
    description="API for controlling and monitoring the Prometheus Bot",
    version="0.1.0",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class BotStatus(BaseModel):
    status: str
    active_trades: int
    total_profit: float
    uptime: str

class StartBot(BaseModel):
    config_file: str = "trading/config/config.json"
    strategy: str = "MomentumStrategy"

class BacktestRequest(BaseModel):
    strategy: str
    timerange: str
    pairs: list[str]
    
# Routes
@app.get("/")
async def root():
    return {
        "message": "Welcome to Prometheus Bot API",
        "version": "0.1.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "components": {
            "api": "up",
            "database": "up",
            "trading_engine": "up"
        }
    }

@app.get("/status", response_model=BotStatus)
async def get_status():
    """Get the current status of the trading bot"""
    # In production, this should check the actual bot status
    return {
        "status": "running",
        "active_trades": 2,
        "total_profit": 105.25,
        "uptime": "1d 3h 45m"
    }

@app.post("/start")
async def start_bot(data: StartBot):
    """Start the trading bot with the specified configuration"""
    try:
        cmd = [
            "freqtrade", 
            "trade", 
            "--config", 
            data.config_file,
            "--strategy",
            data.strategy
        ]
        
        # In a real implementation, you would handle this differently,
        # potentially using a job queue or background task
        subprocess.Popen(cmd)
        return {"message": "Bot started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start bot: {str(e)}")

@app.post("/stop")
async def stop_bot():
    """Stop the trading bot"""
    # This would need to gracefully stop the bot process
    return {"message": "Bot stopped successfully"}

@app.post("/backtest")
async def run_backtest(data: BacktestRequest):
    """Run a backtest with the specified parameters"""
    try:
        from trading.utils.backtest_helper import run_backtest
        
        # This would typically be handled as a background task
        result = run_backtest(
            data.strategy,
            "trading/config/config.json",
            data.timerange,
            pairs=data.pairs
        )
        
        return {"message": "Backtest completed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Backtest failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 