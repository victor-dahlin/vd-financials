import yfinance as yf
import pandas as pd

ticker = yf.Ticker("AAPL")
print("--- INFO KEYS ---")
# Print first 50 keys to avoid spam
print(list(ticker.info.keys())[:50])

print("\n--- FINANCIALS INDEX (Metrics) ---")
# Note: In the current app, these are columns because of .T, but natively they are index
print(ticker.financials.index.tolist())

print("\n--- BALANCE SHEET INDEX (Metrics) ---")
print(ticker.balance_sheet.index.tolist())

print("\n--- CASH FLOW INDEX (Metrics) ---")
print(ticker.cashflow.index.tolist())
