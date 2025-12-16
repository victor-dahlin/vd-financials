import yfinance as yf

def check(t):
    print(f"Checking {t}...")
    try:
        data = yf.Ticker(t).history(period="1d")
        if data.empty:
            print(f"{t}: Empty")
        else:
            print(f"{t}: Found {len(data)} rows")
    except Exception as e:
        print(f"{t}: Error {e}")

check("VOLV-B") # Probably empty
check("VOLV-B.ST") # Should exist
check("NONEXISTENT")
