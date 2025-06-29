import streamlit as st
import pandas as pd
import numpy as np
from utils import calculate_atr

# summarises the raw data retrieved from yfinance by calculating average price, gap, and more.
def create_summary_data(raw_data):
    if raw_data is None or raw_data.empty:
        return None
    
    summary_results = []
    grouped = raw_data.groupby('Ticker')
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    total_tickers = len(grouped) 
    
    for idx, (ticker, df) in enumerate(grouped):
        status_text.text(f"Processing {ticker} ({idx + 1}/{total_tickers})...")
        progress_bar.progress((idx + 1) / total_tickers)
        
        try:
            df = df.sort_index()
            if len(df) < 2:
                continue
            
            # get the latest data points
            latest_data = df.iloc[-1]
            prev_close = df['Close'].iloc[-2] if len(df) > 1 else df['Close'].iloc[-1]
            
            # calculate metrics
            today_open = latest_data['Open']
            today_close = latest_data['Close']
            today_high = latest_data['High']
            today_low = latest_data['Low']
            
            # average price (OHLC average for the latest period)
            avg_price = (today_open + today_high + today_low + today_close) / 4
            
            # gap calculations
            gap_abs = today_open - prev_close
            gap_pct = (gap_abs / prev_close) * 100 if prev_close != 0 else 0
            
            total_volume = df['Volume'].sum()  
            avg_volume = df['Volume'].mean()   
            
            # ATR calculation
            if len(df) >= 14:
                atr = calculate_atr(df).iloc[-1]
            else:
                atr = (today_high - today_low)  # simple range in case not enough data for ATR
            
            company_name = df['Company Name'].iloc[-1] if 'Company Name' in df.columns else 'N/A'
            sector = df['Sector'].iloc[-1] if 'Sector' in df.columns else 'N/A'

            
            summary_results.append({
                'Ticker': ticker,
                'Company Name': company_name,
                'Sector': sector,
                'Price ($)': round(today_close, 2),
                'Avg Price ($)': round(avg_price, 2),
                'Gap ($)': round(gap_abs, 2),
                'Gap (%)': round(gap_pct, 2),
                'Volume': int(total_volume),  
                'Avg Volume': int(avg_volume),      
                'ATR': round(atr, 2),
                # 'Data Points': len(df), 
            })
            
        except Exception as e:
            continue
    
    progress_bar.empty()
    status_text.empty()
    
    if summary_results:
        df_summary = pd.DataFrame(summary_results)
        
        st.success(f"Successfully processed {len(df_summary)} stocks")
        return df_summary
    else:
        st.error("No summary data created")
        return None

# applies the chosen filters to the stocks and retrieves those that meet them
def screen_stocks(df, price_min, price_max, gap_pct_threshold,
                 min_volume, min_avg_volume, min_atr, selected_sectors=None):
    
    df_copy = df.copy()
    
    screened = df_copy[
        (df_copy['Price ($)'] >= price_min) &
        (df_copy['Price ($)'] <= price_max) &
        (df_copy['Gap (%)'].abs() >= gap_pct_threshold) &
        (df_copy['Volume'] >= min_volume) &
        (df_copy['Avg Volume'] >= min_avg_volume) &
        (df_copy['ATR'] >= min_atr)
    ]
    
    # apply sector filter
    if selected_sectors and len(selected_sectors) > 0:
        screened = screened[screened['Sector'].isin(selected_sectors)]
    
    # sort by absolute gap percentage (highest gaps first)
    screened_sorted = screened.sort_values(by='Gap (%)', key=abs, ascending=False)
    return screened_sorted

# detects stocks with abnormally high price, gap, volume and atr in comparison to others stocks in that column
def detect_anomalies(df):
    if df.empty:
        return None
    
    anomalies = []
    
    # z-score based anomaly detection
    for column in ['Price ($)', 'Gap (%)', 'Volume', 'ATR']:
        if column in df.columns:
            z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
            anomaly_mask = z_scores > 2.5  #  more than 2.5 standard deviations
            
            for idx in df[anomaly_mask].index:
                anomalies.append({
                    'Ticker': df.loc[idx, 'Ticker'],
                    'Anomaly Type': f'{column}',
                    'Value': df.loc[idx, column],
                    'Z Score': z_scores.loc[idx],
                })
    
    if anomalies:
        anomaly_df = pd.DataFrame(anomalies)
        anomaly_df = anomaly_df.sort_values('Z Score', ascending=False).drop_duplicates('Ticker')
        return anomaly_df.head(10)  #
    
    return None
