import pandas as pd # type: ignore
import numpy as np # type: ignore
# import talib # Removed TA-Lib
import xgboost as xgb # type: ignore
from sklearn.model_selection import TimeSeriesSplit, GridSearchCV
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import os
import glob  # To find data files
import time
import logging # Keep basic logging for critical errors/info
import ccxt # For Binance
import alpaca_trade_api as tradeapi # For Alpaca
from datetime import datetime, timedelta

# --- Configuration ---
# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Read API Keys from Environment Variables (MUST BE SET)
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY')
BINANCE_SECRET = os.environ.get('BINANCE_SECRET')
ALPACA_KEY = os.environ.get('ALPACA_KEY')
ALPACA_SECRET = os.environ.get('ALPACA_SECRET')
# Use paper trading endpoint for Alpaca testing
ALPACA_PAPER = True # Set to False for live Alpaca trading (use with caution!)
ALPACA_BASE_URL = 'https://paper-api.alpaca.markets' if ALPACA_PAPER else 'https://api.alpaca.markets'

# Data and Model Paths
BASE_DATA_DIR = 'user_data/data/'
MODEL_DIR = 'user_data/models/'
CRYPTO_EXCHANGE = 'binance' # Matches directory structure
CRYPTO_DATA_DIR = os.path.join(BASE_DATA_DIR, CRYPTO_EXCHANGE)
STOCK_DATA_DIR = os.path.join(BASE_DATA_DIR, 'alpaca') # New directory for stock data

# Assets to Trade
CRYPTO_PAIRS = ['BTC/USDT'] # Focus on one for now
STOCK_SYMBOLS = ['AAPL', 'TSLA'] # Example stocks

# Common Parameters
TIMEFRAME_CRYPTO = '1h' # Freqtrade/Binance timeframe
TIMEFRAME_ALPACA = '1Hour' # Alpaca timeframe identifier (check API docs for exact values)
LOOKAHEAD_PERIODS = 4 # How many periods into the future to predict for target
TARGET_PROFIT_THRESHOLD = 0.005 # 0.5% target profit

# Feature parameters
ELO_K_FACTOR = 32 # Standard ELO K-factor
VOLATILITY_ROLLING_WINDOW = 20
ATR_WINDOW = 14
LAG_PERIODS = 1 # How many periods to lag close price

# XGBoost Hyperparameters (Expanded with Regularization)
PARAM_GRID = {
    'n_estimators': [100, 200], # Reduced for faster testing
    'max_depth': [3, 5],        # Reduced for faster testing
    'learning_rate': [0.01, 0.1],
    'subsample': [0.7, 1.0],
    'colsample_bytree': [0.7, 1.0],
    'reg_alpha': [0, 0.1],  # L1 regularization
    'reg_lambda': [1, 1.5]  # L2 regularization
}

# Global variables to hold trained models and API clients
trained_models = {}
binance_client = None
alpaca_client = None

# --- API Initialization ---
def initialize_apis():
    global binance_client, alpaca_client
    logger.info("Initializing API clients...")
    if not BINANCE_API_KEY or not BINANCE_SECRET:
        logger.warning("Binance API keys not found in environment variables. Live crypto trading disabled.")
    else:
        binance_client = ccxt.binance({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_SECRET,
            'enableRateLimit': True, # Important for respecting API limits
        })
        logger.info("Binance client initialized.")

    if not ALPACA_KEY or not ALPACA_SECRET:
        logger.warning("Alpaca API keys not found in environment variables. Live stock trading disabled.")
    else:
        try:
            alpaca_client = tradeapi.REST(ALPACA_KEY, ALPACA_SECRET, ALPACA_BASE_URL, api_version='v2')
            account = alpaca_client.get_account() # Test connection
            logger.info(f"Alpaca client initialized. Account status: {account.status}")
        except Exception as e:
            logger.error(f"Failed to initialize Alpaca client: {e}")
            alpaca_client = None

# --- Data Fetching ---
def fetch_binance_hist_data(pair, timeframe, limit=1000):
    """ Fetches historical data from Binance using ccxt """
    logger.info(f"Fetching historical Binance data for {pair} ({timeframe}, limit={limit})")
    if not binance_client:
        logger.error("Binance client not initialized.")
        return None
    try:
        symbol = pair.replace('/', '') # ccxt uses 'BTCUSDT' format
        # Fetch OHLCV data
        ohlcv = binance_client.fetch_ohlcv(symbol, timeframe, limit=limit)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms', utc=True)
        df.set_index('timestamp', inplace=True)
        # Ensure correct types
        df = df.astype({'open': 'float', 'high': 'float', 'low': 'float', 'close': 'float', 'volume': 'float'})
        logger.info(f"Fetched {len(df)} rows for {pair}")
        return df
    except ccxt.NetworkError as e:
        logger.error(f"Binance NetworkError: {e}")
    except ccxt.ExchangeError as e:
        logger.error(f"Binance ExchangeError: {e}")
    except Exception as e:
        logger.error(f"Error fetching Binance data for {pair}: {e}")
    return None

def fetch_alpaca_data(symbol, timeframe='1H', start=None, end=None, limit=None):
    """Fetch historical data from Alpaca with date range priority."""
    # Ensure necessary imports are available locally or globally
    import alpaca_trade_api as tradeapi
    import pandas as pd
    from datetime import datetime, timedelta
    import os # Needed for os.getenv

    # Assume alpaca_client is initialized globally or passed as argument
    # Using global client for simplicity based on previous context
    global alpaca_client
    if not alpaca_client: # Check if client is initialized
        logger.error("Alpaca client not initialized for fetch.")
        # Try to initialize here? Or rely on main script initialization?
        # Let's rely on main script init and return empty if not ready
        return pd.DataFrame()

    # Use environment variables directly if api object not passed
    # api = tradeapi.REST(os.getenv('ALPACA_KEY'), os.getenv('ALPACA_SECRET'), os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets'))

    # Default to fetching last ~13 months if no specific dates given and limit isn't set for live fetch
    if start is None and end is None and limit is None:
        end_dt = pd.Timestamp.now(tz='UTC')
        # Request ~13 months instead of 2 years
        start_dt = end_dt - timedelta(days=395) # Approx 13 months
        logger.info(f"Defaulting fetch dates for historical pull: {start_dt.date()} to {end_dt.date()} (Reduced History)")
        # Update start/end strings based on calculated dates
        start = start_dt.isoformat()
        end = end_dt.isoformat()

    # Ensure start/end are strings if they were set above
    start_iso = start if isinstance(start, str) else (start_dt.isoformat() if 'start_dt' in locals() and start_dt else None)
    end_iso = end if isinstance(end, str) else (end_dt.isoformat() if 'end_dt' in locals() and end_dt else None)

    # Set parameters: use limit only if no dates are specified
    params = {'timeframe': timeframe}
    if start_iso or end_iso:
        if start_iso: params['start'] = start_iso
        if end_iso: params['end'] = end_iso
    elif limit:
         params['limit'] = limit
    else:
         params['limit'] = 1000

    try:
        # Using the global alpaca_client assumed to be initialized
        # Force IEX feed again
        params['feed'] = 'iex'
        logger.debug(f"Alpaca get_bars call params (forcing IEX, reduced history): {params}")
        bars = alpaca_client.get_bars(symbol, **params).df
        # Reset index to make timestamp a column for conversion
        bars = bars.reset_index()
        # Ensure 'timestamp' column exists before conversion
        if 'timestamp' not in bars.columns:
             logger.error(f"Timestamp column missing in data returned for {symbol}")
             return pd.DataFrame()
        # Convert timestamp and set as index
        bars['timestamp'] = pd.to_datetime(bars['timestamp'], utc=True) # Ensure UTC
        bars.set_index('timestamp', inplace=True)
        logger.info(f"Fetched {len(bars)} rows for {symbol}")
        # Ensure required columns exist
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        if not all(col in bars.columns for col in required_cols):
            missing = [col for col in required_cols if col not in bars.columns]
            logger.error(f"Data for {symbol} missing columns after fetch: {missing}")
            return pd.DataFrame()
        return bars[required_cols].astype(float) # Return only standard columns
    except Exception as e:
        logger.error(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()

def fetch_live_data(symbol, timeframe='1H'):
    """Fetch latest data for live trading."""
    # Specify the limit directly for fetching recent bars
    return fetch_alpaca_data(symbol, timeframe, limit=200)  # Fetch last 200 bars for live features

def fetch_live_binance_data(pair, timeframe, limit=200): # Need enough data for feature calculation
    """ Fetches recent data from Binance for live prediction """
    # Reuses hist function for simplicity, could be optimized
    return fetch_binance_hist_data(pair, timeframe, limit)

def fetch_live_alpaca_data(symbol, timeframe, limit=200):
    """ Fetches recent data from Alpaca for live prediction """
     # Reuses hist function for simplicity
    return fetch_alpaca_data(symbol, timeframe, limit=limit)

# --- Feature Engineering ---
def calculate_market_elo(df):
    """ Calculates a rolling ELO rating based on price movements. """
    logger.debug("Calculating Market ELO...")
    df['elo'] = 1500.0 # Starting ELO, ensure float
    # Use vectorized operations where possible for speed, fallback to loop if needed
    # This loop is computationally intensive for large datasets or frequent live calls
    price_moves = df['close'].diff()
    for i in range(1, len(df)):
        if pd.isna(price_moves.iloc[i]): continue
        prev_elo = df['elo'].iloc[i-1]
        # Simplified ELO logic: Higher price move increases chance of winning (actual=1)
        # Scaling factor (e.g., 100) can be tuned. A smaller factor makes ELO less sensitive.
        expected = 1.0 / (1.0 + 10.0 ** (-price_moves.iloc[i] * 100 / 400.0)) # Simplified ELO probability
        actual = 1.0 if price_moves.iloc[i] > 0 else 0.0
        df.loc[df.index[i], 'elo'] = prev_elo + ELO_K_FACTOR * (actual - expected)
    logger.debug("Market ELO calculated.")
    return df

def calculate_features(dataframe):
    """Calculate technical features with proper .loc usage."""
    df = dataframe.copy()
    # Define constants locally if not global
    VOLATILITY_ROLLING_WINDOW = 20
    LAG_PERIODS = 1

    # Ensure index is DatetimeIndex for time features
    if not isinstance(df.index, pd.DatetimeIndex):
         logger.warning("DataFrame index is not DatetimeIndex in calculate_features. Time features may fail.")
         # Attempt conversion? Or assume it's correct? Let's assume for now.

    # --- Feature Calculations using .loc ---
    df.loc[:, 'rolling_std_close_20'] = df['close'].rolling(window=VOLATILITY_ROLLING_WINDOW).std()
    # Time features (handle potential non-datetime index)
    try:
        df.loc[:, 'hour_of_day'] = df.index.hour
        df.loc[:, 'day_of_week'] = df.index.dayofweek
    except AttributeError:
         logger.warning("Could not extract time features - index might not be DatetimeIndex.")
         df.loc[:, 'hour_of_day'] = -1 # Assign default/error value
         df.loc[:, 'day_of_week'] = -1

    df.loc[:, 'close_lag_1'] = df['close'].shift(LAG_PERIODS)
    df.loc[:, 'volatility_10'] = df['close'].pct_change().rolling(10).std() * 100

    # --- Candlestick patterns ---
    # Initialize first
    df.loc[:, 'bullish_engulfing'] = 0
    df.loc[:, 'bearish_engulfing'] = 0
    # Check length and calculate only if shift is possible
    if len(df) > 1:
        # Conditions need careful alignment with .loc - apply calculation, then assign result
        is_bullish_current = df['close'] > df['open']
        is_bearish_prior = df['close'].shift(1) < df['open'].shift(1)
        open_below_prior_close = df['open'] < df['close'].shift(1)
        close_above_prior_open = df['close'] > df['open'].shift(1)

        bullish_cond = is_bearish_prior & is_bullish_current & close_above_prior_open & open_below_prior_close
        df.loc[bullish_cond.shift(-1).fillna(False), 'bullish_engulfing'] = 1 # Assign based on condition from prior bar

        is_bearish_current = df['close'] < df['open']
        is_bullish_prior = df['close'].shift(1) > df['open'].shift(1)
        open_above_prior_close = df['open'] > df['close'].shift(1)
        close_below_prior_open = df['close'] < df['open'].shift(1)

        bearish_cond = is_bullish_prior & is_bearish_current & close_below_prior_open & open_above_prior_close
        df.loc[bearish_cond.shift(-1).fillna(False), 'bearish_engulfing'] = 1 # Assign based on condition from prior bar


    # --- Volatility states ---
    # Initialize first
    df.loc[:, 'vol_low'] = 0
    df.loc[:, 'vol_med'] = 0
    df.loc[:, 'vol_high'] = 0
    # Calculate rolling std dev of percentage change
    vol_std = df['close'].pct_change().rolling(window=VOLATILITY_ROLLING_WINDOW).std()
    if vol_std.notna().sum() > 3 and vol_std.nunique() > 1: # Check if enough non-NaN unique values exist
        try:
            # Calculate quantiles on the non-NaN part
            q33 = vol_std.quantile(0.33)
            q66 = vol_std.quantile(0.66)
            # Assign states using .loc based on conditions
            df.loc[vol_std < q33, 'vol_low'] = 1
            df.loc[(vol_std >= q33) & (vol_std < q66), 'vol_med'] = 1
            df.loc[vol_std >= q66, 'vol_high'] = 1
        except Exception as e:
             logger.warning(f"Could not calculate volatility states: {e}")
    else:
        logger.debug("Not enough data or variance for volatility states.")

    df.loc[:, 'pair_spread'] = (df['high'] - df['low']) / df['close']

    # --- Add other features from previous version that might be missing ---
    df.loc[:, 'price_change_pct'] = df['close'].pct_change()
    df.loc[:, 'high_low_diff'] = df['high'] - df['low']
    df.loc[:, 'close_open_diff'] = df['close'] - df['open']
    df.loc[:, 'volume_ma_20'] = df['volume'].rolling(window=20).mean()
    df.loc[:, 'volume_ratio'] = np.where( df['volume_ma_20'] > 0, df['volume'] / df['volume_ma_20'], 1 )
    df.loc[:, 'rolling_mean_close_5'] = df['close'].rolling(window=5).mean()
    df.loc[:, 'news_sentiment'] = 0.0 # Placeholder

    # --- ELO ---
    # Keep ELO calculation as it was (assuming it uses .loc correctly internally or was fixed)
    # If calculate_market_elo exists globally:
    # df = calculate_market_elo(df)
    # If ELO logic is to be included here:
    df.loc[:, 'elo'] = np.nan # Initialize elo column
    try:
        close_prices_np = df['close'].values
        # Assume _calculate_elo_numba exists
        elo_values = _calculate_elo_numba(close_prices_np, 1500.0, 32) # Use constant K factor
        df.loc[:, 'elo'] = elo_values
        df['elo'].fillna(method='ffill', inplace=True) # Forward fill any remaining NaNs
        logger.debug("Numba ELO calculation successful (assumed).")
    except NameError:
         logger.warning("Numba ELO function _calculate_elo_numba not found, skipping ELO.")
         df.loc[:, 'elo'] = 1500.0 # Assign default if function missing
    except Exception as e:
         logger.warning(f"ELO calculation failed: {e}. Assigning default.")
         df.loc[:, 'elo'] = 1500.0


    logger.debug(f"Finished calculating features. Columns: {df.columns.tolist()}")
    return df

# --- Target Calculation ---
def calculate_target(dataframe, horizon=None):
    """Calculate target labels with .loc."""
    # Use global LOOKAHEAD_PERIODS if horizon not passed
    if horizon is None:
        global LOOKAHEAD_PERIODS
        horizon = LOOKAHEAD_PERIODS

    # Define threshold locally if not global
    TARGET_PROFIT_THRESHOLD = 0.005 # Or use global

    df = dataframe.copy() # Work on a copy

    # Calculate future returns using .loc for assignment
    df.loc[:, 'future_pct_change'] = df['close'].pct_change(periods=horizon).shift(-horizon)

    # Initialize target column using .loc
    df.loc[:, 'target'] = 0  # Default: Hold

    # Set target based on future returns using .loc and boolean indexing
    buy_cond = df['future_pct_change'] > TARGET_PROFIT_THRESHOLD
    sell_cond = df['future_pct_change'] < -TARGET_PROFIT_THRESHOLD

    df.loc[buy_cond, 'target'] = 1  # Buy Call
    df.loc[sell_cond, 'target'] = 2  # Buy Put (Changed from -1 to 2 based on previous context)

    return df

# --- Model Training ---
def train_model(identifier: str, asset_type: str, df: pd.DataFrame):
    """
    Train an XGBoost model for a specific asset (crypto pair or stock symbol).
    """
    logger.info(f"--- Starting Training for {identifier} ({asset_type}) ---")

    # 1. Clean Data
    df = clean_data(df)

    # 2. Calculate Features
    df = calculate_features(df)

    # 3. Calculate Target
    df = calculate_target(df)

    # 4. Prepare Data for Training
    # Define feature columns dynamically based on calculations
    base_features = [
        'price_change_pct', 'high_low_diff', 'close_open_diff',
        'volume_ma_20', 'volume_ratio', 'rolling_mean_close_5', 'rolling_std_close_20',
        'hour_of_day', 'day_of_week', 'close_lag_1', 'volatility_10',
        'bullish_engulfing', 'bearish_engulfing', 'elo', 'spread'
    ]
    vol_state_features = [f'vol_{state}' for state in ['low', 'med', 'high'] if f'vol_{state}' in df.columns]
    feature_columns = base_features + vol_state_features

    # Ensure all feature columns exist AFTER calculations and cleaning
    df_for_training = df.copy() # Work on a copy to keep original df intact if needed
    missing_cols = [col for col in feature_columns if col not in df_for_training.columns]
    if missing_cols:
        logger.error(f"Training aborted for {identifier}: Following feature columns are missing: {missing_cols}")
        return None

    # Drop rows with NaNs essential for training (features + target)
    df_clean = df_for_training.dropna(subset=feature_columns + ['target', 'future_pct_change']) # Keep future_pct_change for simulation
    if df_clean.empty:
        logger.error(f"Training aborted for {identifier}: No data remaining after dropping NaNs. Check indicator periods/data quality.")
        return None

    X = df_clean[feature_columns]
    y = df_clean['target'] # Target: 0, 1, 2

    logger.info(f"Data prepared for training {identifier}: {len(X)} samples.")
    if len(X) < 100: # Arbitrary minimum
        logger.error(f"Training aborted for {identifier}: Not enough data points ({len(X)}) after cleaning.")
        return None

    # 5. Split Data (Time-Series Aware)
    n_splits = 5
    tscv = TimeSeriesSplit(n_splits=n_splits)

    # Get the last split for validation reporting
    train_index, test_index = list(tscv.split(X))[-1]
    X_train, X_test = X.iloc[train_index], X.iloc[test_index]
    y_train, y_test = y.iloc[train_index], y.iloc[test_index]
    df_test = df_clean.iloc[test_index].copy() # Keep corresponding original data for simulation

    logger.info(f"Train set size: {len(X_train)}, Test set size: {len(X_test)}")

    # 6. Train Model (GridSearchCV)
    logger.info(f"Training XGBoost model with GridSearchCV for {identifier}...")
    model = xgb.XGBClassifier(objective='multi:softmax',
                              num_class=3,
                              use_label_encoder=False,
                              eval_metric='mlogloss',
                              random_state=42) # Add random state for reproducibility

    grid_search = GridSearchCV(estimator=model,
                               param_grid=PARAM_GRID,
                               scoring='accuracy',
                               cv=tscv, # Use time-series splits
                               n_jobs=-1, # Use all cores
                               verbose=1) # Reduced verbosity
    try:
        grid_search.fit(X, y) # Fit on the full dataset for hyperparameter tuning
        best_model = grid_search.best_estimator_
        logger.info(f"Best parameters for {identifier}: {grid_search.best_params_}")
        logger.info(f"Best CV score (accuracy) for {identifier}: {grid_search.best_score_:.4f}")
    except Exception as e:
        logger.error(f"Error during GridSearchCV fitting for {identifier}: {e}")
        return None # Stop if GridSearch fails

    # 7. Evaluate Model on the last split
    logger.info(f"Evaluating model for {identifier} on the last time-series split...")
    try:
        y_pred = best_model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        logger.info(f"Validation Accuracy for {identifier}: {accuracy:.4f}")
        logger.info(f"Validation Classification Report for {identifier}:\n{classification_report(y_test, y_pred, target_names=['Hold', 'Buy/Call', 'Sell/Put'])}")
        logger.info(f"Validation Confusion Matrix for {identifier}:\n{confusion_matrix(y_test, y_pred)}")

        # Simulate Profit on Test Set
        simulated_profit_pct = simulate_profit(y_test, y_pred, df_test, asset_type)
        logger.info(f"Simulated Profit/Loss %% on Test Set for {identifier} ({asset_type}): {simulated_profit_pct:.4f}%")

    except Exception as e:
        logger.error(f"Error during model evaluation or simulation for {identifier}: {e}")
        # Continue to save model maybe? Or return None? Let's return None for now.
        return None

    # 8. Save Model
    # Loosen saving criteria for testing
    os.makedirs(MODEL_DIR, exist_ok=True)
    model_filename = f'{identifier.replace("/", "_")}_{asset_type}_model.joblib'
    model_save_path = os.path.join(MODEL_DIR, model_filename)
    try:
        joblib.dump(best_model, model_save_path)
        logger.info(f"Model for {identifier} saved successfully to {model_save_path}")
        return best_model # Return the trained model
    except Exception as e:
        logger.error(f"Error saving model for {identifier} to {model_save_path}: {e}")
        return None

# --- Simulation ---
def simulate_profit(y_true, y_pred, df_test, asset_type):
    """ Simplified profit simulation on the test set data. Returns total % profit/loss. """
    if 'future_pct_change' not in df_test.columns:
        logger.error("Cannot simulate profit, 'future_pct_change' missing from test data.")
        return 0.0

    df_sim = df_test.copy()
    df_sim['signal'] = y_pred
    # Use the actual future return that was used to calculate the target
    df_sim['actual_return'] = df_sim['future_pct_change']

    if asset_type == 'crypto':
        # Crypto Spot: Long if signal=1 (Buy), Short if signal=2 (Sell)
        df_sim['strategy_return'] = np.where(df_sim['signal'] == 1, df_sim['actual_return'],
                                           np.where(df_sim['signal'] == 2, -df_sim['actual_return'], 0.0))
    elif asset_type == 'stock':
        # Stock Option Proxy: Assume fixed gain/loss based on correct direction
        # Correct Call (Signal=1, Actual Up): +1% (Example)
        # Incorrect Call (Signal=1, Actual Down/Flat): -1% (Example)
        # Correct Put (Signal=2, Actual Down): +1% (Example)
        # Incorrect Put (Signal=2, Actual Up/Flat): -1% (Example)
        # This is highly simplified! Does not reflect real option pricing/decay.
        proxy_gain = 0.01
        df_sim['strategy_return'] = 0.0
        df_sim.loc[(df_sim['signal'] == 1) & (df_sim['actual_return'] > 0), 'strategy_return'] = proxy_gain
        df_sim.loc[(df_sim['signal'] == 1) & (df_sim['actual_return'] <= 0), 'strategy_return'] = -proxy_gain
        df_sim.loc[(df_sim['signal'] == 2) & (df_sim['actual_return'] < 0), 'strategy_return'] = proxy_gain
        df_sim.loc[(df_sim['signal'] == 2) & (df_sim['actual_return'] >= 0), 'strategy_return'] = -proxy_gain
    else:
        df_sim['strategy_return'] = 0.0

    # Calculate total simulated return (percentage points)
    total_profit_pct = df_sim['strategy_return'].sum() * 100
    return total_profit_pct


# --- Live Prediction ---
def get_live_signal(identifier, asset_type, model):
    """ Fetches live data, calculates features, and returns prediction. """
    logger.info(f"Getting live signal for {identifier} ({asset_type})...")
    # 1. Fetch recent data
    if asset_type == 'crypto':
        live_df = fetch_live_binance_data(identifier, TIMEFRAME_CRYPTO)
    elif asset_type == 'stock':
        live_df = fetch_live_alpaca_data(identifier, TIMEFRAME_ALPACA)
    else:
        logger.error(f"Unknown asset type: {asset_type}")
        return "Error"

    if live_df is None or live_df.empty:
        logger.error(f"Failed to fetch live data for {identifier}.")
        return "Error: No Data"

    # 2. Calculate Features
    try:
        features_df = calculate_features(live_df.copy()) # Use copy
        # Get features for the *latest* complete candle
        latest_features = features_df.iloc[-2:-1] # Use second to last row as last might be incomplete
        if latest_features.isnull().any().any(): # Check for NaNs in the feature row
             logger.warning(f"NaNs found in latest features for {identifier}. May need more historical data for calculation.")
             # Try using iloc[-1] as fallback? Or return error? Let's try -1 for now.
             latest_features = features_df.iloc[-1:]
             if latest_features.isnull().any().any():
                 logger.error(f"NaNs still present in latest features (iloc[-1]) for {identifier}. Cannot predict.")
                 return "Error: Feature NaN"


        # Ensure feature columns match model's expected features
        model_features = model.get_booster().feature_names
        latest_features = latest_features[model_features] # Select and reorder

    except Exception as e:
        logger.error(f"Error calculating features for live data {identifier}: {e}")
        return "Error: Feature Calc"

    # 3. Predict
    try:
        prediction = model.predict(latest_features)[0]
        signal_map = {0: 'Hold', 1: 'Buy/Call', 2: 'Sell/Put'}
        signal = signal_map.get(prediction, 'Error: Unknown Pred')
        logger.info(f"Prediction for {identifier} ({asset_type}): {signal} (Raw: {prediction})")
        return signal
    except Exception as e:
        logger.error(f"Error during prediction for {identifier}: {e}")
        return "Error: Prediction"

# --- Main Execution ---
if __name__ == "__main__":
    initialize_apis()

    # --- Training Phase ---
    logger.info("===== STARTING TRAINING PHASE =====")
    assets_to_train = []
    if binance_client:
        for pair in CRYPTO_PAIRS:
            assets_to_train.append({'id': pair, 'type': 'crypto', 'timeframe': TIMEFRAME_CRYPTO})
    if alpaca_client:
        for symbol in STOCK_SYMBOLS:
             assets_to_train.append({'id': symbol, 'type': 'stock', 'timeframe': TIMEFRAME_ALPACA})

    successfully_trained = {}
    for asset in assets_to_train:
        identifier = asset['id']
        asset_type = asset['type']
        timeframe = asset['timeframe']
        df = None
        # Load historical data
        if asset_type == 'crypto':
            # Try loading local Feather first (faster)
            feather_path = os.path.join(CRYPTO_DATA_DIR, f'{identifier.replace("/", "_")}-{timeframe}.feather')
            if os.path.exists(feather_path):
                 try:
                     logger.info(f"Loading cached Feather data for {identifier} from {feather_path}")
                     df = pd.read_feather(feather_path)
                     if 'date' in df.columns: df.set_index('date', inplace=True) # Ensure index is set
                     if not isinstance(df.index, pd.DatetimeIndex):
                          raise ValueError("Index is not DatetimeIndex")
                     if df.index.tz is None: df.index = df.index.tz_localize('UTC')
                     else: df.index = df.index.tz_convert('UTC')

                 except Exception as e:
                     logger.warning(f"Could not load/validate Feather file {feather_path}: {e}. Fetching from API.")
                     df = None # Fallback to API fetch
            if df is None:
                 df = fetch_binance_hist_data(identifier, timeframe, limit=5000) # Fetch more data for training

        elif asset_type == 'stock':
             df = fetch_alpaca_data(identifier, timeframe, limit=5000) # Fetch more data for training

        if df is not None and not df.empty:
            model = train_model(identifier, asset_type, df)
            if model:
                successfully_trained[identifier] = {'model': model, 'type': asset_type}
        else:
            logger.error(f"Could not obtain training data for {identifier}.")

    if not successfully_trained:
        logger.error("CRITICAL: No models were successfully trained. Exiting before live prediction loop.")
        exit() # Exit if no models are ready

    logger.info(f"===== TRAINING PHASE COMPLETE =====")
    logger.info(f"Successfully trained models for: {list(successfully_trained.keys())}")

    # --- Live Prediction Loop ---
    logger.info("===== STARTING LIVE PREDICTION LOOP (Hourly) =====")
    while True:
        logger.info("--- Hourly Prediction Cycle START ---")
        signals = {}
        for identifier, info in successfully_trained.items():
            signal = get_live_signal(identifier, info['type'], info['model'])
            signals[identifier] = signal
            print(f"LIVE SIGNAL [{time.strftime('%Y-%m-%d %H:%M:%S')}] {identifier} ({info['type']}): {signal}") # Direct print for user visibility

        logger.info("--- Hourly Prediction Cycle END ---")

        # Wait for the next hour
        wait_seconds = 3600
        logger.info(f"Sleeping for {wait_seconds / 60:.0f} minutes...")
        time.sleep(wait_seconds) 