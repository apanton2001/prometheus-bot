# tariff_analysis.py - Reverted to Alpaca Fetch

import pandas as pd
import os
from datetime import datetime, timedelta
import warnings
import alpaca_trade_api as tradeapi # Using Alpaca
from dotenv import load_dotenv

# Ignore specific FutureWarning from pandas
warnings.simplefilter(action='ignore', category=FutureWarning)

# --- Configuration ---
TARIFF_CSV_PATH = 'Tarriff Data.csv' # Using root path
MARKET_SYMBOLS_ALPACA = ['SPY'] # Analyze S&P 500 only
# VOLATILITY_SYMBOL_ALPACA = None # Keep VIX/Vol analysis commented out

ANALYSIS_WINDOW_DAYS = 25 # Days after announcement to fetch data
POST_ANNOUNCEMENT_DAYS = [1, 3, 5, 10] # Trading days after announcement
PLOT_CHARTS = False # Disable plotting by default

# --- Load Environment Variables for Alpaca ---
load_dotenv()
ALPACA_KEY = os.getenv('ALPACA_KEY')
ALPACA_SECRET = os.getenv('ALPACA_SECRET')
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets'

# Global Alpaca client
alpaca_client = None

# --- API Initialization ---
def initialize_apis():
    """Initializes the Alpaca API client."""
    global alpaca_client
    if not ALPACA_KEY or not ALPACA_SECRET: print("ERROR: Alpaca API keys missing."); return False
    try:
        alpaca_client = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_BASE_URL, api_version='v2')
        account = alpaca_client.get_account(); print(f"Successfully initialized Alpaca client. Account status: {account.status}"); return True
    except Exception as e: print(f"ERROR: Failed to initialize Alpaca client: {e}"); return False

# --- Alpaca Data Fetch --- # Version using string slicing fix & IEX feed
def fetch_alpaca_data_for_analysis(symbol, start_dt_orig, end_dt_orig, timeframe='1D', feed='iex'):
    """Fetches daily data from Alpaca, ensuring timezone consistency and using string slicing."""
    if not alpaca_client: print(f"  ERROR: Alpaca client not ready for {symbol}."); return pd.DataFrame()
    try: start_dt = pd.to_datetime(start_dt_orig); end_dt = pd.to_datetime(end_dt_orig)
    except Exception as e: print(f"  ERROR: Could not process dates {start_dt_orig}, {end_dt_orig}: {e}"); return pd.DataFrame()
    if timeframe == '1D': start_iso_api = start_dt.strftime('%Y-%m-%d'); end_iso_api = end_dt.strftime('%Y-%m-%d')
    else: start_iso_api = start_dt.isoformat(); end_iso_api = end_dt.isoformat()
    today_api_str = datetime.today().strftime('%Y-%m-%d')
    if end_iso_api > today_api_str: end_iso_api = today_api_str
    if start_iso_api >= end_iso_api: return pd.DataFrame()
    params = {'start': start_iso_api, 'end': end_iso_api, 'feed': feed, 'timeframe': timeframe}
    try:
        print(f"  Fetching {symbol} data from {start_iso_api} to {end_iso_api} via Alpaca ({feed})...")
        bars = alpaca_client.get_bars(symbol, **params).df
        if bars.empty: print(f"  WARNING: No data returned by Alpaca for {symbol}."); return bars
        # Standardize index to UTC
        if isinstance(bars.index, pd.DatetimeIndex):
             if bars.index.tz is None: bars.index = bars.index.tz_localize('UTC')
             else: bars.index = bars.index.tz_convert('UTC')
        else: # Try reset index
             bars = bars.reset_index(); ts_col = 'timestamp' if 'timestamp' in bars.columns else ('index' if 'index' in bars.columns else None)
             if ts_col: bars.rename(columns={ts_col: 'timestamp'}, inplace=True); bars['timestamp'] = pd.to_datetime(bars['timestamp'], utc=True); bars = bars.set_index('timestamp')
             else: print(f"  ERROR: Cannot find timestamp for {symbol}."); return pd.DataFrame()
        # Filter using simple DATE STRINGS for slicing
        bars = bars.sort_index(); start_date_str_filter = start_dt_orig.strftime('%Y-%m-%d'); end_date_str_filter = end_dt_orig.strftime('%Y-%m-%d')
        bars_filtered = bars.loc[start_date_str_filter:end_date_str_filter]
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in bars.columns for col in required_cols): print(f"  ERROR: Data for {symbol} missing columns."); return pd.DataFrame()
        print(f"  Successfully fetched data, {len(bars_filtered)} rows within target period.")
        if bars_filtered.empty: print(f"  WARNING: No data remained after filtering {symbol}."); return pd.DataFrame()
        return bars_filtered[required_cols].astype(float)
    except Exception as e: print(f"  ERROR: Failed fetching/processing Alpaca data for {symbol}: {e}"); return pd.DataFrame()

# --- Helper Functions ---
def calculate_post_announcement_metrics(df_data, announcement_date, days_list):
    metrics = {}; price_col = 'close'
    if df_data.empty or price_col not in df_data.columns: return {f'Return_{d}d': None for d in days_list}
    announcement_date_aware = announcement_date.tz_localize('UTC') if announcement_date.tzinfo is None else announcement_date.tz_convert('UTC')
    announcement_date_aware = announcement_date_aware.normalize()
    try:
        valid_index = df_data.index[df_data.index >= announcement_date_aware];
        if valid_index.empty: raise ValueError("Date not found")
        actual_announce_ts = valid_index.min(); announcement_idx_loc = df_data.index.get_loc(actual_announce_ts)
    except Exception as e: print(f"  WARNING: Could not find index for ann. date {announcement_date.date()}: {e}"); return {f'Return_{d}d': None for d in days_list}
    for days in days_list:
        end_idx_loc = announcement_idx_loc + days
        if end_idx_loc < len(df_data):
            start_price = df_data[price_col].iloc[announcement_idx_loc]; end_price = df_data[price_col].iloc[end_idx_loc]
            if pd.notna(start_price) and pd.notna(end_price) and start_price != 0: metrics[f'Return_{days}d'] = ((end_price / start_price) - 1) * 100
            else: metrics[f'Return_{days}d'] = None
        else: metrics[f'Return_{days}d'] = None
    return metrics

# --- Main Analysis Logic ---
print("--- Tariff Announcement Reaction Analysis (Using Alpaca) ---")
if not initialize_apis(): print("Exiting."); exit()
print(f"\nAttempting to load data from: {TARIFF_CSV_PATH}")
try:
    df_tariffs = pd.read_csv(TARIFF_CSV_PATH, encoding='utf-8'); df_tariffs.columns = df_tariffs.columns.str.strip()
    print(f"Successfully loaded tariff data.")
    if 'announcement_date' not in df_tariffs.columns: print("\nERROR: 'announcement_date' column missing."); exit()
except Exception as e: print(f"\nERROR: Failed loading CSV: {e}"); exit()
print("\n--- Processing Tariff Announcement Dates ---")
announcement_events = [] # Initialize the list HERE
for index, row in df_tariffs.iterrows():
    try:
        # Indent the code inside the try block
        event_name = str(row['event_name']).strip()
        announce_date = pd.to_datetime(row['announcement_date'], errors='coerce')
        # This check is now correctly indented inside the try
        if not pd.isna(announce_date):
            announcement_events.append({
                'event_name': event_name,
                'announcement_date': announce_date.normalize() # Normalize here
            })
    except Exception as e:
        # This except block now correctly follows the try block
        print(f"ERROR processing row {index}: {e}")
        # Continue to next row on error
if not announcement_events: print("\nERROR: No valid announcement dates. Exiting."); exit()
print(f"\nFound {len(announcement_events)} events with announcement dates to analyze.")
print(f"\n--- Fetching & Analyzing {MARKET_SYMBOLS_ALPACA} Data Around Announcements via Alpaca ---")
results = []
symbols_to_analyze = MARKET_SYMBOLS_ALPACA
for event in announcement_events:
    event_name = event['event_name']; announce_date = event['announcement_date']
    print(f"\n--- Analyzing Event Announced: {event_name} ({announce_date.strftime('%Y-%m-%d')}) ---")
    fetch_start = announce_date - timedelta(days=5); fetch_end = announce_date + timedelta(days=ANALYSIS_WINDOW_DAYS + 5)
    event_data = {}; fetch_successful = True
    for symbol in symbols_to_analyze:
        df_symbol = fetch_alpaca_data_for_analysis(symbol, fetch_start, fetch_end, timeframe='1D')
        if df_symbol is None or df_symbol.empty: fetch_successful = False
        else: event_data[symbol] = df_symbol
    if not fetch_successful or 'SPY' not in event_data or event_data['SPY'].empty:
        print(f"  Skipping metric calculation for '{event_name}' due to missing SPY data.")
        continue
    spy_data = event_data['SPY']
    spy_metrics = calculate_post_announcement_metrics(spy_data, announce_date, POST_ANNOUNCEMENT_DAYS)
    event_results = {'Event': event_name, 'Announcement Date': announce_date.date()}
    event_results.update(spy_metrics)
    results.append(event_results)
    print(f"  Post-Announcement Results:")
    for days in POST_ANNOUNCEMENT_DAYS:
        ret_key = f'Return_{days}d'; ret_val = event_results.get(ret_key)
        ret_str = f"{ret_val:.2f}%" if ret_val is not None else "N/A"
        print(f"    {days}-Day: SPY Return={ret_str}")
print("\n--- Announcement Reaction Summary ---")
if results:
    summary_df = pd.DataFrame(results); col_order = ['Event', 'Announcement Date']
    for days in POST_ANNOUNCEMENT_DAYS: col_order.append(f'Return_{days}d')
    col_order = [col for col in col_order if col in summary_df.columns]; summary_df = summary_df[col_order]
    pd.options.display.float_format = '{:,.2f}'.format; print(summary_df.to_string(index=False))
else: print("No results generated from the analysis.")
print("\nAnalysis complete.")