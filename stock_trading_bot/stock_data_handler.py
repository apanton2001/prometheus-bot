import pandas as pd
import numpy as np
import yfinance as yf
import pandas_ta as ta
import logging
import os
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Union, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('stock_data_handler')

class StockDataHandler:
    """
    Handles downloading, preprocessing, and managing stock market data
    for multiple symbols and timeframes.
    """
    
    def __init__(
        self,
        symbols: List[str],
        timeframes: List[str] = ['15m', '1h', '4h', '1d'],
        data_dir: str = 'data',
        use_cache: bool = True,
        max_workers: int = 8
    ):
        """
        Initialize the stock data handler.
        
        Args:
            symbols: List of stock symbols to download data for
            timeframes: List of timeframes to analyze
            data_dir: Directory to store cached data
            use_cache: Whether to use cached data (if available)
            max_workers: Maximum number of concurrent download workers
        """
        self.symbols = symbols
        self.timeframes = timeframes
        self.data_dir = data_dir
        self.use_cache = use_cache
        self.max_workers = max_workers
        
        # Mapping from our timeframe format to yfinance interval format
        self.tf_to_yf = {
            '1m': '1m',
            '5m': '5m',
            '15m': '15m',
            '30m': '30m',
            '1h': '1h',
            '4h': '4h',
            '1d': '1d',
            '1w': '1wk',
            '1mo': '1mo'
        }
        
        # Data storage
        self.data = {symbol: {tf: None for tf in timeframes} for symbol in symbols}
        self.sectors = {}
        self.macro_data = {}
        
        # Create data directory if it doesn't exist
        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'stocks'), exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'sectors'), exist_ok=True)
        os.makedirs(os.path.join(data_dir, 'macro'), exist_ok=True)
        
        # Load sector mappings
        self._load_sector_mappings()
        
        logger.info(f"Initialized StockDataHandler for {len(symbols)} symbols and {len(timeframes)} timeframes")
        
    def _load_sector_mappings(self) -> None:
        """
        Load sector mappings for symbols.
        If the mapping file doesn't exist, create a basic mapping by fetching info.
        """
        mapping_file = os.path.join(self.data_dir, 'sector_mapping.json')
        
        if os.path.exists(mapping_file):
            try:
                with open(mapping_file, 'r') as f:
                    self.sectors = json.load(f)
                logger.info(f"Loaded sector mappings for {len(self.sectors)} symbols")
                return
            except Exception as e:
                logger.error(f"Error loading sector mappings: {e}")
        
        # Create basic mapping by fetching info
        logger.info("Creating new sector mapping")
        self.sectors = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_symbol = {executor.submit(self._get_symbol_info, symbol): symbol for symbol in self.symbols}
            
            for future in as_completed(future_to_symbol):
                symbol = future_to_symbol[future]
                try:
                    info = future.result()
                    if info and 'sector' in info:
                        self.sectors[symbol] = {
                            'sector': info.get('sector', 'Unknown'),
                            'industry': info.get('industry', 'Unknown')
                        }
                except Exception as e:
                    logger.error(f"Error getting info for {symbol}: {e}")
        
        # Save mapping
        try:
            with open(mapping_file, 'w') as f:
                json.dump(self.sectors, f, indent=4)
            logger.info(f"Saved sector mappings for {len(self.sectors)} symbols")
        except Exception as e:
            logger.error(f"Error saving sector mappings: {e}")
    
    def _get_symbol_info(self, symbol: str) -> dict:
        """
        Get info for a specific symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock info
        """
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info
        except Exception as e:
            logger.error(f"Error getting info for {symbol}: {e}")
            return {}
    
    def _get_cache_path(self, symbol: str, timeframe: str) -> str:
        """
        Get the cache file path for a specific symbol and timeframe.
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe
            
        Returns:
            Path to cache file
        """
        return os.path.join(self.data_dir, 'stocks', f"{symbol}_{timeframe}.csv")
    
    def _get_required_period(self, timeframe: str) -> Tuple[str, int]:
        """
        Get the required period for a specific timeframe.
        Returns a tuple of (period, period_count).
        
        Args:
            timeframe: Timeframe string
            
        Returns:
            Tuple of period string and count
        """
        # Define periods for each timeframe to ensure sufficient historical data
        tf_periods = {
            '1m': ('d', 7),      # 7 days of 1-minute data
            '5m': ('d', 60),     # 60 days of 5-minute data
            '15m': ('d', 60),    # 60 days of 15-minute data
            '30m': ('d', 60),    # 60 days of 30-minute data
            '1h': ('d', 730),    # 2 years of hourly data
            '4h': ('y', 5),      # 5 years of 4-hour data
            '1d': ('y', 10),     # 10 years of daily data
            '1w': ('y', 20),     # 20 years of weekly data
            '1mo': ('y', 50)     # 50 years of monthly data
        }
        
        return tf_periods.get(timeframe, ('d', 30))  # Default: 30 days
    
    def download_data(self, symbol: str, timeframe: str, force_download: bool = False) -> Optional[pd.DataFrame]:
        """
        Download data for a specific symbol and timeframe.
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe string
            force_download: Whether to force download even if cache exists
            
        Returns:
            DataFrame with OHLCV data or None if download failed
        """
        cache_path = self._get_cache_path(symbol, timeframe)
        
        # Check cache first
        if self.use_cache and os.path.exists(cache_path) and not force_download:
            try:
                df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                logger.info(f"Loaded cached data for {symbol} ({timeframe}) from {cache_path}")
                return df
            except Exception as e:
                logger.error(f"Error loading cached data for {symbol} ({timeframe}): {e}")
        
        # Download data
        try:
            # Get appropriate period for timeframe
            period_type, period_count = self._get_required_period(timeframe)
            period = f"{period_count}{period_type}"
            
            # Get appropriate interval for yfinance
            interval = self.tf_to_yf.get(timeframe, '1d')
            
            logger.info(f"Downloading {symbol} data for {timeframe} (period={period}, interval={interval})")
            
            # Download data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period, interval=interval)
            
            # Handle empty dataframe
            if df.empty:
                logger.warning(f"No data downloaded for {symbol} ({timeframe})")
                return None
            
            # Fix column names (yfinance uses capitalized column names)
            df.columns = [col.lower() for col in df.columns]
            
            # Make sure we have all required columns
            required_columns = ['open', 'high', 'low', 'close', 'volume']
            for col in required_columns:
                if col not in df.columns:
                    logger.error(f"Missing required column {col} for {symbol} ({timeframe})")
                    return None
            
            # Drop unnecessary columns
            for col in df.columns:
                if col not in required_columns and col != 'dividends' and col != 'stock splits':
                    df = df.drop(columns=[col])
            
            # Save to cache
            df.to_csv(cache_path)
            logger.info(f"Downloaded and cached {len(df)} rows of {symbol} ({timeframe}) data")
            
            return df
            
        except Exception as e:
            logger.error(f"Error downloading data for {symbol} ({timeframe}): {e}")
            return None
    
    def download_all_data(self, force_download: bool = False) -> None:
        """
        Download data for all symbols and timeframes.
        
        Args:
            force_download: Whether to force download even if cache exists
        """
        logger.info(f"Downloading data for {len(self.symbols)} symbols and {len(self.timeframes)} timeframes")
        
        # Create a list of all download tasks
        download_tasks = []
        for symbol in self.symbols:
            for timeframe in self.timeframes:
                download_tasks.append((symbol, timeframe))
        
        # Download data in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_task = {
                executor.submit(self.download_data, symbol, timeframe, force_download): (symbol, timeframe)
                for symbol, timeframe in download_tasks
            }
            
            for future in as_completed(future_to_task):
                symbol, timeframe = future_to_task[future]
                try:
                    df = future.result()
                    if df is not None:
                        self.data[symbol][timeframe] = df
                except Exception as e:
                    logger.error(f"Error handling download for {symbol} ({timeframe}): {e}")
        
        logger.info("Completed downloading all data")
    
    def download_sector_data(self, force_download: bool = False) -> None:
        """
        Download data for sector ETFs to analyze sector performance.
        
        Args:
            force_download: Whether to force download even if cache exists
        """
        # Key sector ETFs
        sector_etfs = {
            'XLK': 'Technology',
            'XLF': 'Financial',
            'XLV': 'Healthcare',
            'XLE': 'Energy',
            'XLY': 'Consumer Discretionary',
            'XLP': 'Consumer Staples',
            'XLI': 'Industrial',
            'XLB': 'Materials',
            'XLU': 'Utilities',
            'XLRE': 'Real Estate',
            'XLC': 'Communication Services',
            'SPY': 'S&P 500'  # For reference
        }
        
        logger.info(f"Downloading data for {len(sector_etfs)} sector ETFs")
        
        sector_data = {}
        
        # Download data for each sector ETF
        for symbol, sector in sector_etfs.items():
            cache_path = os.path.join(self.data_dir, 'sectors', f"{symbol}_1d.csv")
            
            # Check cache first
            if self.use_cache and os.path.exists(cache_path) and not force_download:
                try:
                    df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                    logger.info(f"Loaded cached data for sector ETF {symbol}")
                    sector_data[sector] = df
                    continue
                except Exception as e:
                    logger.error(f"Error loading cached data for sector ETF {symbol}: {e}")
            
            # Download data
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period='2y', interval='1d')
                
                if df.empty:
                    logger.warning(f"No data downloaded for sector ETF {symbol}")
                    continue
                
                # Fix column names
                df.columns = [col.lower() for col in df.columns]
                
                # Save to cache
                df.to_csv(cache_path)
                logger.info(f"Downloaded and cached {len(df)} rows of {symbol} sector data")
                
                sector_data[sector] = df
                
            except Exception as e:
                logger.error(f"Error downloading data for sector ETF {symbol}: {e}")
        
        # Store sector data
        self.sector_data = sector_data
        logger.info(f"Completed downloading data for {len(sector_data)} sectors")
    
    def download_macro_data(self, force_download: bool = False) -> None:
        """
        Download macroeconomic indicator data.
        
        Args:
            force_download: Whether to force download even if cache exists
        """
        # Key macro indicators (use VIX, US10Y, DXY, etc.)
        macro_symbols = {
            '^VIX': 'Volatility',
            '^TNX': 'US10Y',
            'DX-Y.NYB': 'DollarIndex',
            'GC=F': 'Gold',
            'CL=F': 'OilWTI'
        }
        
        logger.info(f"Downloading data for {len(macro_symbols)} macro indicators")
        
        macro_data = {}
        
        # Download data for each macro indicator
        for symbol, name in macro_symbols.items():
            cache_path = os.path.join(self.data_dir, 'macro', f"{name}_1d.csv")
            
            # Check cache first
            if self.use_cache and os.path.exists(cache_path) and not force_download:
                try:
                    df = pd.read_csv(cache_path, index_col=0, parse_dates=True)
                    logger.info(f"Loaded cached data for macro indicator {name}")
                    macro_data[name] = df
                    continue
                except Exception as e:
                    logger.error(f"Error loading cached data for macro indicator {name}: {e}")
            
            # Download data
            try:
                ticker = yf.Ticker(symbol)
                df = ticker.history(period='2y', interval='1d')
                
                if df.empty:
                    logger.warning(f"No data downloaded for macro indicator {name}")
                    continue
                
                # Fix column names
                df.columns = [col.lower() for col in df.columns]
                
                # Save to cache
                df.to_csv(cache_path)
                logger.info(f"Downloaded and cached {len(df)} rows of {name} macro data")
                
                macro_data[name] = df
                
            except Exception as e:
                logger.error(f"Error downloading data for macro indicator {name}: {e}")
        
        # Store macro data
        self.macro_data = macro_data
        logger.info(f"Completed downloading data for {len(macro_data)} macro indicators")
    
    def get_data(self, symbol: str, timeframe: str) -> Optional[pd.DataFrame]:
        """
        Get data for a specific symbol and timeframe.
        Downloads data if necessary.
        
        Args:
            symbol: Stock symbol
            timeframe: Timeframe string
            
        Returns:
            DataFrame with OHLCV data or None if not available
        """
        # Check if we already have the data
        if symbol in self.data and timeframe in self.data[symbol] and self.data[symbol][timeframe] is not None:
            return self.data[symbol][timeframe]
        
        # Download data if necessary
        df = self.download_data(symbol, timeframe)
        if df is not None:
            self.data[symbol][timeframe] = df
            
        return df
    
    def get_sector_data(self) -> Dict[str, pd.DataFrame]:
        """
        Get sector performance data.
        Downloads data if necessary.
        
        Returns:
            Dictionary mapping sector names to DataFrames
        """
        if not self.sector_data:
            self.download_sector_data()
            
        return self.sector_data
    
    def get_macro_data(self) -> Dict[str, pd.DataFrame]:
        """
        Get macroeconomic indicator data.
        Downloads data if necessary.
        
        Returns:
            Dictionary mapping indicator names to DataFrames
        """
        if not self.macro_data:
            self.download_macro_data()
            
        return self.macro_data
    
    def get_symbol_sector(self, symbol: str) -> str:
        """
        Get the sector for a specific symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Sector name or 'Unknown' if not available
        """
        if symbol in self.sectors:
            return self.sectors[symbol].get('sector', 'Unknown')
        return 'Unknown'
    
    def get_symbols_by_sector(self, sector: str) -> List[str]:
        """
        Get all symbols in a specific sector.
        
        Args:
            sector: Sector name
            
        Returns:
            List of stock symbols in the sector
        """
        return [
            symbol for symbol, info in self.sectors.items()
            if info.get('sector') == sector
        ]
    
    def preprocess_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess data to fix common issues.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            Preprocessed DataFrame
        """
        if df is None or df.empty:
            return df
        
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Handle missing values
        if df.isnull().any().any():
            # Fill missing OHLC with previous values
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].fillna(method='ffill')
            
            # Fill missing volume with 0
            df['volume'] = df['volume'].fillna(0)
        
        # Handle duplicate indices
        if df.index.duplicated().any():
            logger.warning(f"Found {df.index.duplicated().sum()} duplicate timestamps in data")
            df = df[~df.index.duplicated(keep='first')]
        
        # Sort index
        df = df.sort_index()
        
        return df
    
    def calculate_returns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate returns for a price series.
        
        Args:
            df: DataFrame with OHLCV data
            
        Returns:
            DataFrame with added return columns
        """
        if df is None or df.empty:
            return df
        
        # Make a copy to avoid modifying the original
        df = df.copy()
        
        # Calculate returns
        df['daily_return'] = df['close'].pct_change()
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        
        # Calculate cumulative returns
        df['cumulative_return'] = (1 + df['daily_return']).cumprod() - 1
        
        return df
    
    def resample_timeframe(self, df: pd.DataFrame, source_tf: str, target_tf: str) -> Optional[pd.DataFrame]:
        """
        Resample data from one timeframe to another.
        
        Args:
            df: DataFrame with OHLCV data
            source_tf: Source timeframe
            target_tf: Target timeframe
            
        Returns:
            Resampled DataFrame or None if resampling is not possible
        """
        if df is None or df.empty:
            return None
        
        # Define mapping for pandas resampling rule
        tf_to_rule = {
            '1m': '1min',
            '5m': '5min',
            '15m': '15min',
            '30m': '30min',
            '1h': '1H',
            '4h': '4H',
            '1d': 'D',
            '1w': 'W',
            '1mo': 'M'
        }
        
        # Check if resampling is possible
        if source_tf not in tf_to_rule or target_tf not in tf_to_rule:
            logger.error(f"Invalid timeframe for resampling: {source_tf} -> {target_tf}")
            return None
        
        source_rule = tf_to_rule[source_tf]
        target_rule = tf_to_rule[target_tf]
        
        # We can only resample to a higher timeframe (e.g. 1m -> 5m, not 1h -> 1m)
        source_minutes = self._timeframe_to_minutes(source_tf)
        target_minutes = self._timeframe_to_minutes(target_tf)
        
        if source_minutes > target_minutes:
            logger.error(f"Cannot resample from higher to lower timeframe: {source_tf} -> {target_tf}")
            return None
        
        try:
            # Make a copy to avoid modifying the original
            df = df.copy()
            
            # Resample
            resampled = df.resample(target_rule).agg({
                'open': 'first',
                'high': 'max',
                'low': 'min',
                'close': 'last',
                'volume': 'sum'
            })
            
            # Drop rows with NaN values
            resampled = resampled.dropna()
            
            logger.info(f"Resampled data from {source_tf} to {target_tf}: {len(df)} -> {len(resampled)} rows")
            
            return resampled
            
        except Exception as e:
            logger.error(f"Error resampling data from {source_tf} to {target_tf}: {e}")
            return None
    
    def _timeframe_to_minutes(self, timeframe: str) -> int:
        """
        Convert a timeframe string to minutes for comparison.
        
        Args:
            timeframe: Timeframe string
            
        Returns:
            Equivalent minutes
        """
        if timeframe == '1m':
            return 1
        elif timeframe == '5m':
            return 5
        elif timeframe == '15m':
            return 15
        elif timeframe == '30m':
            return 30
        elif timeframe == '1h':
            return 60
        elif timeframe == '4h':
            return 240
        elif timeframe == '1d':
            return 1440  # 24 hours
        elif timeframe == '1w':
            return 10080  # 7 days
        elif timeframe == '1mo':
            return 43200  # 30 days (approx)
        else:
            return 0
    
    def get_sp500_symbols(self) -> List[str]:
        """
        Get the list of current S&P 500 constituents.
        
        Returns:
            List of S&P 500 stock symbols
        """
        try:
            # Download S&P 500 components from Wikipedia
            url = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
            tables = pd.read_html(url)
            df = tables[0]
            symbols = df['Symbol'].tolist()
            
            # Clean symbols (remove dots and convert to uppercase)
            symbols = [symbol.replace('.', '-').upper() for symbol in symbols]
            
            logger.info(f"Downloaded {len(symbols)} S&P 500 symbols")
            
            return symbols
            
        except Exception as e:
            logger.error(f"Error getting S&P 500 symbols: {e}")
            
            # Fallback to default set of major components
            default_symbols = [
                'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 
                'TSLA', 'BRK-B', 'UNH', 'JNJ', 'JPM',
                'V', 'PG', 'XOM', 'HD', 'CVX',
                'MA', 'BAC', 'ABBV', 'PFE', 'AVGO',
                'COST', 'DIS', 'KO', 'PEP', 'TMO',
                'CSCO', 'ADBE', 'ABT', 'CRM', 'VZ'
            ]
            
            logger.info(f"Using fallback list of {len(default_symbols)} major S&P 500 components")
            
            return default_symbols


# Usage example
if __name__ == "__main__":
    # Initialize data handler with top S&P 500 components
    data_handler = StockDataHandler(
        symbols=['SPY', 'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META'],
        timeframes=['1d', '4h', '1h', '15m'],
        data_dir='../data',
        use_cache=True
    )
    
    # Download data for all symbols and timeframes
    data_handler.download_all_data()
    
    # Download sector data
    data_handler.download_sector_data()
    
    # Download macro data
    data_handler.download_macro_data()
    
    # Get all S&P 500 symbols
    sp500_symbols = data_handler.get_sp500_symbols()
    print(f"S&P 500 symbols: {len(sp500_symbols)}")
    
    # Get data for a specific symbol and timeframe
    spy_daily = data_handler.get_data('SPY', '1d')
    if spy_daily is not None:
        # Calculate returns
        spy_daily = data_handler.calculate_returns(spy_daily)
        
        # Print recent data
        print(spy_daily.tail()) 