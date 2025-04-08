# test_yfinance.py
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

print("--- Testing yfinance Download ---")
ticker = "SPY"
# Try fetching just the last month of data
end_date = datetime.today().strftime('%Y-%m-%d')
start_date = (datetime.today() - timedelta(days=30)).strftime('%Y-%m-%d')

print(f"Attempting to download {ticker} from {start_date} to {end_date}...")

try:
    data = yf.download(ticker, start=start_date, end=end_date, progress=False)

    if not data.empty:
        print(f"\nSUCCESS! Downloaded {len(data)} rows.")
        print("First 5 rows:")
        # Ensure index is datetime for printing
        data.index = pd.to_datetime(data.index)
        print(data.head().to_string())
    else:
        print("\nWARNING: Download returned an empty DataFrame.")

except Exception as e:
    print(f"\nERROR during yfinance download: {e}")

print("\n--- Test Complete ---")