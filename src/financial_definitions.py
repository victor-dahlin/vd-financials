# Standard Financial Statement Structures

# Each tuple: (Section Name, [List of yfinance metrics to include])

INCOME_STATEMENT_STRUCTURE = [
    ("Revenue & Gross Profit", [
        "Total Revenue", "Operating Revenue", "Cost Of Revenue", "Gross Profit"
    ]),
    ("Operating Expenses", [
        "Research And Development", "Selling General And Administration", 
        "Operating Expense", "Total Operating Income As Reported", "Operating Income"
    ]),
    ("Non-Operating Income & Expenses", [
        "Interest Expense", "Interest Income", "Net Interest Income",
        "Other Non Operating Income Expenses", "Pretax Income"
    ]),
    ("Taxes & Net Income", [
        "Tax Provision", "Net Income Common Stockholders", "Net Income", 
        "Diluted EPS", "Basic EPS", "Diluted Average Shares", "Basic Average Shares"
    ])
]

BALANCE_SHEET_STRUCTURE = [
    ("Assets", []), # Placeholder, will handle dynamically or just list major ones
    ("Current Assets", [
        "Cash And Cash Equivalents", "Short Term Investments", "Total Cash From Operating Activities", # Wait this is CF
        "Cash Cash Equivalents And Short Term Investments", 
        "Receivables", "Inventory", "Other Current Assets", "Total Current Assets"
    ]),
    ("Non-Current Assets", [
        "Net PPE", "Investments And Advances", "Goodwill", "Intangible Assets",
        "Total Non Current Assets", "Total Assets"
    ]),
    ("Liabilities", []),
    ("Current Liabilities", [
        "Payables", "Accounts Payable", "Current Debt", "Current Deferred Liabilities",
        "Total Current Liabilities"
    ]),
    ("Non-Current Liabilities", [
        "Long Term Debt", "Total Non Current Liabilities Net Minority Interest",
        "Total Liabilities Net Minority Interest"
    ]),
    ("Equity", [
        "Common Stock", "Retained Earnings", "Stockholders Equity", 
        "Total Capitalization"
    ])
]

CASH_FLOW_STRUCTURE = [
    ("Operating Activities", [
        "Net Income", "Depreciation And Amortization", "Change In Working Capital",
        "Stock Based Compensation", "Operating Cash Flow"
    ]),
    ("Investing Activities", [
        "Capital Expenditure", "Purchase Of Business", "Purchase Of Investment",
        "Sale Of Investment", "Investing Cash Flow"
    ]),
    ("Financing Activities", [
        "Repayment Of Debt", "Issuance Of Debt", "Issuance Of Capital Stock", 
        "Repurchase Of Capital Stock", "Cash Dividends Paid", "Financing Cash Flow"
    ]),
    ("Summary", [
        "End Cash Position", "Changes In Cash", "Free Cash Flow"
    ])
]
