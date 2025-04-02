from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime, timedelta
from ...data.provider import MarketDataProvider
from ...core.auth import get_current_user
from ...core.config import settings

router = APIRouter(
    prefix="/data",
    tags=["data"],
    dependencies=[Depends(get_current_user)]
)

# Initialize market data provider
provider = MarketDataProvider(exchange_id=settings.EXCHANGE_ID)

@router.get("/ohlcv/{symbol}")
async def get_ohlcv(
    symbol: str,
    timeframe: str = '1h',
    since: Optional[datetime] = None,
    limit: int = 100
) -> Dict:
    """
    Get OHLCV data for a symbol.
    
    Args:
        symbol (str): Trading pair symbol
        timeframe (str): Timeframe for the data (default: '1h')
        since (Optional[datetime]): Start time for the data
        limit (int): Number of candles to fetch
        
    Returns:
        Dict: OHLCV data
    """
    try:
        df = provider.get_ohlcv(symbol, timeframe, since, limit)
        
        # Convert DataFrame to dict for response
        data = df.reset_index().to_dict(orient='records')
        
        return {
            "symbol": symbol,
            "timeframe": timeframe,
            "data": data,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching OHLCV data: {str(e)}"
        )

@router.get("/ticker/{symbol}")
async def get_ticker(symbol: str) -> Dict:
    """
    Get current ticker data for a symbol.
    
    Args:
        symbol (str): Trading pair symbol
        
    Returns:
        Dict: Ticker data
    """
    try:
        ticker = provider.get_ticker(symbol)
        return {
            "symbol": symbol,
            "data": ticker,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching ticker data: {str(e)}"
        )

@router.get("/orderbook/{symbol}")
async def get_orderbook(
    symbol: str,
    limit: int = 20
) -> Dict:
    """
    Get order book data for a symbol.
    
    Args:
        symbol (str): Trading pair symbol
        limit (int): Number of orders to fetch
        
    Returns:
        Dict: Order book data
    """
    try:
        orderbook = provider.get_orderbook(symbol, limit)
        return {
            "symbol": symbol,
            "data": orderbook,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching order book: {str(e)}"
        )

@router.get("/trades/{symbol}")
async def get_recent_trades(
    symbol: str,
    limit: int = 50
) -> Dict:
    """
    Get recent trades for a symbol.
    
    Args:
        symbol (str): Trading pair symbol
        limit (int): Number of trades to fetch
        
    Returns:
        Dict: Recent trades
    """
    try:
        trades = provider.get_recent_trades(symbol, limit)
        return {
            "symbol": symbol,
            "data": trades,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching recent trades: {str(e)}"
        )

@router.get("/symbols")
async def get_symbols() -> Dict:
    """
    Get list of available trading symbols.
    
    Returns:
        Dict: List of trading symbols
    """
    try:
        symbols = provider.get_symbols()
        return {
            "symbols": symbols,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching symbols: {str(e)}"
        )

@router.get("/exchange-info")
async def get_exchange_info() -> Dict:
    """
    Get exchange information.
    
    Returns:
        Dict: Exchange information
    """
    try:
        info = provider.get_exchange_info()
        return {
            "info": info,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching exchange info: {str(e)}"
        )

@router.post("/clear-cache")
async def clear_cache() -> Dict:
    """
    Clear the data cache.
    
    Returns:
        Dict: Cache status
    """
    try:
        provider.clear_cache()
        return {
            "status": "success",
            "message": "Cache cleared successfully",
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error clearing cache: {str(e)}"
        ) 