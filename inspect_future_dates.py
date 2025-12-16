import yfinance as yf
ticker = yf.Ticker("AAPL")
fin = ticker.financials.T.sort_index(ascending=True)

print("--- 2025 Data ---")
try:
    print(fin.loc['2025-09-30', ["Total Revenue", "Net Income"]])
except KeyError:
    print("2025 not found via string lookup, checking integer index")
    print(fin.iloc[-1][["Total Revenue", "Net Income"]])

print("\n--- 2024 Data ---")
try:
    print(fin.loc['2024-09-30', ["Total Revenue", "Net Income"]])
except KeyError:
    print("2024 not found via string lookup")
