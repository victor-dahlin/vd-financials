import yfinance as yf
import pandas as pd

ticker = yf.Ticker("AAPL")

print("--- FETCHING FINANCIALS ---")
fin = ticker.financials
print("Original Columns (Dates):", fin.columns.tolist())

print("\n--- TRANSPOSED & SORTED (ASCENDING = EARLIEST LEFT) ---")
# This mimics what we will do
df_display = fin.T.sort_index(ascending=True)
print("Display Columns (Metrics):", df_display.columns.tolist()[:5]) # just first few
print("Display Index (Dates):", df_display.index.tolist())

print("\n--- CHECKING FOR MISSING DATA IN EARLIEST PERIOD ---")
earliest_date = df_display.index[0]
print(f"Earliest Date: {earliest_date}")
earliest_data = df_display.loc[earliest_date]
print(f"Missing Values count in earliest period: {earliest_data.isna().sum()}")
print(f"Total Metrics: {len(earliest_data)}")

print("\n--- SAMPLE VALUES EARLIEST PERIOD ---")
print(earliest_data.head(10))
