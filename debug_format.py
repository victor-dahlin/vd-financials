
import pandas as pd
import numpy as np

def test_formatting_error():
    print("Testing formatting with None...")
    # Simulate dataframe with None in object column
    df = pd.DataFrame({
        'A': [1.0, 2.0, None], # None in float array -> NaN (usually)
        'B': [1.0, 2.0, None]  # If created as list with None
    })
    # If we force object dtype
    df['C'] = [1.0, 2.5, None]
    df['C'] = df['C'].astype(object)
    
    print("Dataframe:")
    print(df)
    print(df.dtypes)
    
    try:
        # replicate app.py style format
        styler = df.style.format("{:,.2f}")
        # To test, we need to render it? or _repr_html_?
        html = styler.to_html()
        print("Success! (Pandas handled it?)")
    except TypeError as e:
        print("Caught Expected TypeError:")
        print(e)
    except Exception as e:
        print(f"Caught other exception: {e}")

if __name__ == "__main__":
    test_formatting_error()
