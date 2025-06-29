import streamlit as st
import pandas as pd
import yfinance as yf
import time
from utils import get_batches

# different stock indexes 
INDEX_CONFIGS = {
    'NASDAQ': {
        'ticker': '^IXIC', 
        'file_path': 'nasdaq_tickers.csv',
        'use_batches': True,
    },
    'NYSE': {
        'ticker': '^NYA',
        'file_path': 'nyse_tickers.csv',
        'use_batches': True,
    },
    'DOWJONES': {
        'ticker': '^DJI',
        'file_path': 'dowjones_tickers.csv',
        'use_batches': True,
    }
}

def download_batch(tickers, period, interval, ticker_info_dict):
    try:
        all_frames = []
        company_info_dict = {}
        
        # getting the data in bulk (for the whole batch) 
        try:
            bulk_data = yf.download(
                tickers=tickers,
                period=period,
                interval=interval,
                group_by='ticker',
                auto_adjust=False,
                threads=True,
                progress=False
            )
            
            # process each ticker
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, ticker in enumerate(tickers):
                try:
                    # get ticker info from the pre-loaded data
                    ticker_info = ticker_info_dict.get(ticker, {
                        'Company Name': 'N/A',
                        'Sector': 'N/A'
                    })
                    
                    company_info = {
                        'Ticker': ticker,
                        'Company Name': ticker_info.get('Company Name', 'N/A'),
                        'Sector': ticker_info.get('Sector', 'N/A')
                    }
                    company_info_dict[ticker] = company_info
                    
                    # extract the ticker data from bulk download
                    if isinstance(bulk_data.columns, pd.MultiIndex):
                        ticker_data = bulk_data.xs(ticker, axis=1, level=0)
                    else:
                        ticker_data = bulk_data
                    
                    ticker_data = ticker_data.dropna()
                    if not ticker_data.empty:
                        ticker_data['Ticker'] = ticker
                        ticker_data['Company Name'] = company_info['Company Name']
                        ticker_data['Sector'] = company_info['Sector']
                        all_frames.append(ticker_data)
                        
                except Exception as e:
                    continue
                
                progress_bar.progress((i + 1) / len(tickers))
                status_text.text(f"Processing: {i + 1}/{len(tickers)} stocks")
            
            progress_bar.empty()
            status_text.empty()
            
        except Exception as e:
            st.error("Download Failed :(")
            
        return all_frames, company_info_dict
        
    except Exception as e:
        st.error(f"Batch download failed: {e}")
        return [], {}

def download_index_data(selected_indices, period, interval):
    tickers, ticker_info_dict = get_combined_tickers_and_info(selected_indices)
    
    if not tickers:
        st.error(f"No tickers found for selected indices: {', '.join(selected_indices)}")
        return None
    
    if(len(selected_indices) > 1):
        st.warning("**Note:** For multiple indices, duplicates are removed.")
    st.warning("**Note:** Few stocks may have been delisted, or have no data (in the selected period) to be fetched.")
    st.info(f"Downloading data for {len(tickers)} stocks...")
    
    batch_size = 500
    batches = list(get_batches(tickers, batch_size))
    
    all_frames = []
    all_company_info = {}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for batch_num, batch in enumerate(batches):
        status_text.text(f"Processing batch {batch_num + 1}/{len(batches)} ({len(batch)} stocks)...")
        
        batch_frames, batch_info = download_batch(batch, period, interval, ticker_info_dict)
        
        all_frames.extend(batch_frames)
        all_company_info.update(batch_info)
        
        progress_bar.progress((batch_num + 1) / len(batches))
        
        time.sleep(1) # to prevent rate limiting :)

    progress_bar.empty()
    status_text.empty()
    
    if all_frames:
        combined_df = pd.concat(all_frames, ignore_index=True)
        st.success(f"Successfully downloaded data for {len(all_frames)} stocks with company information")
        return combined_df
    else:
        st.error("No data collected")
        return None

def load_index_tickers(index_name):
    try:
        config = INDEX_CONFIGS.get(index_name.upper())
        if not config:
            st.error(f"Index {index_name} not found in configurations")
            return [], {}
            
        file_path = config['file_path']
        
        df = pd.read_csv(file_path)
        ticker_info_dict = {}
        for _, row in df.iterrows():
            ticker_info_dict[row['Symbol']] = {
                'Company Name': row['Company Name'],
                'Sector': row['Sector']
            }
        
        tickers = df['Symbol'].dropna().tolist()
        st.info(f"Loaded {len(tickers)} tickers from {index_name}")
        return tickers, ticker_info_dict
        
    except Exception as e:
        st.error(f"Error loading {index_name} tickers from {file_path}: {e}")
        return [], {}

def get_index_tickers_and_info(index_name):
    try:
        return load_index_tickers(index_name)
        
    except Exception as e:
        st.error(f"Error fetching {index_name} tickers: {e}")
        return [], {}

def get_combined_tickers_and_info(selected_indices):
    all_tickers = []
    combined_ticker_info = {}
    
    for index_name in selected_indices:
        tickers, ticker_info = get_index_tickers_and_info(index_name)
        if tickers:
            all_tickers.extend(tickers)
            combined_ticker_info.update(ticker_info)
    
    unique_tickers = list(dict.fromkeys(all_tickers))
    
    return unique_tickers, combined_ticker_info
