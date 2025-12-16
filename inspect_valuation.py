import yfinance as yf
ticker = yf.Ticker("AAPL")
info = ticker.info
print("--- Valuation Keys Present ---")
keys_to_check = ["trailingPE", "forwardPE", "pegRatio", "priceToBook", "enterpriseToEbitda", "beta", "dividendYield", "trailingEps", "forwardEps", "bookValue"]
for k in keys_to_check:
    print(f"{k}: {info.get(k)}")
