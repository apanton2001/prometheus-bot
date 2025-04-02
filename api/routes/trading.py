from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from ...trading.paper_trading import PaperTrading
from ...trading.strategies.momentum_strategy import MomentumStrategy
from ...content.generators.trading_report import TradingReportGenerator
from ...core.auth import get_current_user
from ...core.config import settings
import numpy as np

router = APIRouter(
    prefix="/trading",
    tags=["trading"],
    dependencies=[Depends(get_current_user)]
)

# Initialize trading components
paper_trading = PaperTrading(
    initial_balance=settings.INITIAL_BALANCE,
    strategy=MomentumStrategy(settings.TRADING_STRATEGY_CONFIG)
)

report_generator = TradingReportGenerator(settings.CONTENT_GENERATOR_CONFIG)

@router.get("/positions")
async def get_positions() -> Dict:
    """
    Get all current positions.
    
    Returns:
        Dict: Current positions
    """
    try:
        positions = paper_trading.get_all_positions()
        return {
            "positions": positions,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting positions: {str(e)}"
        )

@router.get("/positions/{symbol}")
async def get_position(symbol: str) -> Dict:
    """
    Get position for a specific symbol.
    
    Args:
        symbol (str): Trading pair symbol
        
    Returns:
        Dict: Position details
    """
    try:
        position = paper_trading.get_position(symbol)
        if position is None:
            raise HTTPException(
                status_code=404,
                detail=f"No position found for {symbol}"
            )
        return {
            "symbol": symbol,
            "position": position,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting position: {str(e)}"
        )

@router.get("/trades")
async def get_trades(
    symbol: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Dict:
    """
    Get trade history.
    
    Args:
        symbol (Optional[str]): Filter by trading pair symbol
        start_date (Optional[datetime]): Filter by start date
        end_date (Optional[datetime]): Filter by end date
        
    Returns:
        Dict: Trade history
    """
    try:
        trades = paper_trading.get_trade_history()
        
        # Apply filters
        if symbol:
            trades = [t for t in trades if t['symbol'] == symbol]
        if start_date:
            trades = [t for t in trades if t['timestamp'] >= start_date]
        if end_date:
            trades = [t for t in trades if t['timestamp'] <= end_date]
        
        return {
            "trades": trades,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting trades: {str(e)}"
        )

@router.get("/performance")
async def get_performance() -> Dict:
    """
    Get trading performance metrics.
    
    Returns:
        Dict: Performance metrics
    """
    try:
        metrics = paper_trading.get_performance_metrics()
        return {
            "metrics": metrics,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting performance metrics: {str(e)}"
        )

@router.get("/balance")
async def get_balance() -> Dict:
    """
    Get current account balance.
    
    Returns:
        Dict: Account balance
    """
    try:
        balance = paper_trading.get_balance()
        return {
            "balance": balance,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error getting balance: {str(e)}"
        )

@router.post("/update")
async def update_market_data(symbol: str, data: pd.DataFrame) -> Dict:
    """
    Update market data and check for trading signals.
    
    Args:
        symbol (str): Trading pair symbol
        data (pd.DataFrame): Market data
        
    Returns:
        Dict: Update results
    """
    try:
        # Update market data and check for signals
        signal = paper_trading.update_market_data(symbol, data)
        
        # Check existing positions
        closed_positions = paper_trading.check_positions(symbol, data['close'].iloc[-1])
        
        return {
            "symbol": symbol,
            "signal": signal,
            "closed_positions": closed_positions,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating market data: {str(e)}"
        )

@router.get("/report/daily")
async def get_daily_report() -> Dict:
    """
    Get daily trading report.
    
    Returns:
        Dict: Daily report
    """
    try:
        # Get current positions and trade history
        positions = paper_trading.get_all_positions()
        trade_history = paper_trading.get_trade_history()
        performance_metrics = paper_trading.get_performance_metrics()
        
        # TODO: Get market data from data provider
        market_data = _get_sample_market_data()
        
        # Generate report
        report = report_generator.generate_daily_report(
            positions=positions,
            trade_history=trade_history,
            performance_metrics=performance_metrics,
            market_data=market_data
        )
        
        return {
            "report": report,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating daily report: {str(e)}"
        )

@router.get("/report/performance")
async def get_performance_report() -> Dict:
    """
    Get performance report.
    
    Returns:
        Dict: Performance report
    """
    try:
        # Get trade history and performance metrics
        trade_history = paper_trading.get_trade_history()
        performance_metrics = paper_trading.get_performance_metrics()
        
        # TODO: Get market data from data provider
        market_data = _get_sample_market_data()
        
        # Generate report
        report = report_generator.generate_performance_report(
            trade_history=trade_history,
            performance_metrics=performance_metrics,
            market_data=market_data
        )
        
        return {
            "report": report,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating performance report: {str(e)}"
        )

def _get_sample_market_data() -> pd.DataFrame:
    """
    Get sample market data for testing.
    TODO: Replace with actual market data fetching.
    
    Returns:
        pd.DataFrame: Sample market data
    """
    # Generate sample data
    dates = pd.date_range(
        start=datetime.utcnow() - timedelta(hours=100),
        periods=100,
        freq='1h'
    )
    
    # Generate random price data
    base_price = 50000  # Example BTC price
    prices = base_price + np.random.normal(0, 1000, 100).cumsum()
    
    data = pd.DataFrame({
        'open': prices + np.random.normal(0, 100, 100),
        'high': prices + abs(np.random.normal(0, 200, 100)),
        'low': prices - abs(np.random.normal(0, 200, 100)),
        'close': prices + np.random.normal(0, 100, 100),
        'volume': abs(np.random.normal(100, 20, 100))
    }, index=dates)
    
    # Ensure OHLCV relationships are valid
    data['high'] = data[['open', 'close']].max(axis=1) + abs(np.random.normal(0, 100, 100))
    data['low'] = data[['open', 'close']].min(axis=1) - abs(np.random.normal(0, 100, 100))
    
    return data 