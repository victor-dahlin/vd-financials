
import pandas as pd
import yfinance as yf
import src.analysis as analysis
from src.data_loader import StockDataLoader

def test_crash():
    ticker = "AAPL"
    print("Fetching data...")
    # Mimic app.py logic
    # Need to fetch financials manually or mock them
    # StockDataLoader.fetch_financials uses yf.Ticker(...).quarterly_financials usually
    # But let's just use StockDataLoader directly if possible.
    
    financials = StockDataLoader.fetch_financials(ticker, quarterly=True)
    bs = StockDataLoader.fetch_balance_sheet(ticker, quarterly=True)
    cfs = StockDataLoader.fetch_cashflow(ticker, quarterly=True)
    
    val_prices = StockDataLoader.fetch_history(ticker, period="10y", interval="1d")
    
    print("Calling calculate_fundamental_metrics...")
    try:
        fund_metrics = analysis.calculate_fundamental_metrics(financials, bs, cfs, price_data=val_prices)
        print("Success!")
        print(fund_metrics.head())
    except Exception as e:
        print("Caught Exception:")
        print(e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_crash()
