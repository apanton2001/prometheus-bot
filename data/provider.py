from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
from ...core.config import settings
from ...core.logger import get_logger

logger = get_logger(__name__)

class MarketDataProvider:
    """
    Provider for fetching market data from various sources.
    Currently supports CCXT exchanges.
    """
    
    def __init__(self, exchange_id: str = "binance"):
        """
        Initialize the market data provider.
        
        Args:
            exchange_id (str): ID of the exchange to use (default: "binance")
        """
        self.exchange = getattr(ccxt, exchange_id)({
            'enableRateLimit': True,
            'timeout': 30000,
        })
        
        # Load markets
        self.exchange.load_markets()
        
        # Cache for market data
        self._cache: Dict[str, pd.DataFrame] = {}
        self._cache_timestamps: Dict[str, datetime] = {}
        self._cache_duration = timedelta(minutes=5)
    
    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = '1h',
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> pd.DataFrame:
        """
        Get OHLCV data for a symbol.
        
        Args:
            symbol (str): Trading pair symbol
            timeframe (str): Timeframe for the data (default: '1h')
            since (Optional[datetime]): Start time for the data
            limit (int): Number of candles to fetch
            
        Returns:
            pd.DataFrame: OHLCV data
        """
        try:
            # Check cache first
            cache_key = f"{symbol}_{timeframe}"
            if self._is_cache_valid(cache_key):
                return self._cache[cache_key]
            
            # Convert datetime to timestamp
            since_ts = int(since.timestamp() * 1000) if since else None
            
            # Fetch data from exchange
            ohlcv = self.exchange.fetch_ohlcv(
                symbol,
                timeframe=timeframe,
                since=since_ts,
                limit=limit
            )
            
            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            
            # Convert timestamp to datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            
            # Cache the data
            self._cache[cache_key] = df
            self._cache_timestamps[cache_key] = datetime.utcnow()
            
            return df
            
        except Exception as e:
            logger.error(f"Error fetching OHLCV data: {str(e)}")
            raise
    
    def get_ticker(self, symbol: str) -> Dict:
        """
        Get current ticker data for a symbol.
        
        Args:
            symbol (str): Trading pair symbol
            
        Returns:
            Dict: Ticker data
        """
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return {
                'symbol': symbol,
                'last': ticker['last'],
                'bid': ticker['bid'],
                'ask': ticker['ask'],
                'volume': ticker['baseVolume'],
                'timestamp': datetime.fromtimestamp(ticker['timestamp'] / 1000)
            }
        except Exception as e:
            logger.error(f"Error fetching ticker data: {str(e)}")
            raise
    
    def get_orderbook(self, symbol: str, limit: int = 20) -> Dict:
        """
        Get order book data for a symbol.
        
        Args:
            symbol (str): Trading pair symbol
            limit (int): Number of orders to fetch
            
        Returns:
            Dict: Order book data
        """
        try:
            orderbook = self.exchange.fetch_order_book(symbol, limit=limit)
            return {
                'symbol': symbol,
                'bids': orderbook['bids'],
                'asks': orderbook['asks'],
                'timestamp': datetime.fromtimestamp(orderbook['timestamp'] / 1000)
            }
        except Exception as e:
            logger.error(f"Error fetching order book: {str(e)}")
            raise
    
    def get_recent_trades(self, symbol: str, limit: int = 50) -> List[Dict]:
        """
        Get recent trades for a symbol.
        
        Args:
            symbol (str): Trading pair symbol
            limit (int): Number of trades to fetch
            
        Returns:
            List[Dict]: Recent trades
        """
        try:
            trades = self.exchange.fetch_trades(symbol, limit=limit)
            return [{
                'id': trade['id'],
                'timestamp': datetime.fromtimestamp(trade['timestamp'] / 1000),
                'price': trade['price'],
                'amount': trade['amount'],
                'side': trade['side'],
                'cost': trade['cost']
            } for trade in trades]
        except Exception as e:
            logger.error(f"Error fetching recent trades: {str(e)}")
            raise
    
    def get_symbols(self) -> List[str]:
        """
        Get list of available trading symbols.
        
        Returns:
            List[str]: List of trading symbols
        """
        try:
            return list(self.exchange.markets.keys())
        except Exception as e:
            logger.error(f"Error fetching symbols: {str(e)}")
            raise
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """
        Check if cached data is still valid.
        
        Args:
            cache_key (str): Cache key to check
            
        Returns:
            bool: True if cache is valid, False otherwise
        """
        if cache_key not in self._cache_timestamps:
            return False
        
        cache_age = datetime.utcnow() - self._cache_timestamps[cache_key]
        return cache_age < self._cache_duration
    
    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()
        self._cache_timestamps.clear()
    
    def get_exchange_info(self) -> Dict:
        """
        Get exchange information.
        
        Returns:
            Dict: Exchange information
        """
        try:
            return {
                'id': self.exchange.id,
                'name': self.exchange.name,
                'version': self.exchange.version,
                'timeframes': self.exchange.timeframes,
                'has': self.exchange.has,
                'rateLimit': self.exchange.rateLimit,
                'urls': self.exchange.urls
            }
        except Exception as e:
            logger.error(f"Error fetching exchange info: {str(e)}")
            raise 