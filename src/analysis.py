import pandas as pd

def calculate_sma(data: pd.DataFrame, window: int = 20) -> pd.Series:
    """Calculates Simple Moving Average."""
    return data['Close'].rolling(window=window).mean()

def calculate_ema(data: pd.DataFrame, window: int = 20) -> pd.Series:
    """Calculates Exponential Moving Average."""
    return data['Close'].ewm(span=window, adjust=False).mean()

def calculate_rsi(data: pd.DataFrame, window: int = 14) -> pd.Series:
    """Calculates Relative Strength Index."""
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()

    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_bollinger_bands(data: pd.DataFrame, window: int = 20):
    """Calculates Bollinger Bands."""
    sma = calculate_sma(data, window)
    std = data['Close'].rolling(window=window).std()
    upper_band = sma + (std * 2)
    lower_band = sma - (std * 2)
    return upper_band, lower_band

def calculate_fundamental_metrics(financials: pd.DataFrame, balance_sheet: pd.DataFrame, cashflow: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates a comprehensive set of fundamental metrics from financial statements.
    Assumes inputs are Date-indexed (rows=dates, cols=metrics).
    """
    metrics = pd.DataFrame(index=financials.index)

    # Helper to safely get column
    def get_val(df, keywords):
        for k in keywords:
            for c in df.columns:
                if k.lower() == c.lower() or k.lower() in c.lower():
                    return df[c]
        return pd.Series(index=df.index, dtype=float) # Return NaNs if not found

    # --- 1. Profitability Metrics ---
    revenue = get_val(financials, ['Total Revenue', 'Revenue'])
    net_income = get_val(financials, ['Net Income', 'Net Income Common Stockholders'])
    gross_profit = get_val(financials, ['Gross Profit'])
    op_income = get_val(financials, ['Operating Income'])
    ebitda = get_val(financials, ['EBITDA', 'Normalized EBITDA'])
    ebit = get_val(financials, ['EBIT'])
    
    metrics['Gross Margin %'] = (gross_profit / revenue) * 100
    metrics['Operating Margin %'] = (op_income / revenue) * 100
    metrics['Net Margin %'] = (net_income / revenue) * 100
    metrics['EBITDA Margin %'] = (ebitda / revenue) * 100
    
    stockholders_equity = get_val(balance_sheet, ['Stockholders Equity', 'Total Stockholder Equity'])
    total_assets = get_val(balance_sheet, ['Total Assets'])
    
    metrics['ROE %'] = (net_income / stockholders_equity) * 100
    metrics['ROA %'] = (net_income / total_assets) * 100

    # --- 2. Liquidity & Health ---
    current_assets = get_val(balance_sheet, ['Current Assets', 'Total Current Assets'])
    current_liabilities = get_val(balance_sheet, ['Current Liabilities', 'Total Current Liabilities'])
    inventory = get_val(balance_sheet, ['Inventory'])
    
    metrics['Current Ratio'] = current_assets / current_liabilities
    metrics['Quick Ratio'] = (current_assets - inventory) / current_liabilities
    
    total_debt = get_val(balance_sheet, ['Total Debt'])
    metrics['Debt-to-Equity'] = total_debt / stockholders_equity
    metrics['Debt-to-Assets'] = total_debt / total_assets
    
    interest_expense = get_val(financials, ['Interest Expense'])
    # Interest Coverage = EBIT / Interest Expense
    metrics['Interest Coverage'] = ebit / interest_expense

    # --- 3. Efficiency ---
    metrics['Asset Turnover'] = revenue / total_assets
    
    receivables = get_val(balance_sheet, ['Receivables', 'Accounts Receivable'])
    # Receivables Turnover = Revenue / Receivables
    metrics['Receivables Turnover'] = revenue / receivables

    # --- 4. Cash Flow Metrics ---
    op_cash_flow = get_val(cashflow, ['Operating Cash Flow', 'Total Cash From Operating Activities'])
    capex = get_val(cashflow, ['Capital Expenditure'])
    
    # Free Cash Flow = Operating Cash Flow + CapEx (assuming CapEx is typically negative)
    # metrics['Operating Cash Flow'] = op_cash_flow
    # metrics['Free Cash Flow'] = op_cash_flow + capex 
    free_cash_flow = op_cash_flow + capex
    
    metrics['FCF / Net Income'] = free_cash_flow / net_income

    # --- 5. Per Share Data ---
    shares = get_val(financials, ['Diluted Average Shares', 'Basic Average Shares'])
    metrics['EPS (Diluted)'] = get_val(financials, ['Diluted EPS'])
    metrics['EPS (Basic)'] = get_val(financials, ['Basic EPS'])
    metrics['Book Value Per Share'] = stockholders_equity / shares
    metrics['FCF Per Share'] = free_cash_flow / shares

    # Cleanup: Return Metrics as Rows, Dates as Columns
    # Request: Invert X-axis (Oldest -> Newest) implies Ascending order of dates
    return metrics.sort_index(ascending=True).T

def calculate_dcf(
    free_cash_flow: float,
    growth_rate: float,
    terminal_growth_rate: float,
    discount_rate: float,
    years: int = 5,
    shares_outstanding: float = 1,
    net_debt: float = 0
) -> dict:
    """
    Performs a simple DCF Analysis.
    
    Args:
        free_cash_flow: Most recent FCF (or TTM).
        growth_rate: Expected annual growth rate for the projection period (decimal, e.g. 0.10).
        terminal_growth_rate: Perpetual growth rate after projection period (decimal, e.g. 0.025).
        discount_rate: WACC (decimal, e.g. 0.08).
        years: Number of years to project.
        shares_outstanding: Total shares.
        net_debt: Total Debt - Cash.
        
    Returns:
        Dictionary with 'fair_value', 'share_price', 'projections'.
    """
    projections = []
    current_fcf = free_cash_flow
    
    # 1. Project Cash Flows
    for i in range(1, years + 1):
        current_fcf *= (1 + growth_rate)
        discount_factor = (1 + discount_rate) ** i
        pv = current_fcf / discount_factor
        projections.append({
            "Year": i,
            "FCF": current_fcf,
            "PV": pv
        })
        
    sum_pv_fcf = sum(p['PV'] for p in projections)
    
    # 2. Terminal Value (Gordon Growth)
    last_fcf = projections[-1]['FCF']
    terminal_value = (last_fcf * (1 + terminal_growth_rate)) / (discount_rate - terminal_growth_rate)
    pv_terminal_value = terminal_value / ((1 + discount_rate) ** years)
    
    # 3. Enterprise Value
    enterprise_value = sum_pv_fcf + pv_terminal_value
    
    # 4. Equity Value
    equity_value = enterprise_value - net_debt
    
    # 5. Share Price
    fair_value = equity_value / shares_outstanding
    
    return {
        "fair_value": fair_value,
        "enterprise_value": enterprise_value,
        "equity_value": equity_value,
        "projections": projections,
        "terminal_value": terminal_value,
        "pv_terminal_value": pv_terminal_value
    }
