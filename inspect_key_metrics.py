import yfinance as yf
ticker = yf.Ticker("AAPL")
fin = ticker.financials.T.sort_index(ascending=True)

print("--- Earliest Date Data for Key Metrics ---")
keys = ["Total Revenue", "Net Income", "Operating Income", "Cost Of Revenue"]
print(fin.loc[fin.index[0], keys])

print("\n--- All dates ---")
print(fin.index)
