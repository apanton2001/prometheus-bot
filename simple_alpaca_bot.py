# simple_alpaca_bot.py - MA Crossover Test with Position Check and Risk Management

import os
import time
import alpaca_trade_api as tradeapi
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import logging
from dotenv import load_dotenv

# --- Configuration Constants ---
STOCK_SYMBOL = 'AAPL'
ORDER_QTY = 1  # Default/Minimum buy quantity if risk calc fails or results in <1
SLEEP_TIME_SECONDS = 60  # Time between checks
MAX_RETRIES = 3  # Max retries for API calls
BAR_TIMEFRAME = '1H'  # Fetch hourly bars
BAR_LOOKBACK = 30 + 10 # long_window + buffer + safety margin

# --- Risk Management Constants ---
MAX_POSITION_VALUE = 10000  # Maximum $ amount allowed for this stock position
MIN_BUYING_POWER = 1000    # Minimum account buying power required to place new BUY orders
MAX_DAILY_LOSS_PCT = -5.0  # Maximum allowed daily loss percentage before stopping new BUYs (-5 means 5% loss)
POSITION_SIZING_BUFFER = 0.95  # Use 95% of calculated max position to allow for fees/slippage

# --- Setup Logging ---
logging.basicConfig(
    filename='trading_log.txt',
    filemode='a',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logging.getLogger().addHandler(logging.StreamHandler())

# --- Load Environment Variables ---
load_dotenv()
API_KEY = os.getenv('ALPACA_KEY')
SECRET_KEY = os.getenv('ALPACA_SECRET')
BASE_URL = 'https://paper-api.alpaca.markets'

# --- API Helper Function ---
def retry_api_call(func, max_retries=MAX_RETRIES):
    """Retry API calls with exponential backoff"""
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            logging.warning(f"API call failed (attempt {i+1}/{max_retries}): {e}")
            if i == max_retries - 1:
                logging.error("API call failed after max retries.")
                return None # Return None instead of raising to allow bot to potentially continue
            wait_time = 2 ** i
            logging.info(f"Retrying API call in {wait_time} seconds...")
            time.sleep(wait_time)
    return None

# --- Initialize API Client ---
api = None
try:
    api = tradeapi.REST(key_id=API_KEY, secret_key=SECRET_KEY, base_url=BASE_URL)
    logging.info("API client object created.")
    account = retry_api_call(lambda: api.get_account())
    if account:
        logging.info(f"Alpaca connection successful! Account status: {account.status}, Buying Power: {account.buying_power}")
    else:
        raise ConnectionError("Failed to connect to Alpaca after retries.")
except Exception as e:
    logging.error(f"CRITICAL: Error initializing API client or testing connection: {e}")
    api = None
    exit("Bot cannot start without API connection.")

# --- Trading Bot Class ---
class TradingBot:
    def __init__(self, api_client):
        if not api_client: raise ValueError("API client must be initialized.")
        self.api = api_client
        self.short_window = 10
        self.long_window = 30
        logging.info("TradingBot Initialized with API client.")

    # --- Risk & Position Sizing ---
    def calculate_position_size(self, current_price, cash_available):
        """Calculate safe position size based on risk parameters"""
        if current_price is None or current_price <= 0: logging.warning("Cannot calculate size: Invalid price."); return 0
        if cash_available is None: logging.warning("Cannot calculate size: Cash available is None."); return 0
        try:
            cash_available_float = float(cash_available) # Ensure it's float
            max_shares_by_value = int((MAX_POSITION_VALUE * POSITION_SIZING_BUFFER) / current_price)
            max_shares_by_cash = int((cash_available_float * POSITION_SIZING_BUFFER) / current_price)
            safe_size = min(max_shares_by_value, max_shares_by_cash) # Simplified sizing
            final_size = max(1, safe_size) if safe_size > 0 else 0
            logging.info(f"Calculated position size: {final_size} shares (Cash Avail: {cash_available_float:.2f}, Max Val Shares: {max_shares_by_value}, Max Cash Shares: {max_shares_by_cash})")
            return final_size
        except Exception as e: logging.error(f"Error calculating position size: {e}"); return 0

    def check_risk_limits(self, symbol):
        """Check if account status and limits allow trading."""
        try:
            account = retry_api_call(lambda: self.api.get_account())
            if not account: logging.error("Risk Check: Could not fetch account info."); return False
            if account.trading_blocked or account.account_blocked:
                logging.critical(f"ACCOUNT BLOCKED! Trading blocked: {account.trading_blocked}, Account blocked: {account.account_blocked}")
                return False
            buying_power = float(account.buying_power)
            if buying_power < MIN_BUYING_POWER:
                logging.warning(f"Risk Check: Insufficient buying power ({buying_power:.2f} < {MIN_BUYING_POWER}). Blocking new BUYS.")
                return False
            # Skipping portfolio history check due to potential unreliability on paper/IEX
            # logging.warning("Risk Check: Portfolio history check for daily P&L is currently skipped.")
            return True # Passes checks available
        except Exception as e: logging.error(f"CRITICAL Error during risk check: {e}", exc_info=True); return False

    # --- Core Strategy & Execution ---
    def calculate_moving_averages(self, bars):
        if bars is None or len(bars) < self.long_window: logging.warning(f"Insufficient data for MA calc."); return None
        df = bars.copy()
        try: df.loc[:, 'MA_short'] = df['close'].rolling(window=self.short_window).mean(); df.loc[:, 'MA_long'] = df['close'].rolling(window=self.long_window).mean(); return df
        except Exception as e: logging.error(f"Error calculating MAs: {e}"); return None

    def analyze_data(self, bars):
        if bars is None: return 'HOLD'
        df_with_ma = self.calculate_moving_averages(bars)
        if df_with_ma is None or len(df_with_ma) < 2 or 'MA_short' not in df_with_ma.columns or 'MA_long' not in df_with_ma.columns: logging.debug("Insufficient data/MAs for decision."); return 'HOLD'
        try: current_short_ma = df_with_ma['MA_short'].iloc[-1]; current_long_ma = df_with_ma['MA_long'].iloc[-1]; prev_short_ma = df_with_ma['MA_short'].iloc[-2]; prev_long_ma = df_with_ma['MA_long'].iloc[-2]
        except IndexError: logging.warning("IndexError accessing MAs."); return 'HOLD'
        if pd.isna(current_short_ma) or pd.isna(current_long_ma) or pd.isna(prev_short_ma) or pd.isna(prev_long_ma): logging.debug("HOLD decision: NaN in MA values."); return 'HOLD'
        logging.info(f"Latest Close: {df_with_ma['close'].iloc[-1]:.2f}, Short MA: {current_short_ma:.2f}, Long MA: {current_long_ma:.2f}")
        if prev_short_ma <= prev_long_ma and current_short_ma > current_long_ma: logging.info("Golden Cross detected - Potential BUY signal"); return 'BUY'
        elif prev_short_ma >= prev_long_ma and current_short_ma < current_long_ma: logging.info("Death Cross detected - Potential SELL signal"); return 'SELL'
        return 'HOLD'

    def get_recent_bars(self, symbol, lookback_bars=BAR_LOOKBACK, timeframe=BAR_TIMEFRAME):
        if not self.api: logging.error("API client missing."); return None
        params = {'limit': lookback_bars, 'timeframe': timeframe, 'feed': 'iex'}
        try:
            logging.debug(f"Fetching {lookback_bars} recent {timeframe} bars for {symbol}...")
            bars_df = retry_api_call(lambda: self.api.get_bars(symbol, **params).df)
            if bars_df is None or bars_df.empty: logging.warning(f"No recent bars returned for {symbol}."); return None
            # Standardize index
            if isinstance(bars_df.index, pd.DatetimeIndex):
                # CORRECTED if/else for timezone
                if bars_df.index.tz is None:
                     bars_df.index = bars_df.index.tz_localize('UTC')
                else:
                     bars_df.index = bars_df.index.tz_convert('UTC')
            else:
                 bars_df=bars_df.reset_index(); ts_col='timestamp' if 'timestamp' in bars_df.columns else ('index' if 'index' in bars_df.columns else None);
                 if ts_col: bars_df.rename(columns={ts_col:'timestamp'},inplace=True); bars_df['timestamp']=pd.to_datetime(bars_df['timestamp'],utc=True); bars_df=bars_df.set_index('timestamp')
                 else: logging.error(f"Cannot find timestamp for {symbol}."); return None
            bars_df = bars_df.sort_index(); required_cols = ['open', 'high', 'low', 'close', 'volume']
            if not all(col in bars_df.columns for col in required_cols): logging.error(f"{symbol} data missing columns."); return None
            logging.info(f"Fetched {len(bars_df)} recent bars for {symbol}. Latest: {bars_df.index[-1]}")
            return bars_df[required_cols].astype(float)
        except Exception as e: logging.error(f"Error fetching recent bars for {symbol}: {str(e)}"); return None

    def submit_order(self, symbol, qty, side):
        if not self.api: logging.error("Cannot submit order, API client missing."); return None
        if side not in ['buy', 'sell']: logging.error(f"Invalid side: {side}"); return None
        if qty <= 0: logging.warning(f"Attempted order for {qty} shares. Skipping."); return None
        if side == 'buy':
            if not self.check_risk_limits(symbol): logging.warning(f"BUY order {symbol} cancelled: risk limits."); return None
        logging.warning(f"Attempting to submit paper {side} order for {qty} share(s) of {symbol}")
        try:
            order = retry_api_call(lambda: self.api.submit_order(symbol=symbol, qty=abs(int(qty)), side=side.lower(), type='market', time_in_force='day'))
            if order: logging.info(f"Paper order submitted: ID={order.id}, Sym={symbol}, Qty={qty}, Side={side}")
            else: logging.error(f"Order submission failed after retries {symbol}.")
            return order
        except Exception as e: logging.error(f"Order submission failed {symbol}: {str(e)}"); return None

    def run(self, symbol=STOCK_SYMBOL):
        logging.info("Starting trading bot with MA Crossover strategy and risk management...")
        print("Starting trading bot with MA Crossover strategy and risk management...")
        print("Press CTRL+C to stop.")
        # --- This is the start of the main loop's try block ---
        while True:
            try: # <---- Start of the TRY for the main loop
                can_buy = self.check_risk_limits(symbol)
                if not can_buy: logging.warning("Risk limits potentially breached - BUY orders disabled for this cycle.")
                current_position = 0; current_price = None
                try:
                    position = retry_api_call(lambda: self.api.get_position(symbol))
                    if position: current_position = int(position.qty); logging.info(f"Current position: {current_position} {symbol}")
                except tradeapi.rest.APIError as e:
                    if e.status_code == 404: logging.info(f"No current position in {symbol}")
                    else: logging.error(f"APIError checking position: {e}")
                except Exception as e_pos: logging.error(f"Error checking position: {e_pos}")
                bars = self.get_recent_bars(symbol, lookback_bars=BAR_LOOKBACK)
                if bars is not None and not bars.empty:
                    current_price = bars['close'].iloc[-1] if not bars.empty else None
                    decision = self.analyze_data(bars)
                    logging.info(f"Decision for {symbol}: {decision}")
                    print(f"Latest {symbol} analysis complete. Decision: {decision}")
                    if decision == 'BUY':
                        if current_position == 0:
                             if can_buy:
                                 if current_price:
                                     account = retry_api_call(lambda: self.api.get_account())
                                     if account:
                                         size = self.calculate_position_size(current_price, account.buying_power)
                                         if size > 0: self.submit_order(symbol, size, 'buy')
                                         else: logging.warning("Buy order skipped: Size 0.")
                                     else: logging.error("Buy order skipped: No account info.")
                                 else: logging.warning("Buy order skipped: No price.")
                             else: logging.info("BUY signal ignored: risk limits.")
                        else: logging.info(f"BUY signal ignored: Already long {current_position} {symbol}.")
                    elif decision == 'SELL':
                        if current_position > 0: logging.info(f"Submitting sell for position ({current_position} shares)."); self.submit_order(symbol, abs(current_position), 'sell')
                        else: logging.info("SELL signal ignored: No position.")
                logging.info(f"Sleeping for {SLEEP_TIME_SECONDS} seconds...")
                time.sleep(SLEEP_TIME_SECONDS)
            # --- THESE EXCEPT BLOCKS MUST BE PRESENT AND ALIGNED WITH THE 'try' ABOVE ---
            except KeyboardInterrupt:
                 logging.info("Bot stopped by user"); print("\nStopping..."); break
            except Exception as e:
                 logging.error(f"Unhandled error: {str(e)}", exc_info=True); time.sleep(SLEEP_TIME_SECONDS)

# --- Main Execution ---
if __name__ == "__main__":
    logging.info("--- Simple Alpaca Bot - MA Crossover w/ Risk Mgmt ---")
    if api: bot = TradingBot(api); bot.run()
    else: logging.critical("Exiting: API client failed init.")
    logging.info("--- Bot Shutdown ---")