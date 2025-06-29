import pandas as pd
import numpy as np

# batch generator used for splitting the tickers into batches
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

# highlights the $ gap in the table according to the value (< 0 will be red, > 0 will be green)
def apply_gap_styling(df):
    def color_gaps(val):
        if val > 0:
            return 'background-color: #d4edda; color: #155724'
        else:
            return 'background-color: #f8d7da; color: #721c24'
    
    styled_df = df.style.map(color_gaps, subset=['Gap (%)'])
    return styled_df

# validates the period and interval input provided in the intial configuration screen
def validate_period_interval(period, interval):
    period_minutes = {
        '1d': 1440,    
        '3d': 4320,    
        '5d': 7200,    
        '1wk': 10080,  
        '2wk': 20160,  
        '1mo': 43200,  
        '2mo': 86400,  
        '3mo': 129600  
    }
    
    interval_minutes = {

        '15m': 15,
        '30m': 30,
        '1h': 60,
        '1d': 1440,
        '5d': 7200,
        '1wk': 10080,
        '1mo': 43200,
        '3mo': 129600
    }
    
    period_val = period_minutes.get(period, 0)
    interval_val = interval_minutes.get(interval, 0)
    
    if interval_val > period_val:
        return False, f"Interval ({interval}) cannot be greater than period ({period})"
    
    return True, ""
