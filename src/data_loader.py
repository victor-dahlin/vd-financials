import yfinance as yf
import pandas as pd
import streamlit as st

class StockDataLoader:
    """Handles fetching data from yfinance."""

    @staticmethod
    @st.cache_data
    def fetch_history(ticker_symbol: str, period: str = "1y", interval: str = "1d") -> pd.DataFrame:
        """
        Fetches historical stock data.
        
        Args:
            ticker_symbol: The stock ticker (e.g., 'AAPL').
            period: The data period to download (e.g., '1y', '5y', 'max').
            interval: The data interval (e.g., '1d', '1m').
            
        Returns:
            DataFrame containing historical data.
        """
        ticker = yf.Ticker(ticker_symbol)
        history = ticker.history(period=period, interval=interval)
        return history

    @staticmethod
    @st.cache_data
    def fetch_financials(ticker_symbol: str, quarterly: bool = False) -> pd.DataFrame:
        """
        Fetches financials (Income Statement).
        
        Args:
            ticker_symbol: The stock ticker.
            quarterly: Whether to fetch quarterly data instead of annual.
            
        Returns:
            DataFrame of financials (Income Statement).
        """
        ticker = yf.Ticker(ticker_symbol)
        # yfinance returns financials with columns as dates
        if quarterly:
            return ticker.quarterly_financials.T
        return ticker.financials.T # Transpose so dates are rows

    @staticmethod
    @st.cache_data
    def fetch_company_name(ticker_symbol: str) -> str:
        """
        Fetches the full company name.
        """
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            return info.get('longName', info.get('shortName', ticker_symbol))
        except Exception:
            return ticker_symbol

    @staticmethod
    @st.cache_data
    def fetch_balance_sheet(ticker_symbol: str, quarterly: bool = False) -> pd.DataFrame:
        """
        Fetches Balance Sheet.
        """
        ticker = yf.Ticker(ticker_symbol)
        if quarterly:
            return ticker.quarterly_balance_sheet.T
        return ticker.balance_sheet.T

    @staticmethod
    @st.cache_data
    def fetch_cashflow(ticker_symbol: str, quarterly: bool = False) -> pd.DataFrame:
        """
        Fetches Cash Flow Statement.
        """
        ticker = yf.Ticker(ticker_symbol)
        if quarterly:
            return ticker.quarterly_cashflow.T
        return ticker.cashflow.T
