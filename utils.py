import pandas as pd
import numpy as np

# batch generator used for splitting the NASDAQ tickers into batches
def get_batches(tickers, batch_size=500):
    for i in range(0, len(tickers), batch_size):
        yield tickers[i:i + batch_size]

# average true range calculation 
def calculate_atr(data, period=14):
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = tr.rolling(window=period).mean()
    return atr

# renames columns for better display 
def format_dataframe(df):
    display_df = df.copy()
    display_df = display_df.reset_index(drop=True)
    
    column_mapping = {
        'Latest Price': 'Price ($)',
        'Average_Price': 'Avg Price ($)',
        'Gap($)': 'Gap ($)',
        'Gap(%)': 'Gap (%)',
        'Prev_Close': 'Prev Close ($)'
    }
    display_df = display_df.rename(columns=column_mapping)
    
    numeric_cols = ['Price ($)', 'Avg Price ($)', 'Gap ($)', 'Open', 'High', 'Low', 'Close', 'Prev Close ($)', 'ATR']
    for col in numeric_cols:
        if col in display_df.columns:
            display_df[col] = display_df[col].round(2)
    
    return display_df

# highlights the $ gap in the table according to the value (< 0 will be red, > 0 will be green)
def apply_gap_styling(df):
    def color_gaps(val):
        if val > 0:
            return 'background-color: #d4edda; color: #155724'
        else:
            return 'background-color: #f8d7da; color: #721c24'
    
    styled_df = df.style.map(color_gaps, subset=['Gap ($)'])
    return styled_df
