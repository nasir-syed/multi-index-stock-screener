import streamlit as st
import pandas as pd
import yfinance as yf
import time
from utils import get_batches

# the 30 companies for dow jones 
DOW_JONES_TICKERS = [
    'AAPL', 'AMGN', 'AXP', 'BA', 'CAT', 'CRM', 'CSCO', 'CVX', 'DIS', 'DOW',
    'GS', 'HD', 'HON', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD', 'MMM',
    'MRK', 'MSFT', 'NKE', 'PG', 'TRV', 'UNH', 'V', 'VZ', 'WBA', 'WMT'
]

INDEX_CONFIGS = {
    'S&P 500': {
        'ticker': '^GSPC',
        'url': 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies',
        'table_index': 0,
        'symbol_column': 'Symbol',
        'use_batches': False
    },
    'NASDAQ': {
        'ticker': '^IXIC', 
        'file_path': 'nasdaq_tickers.txt',
        'use_batches': True,
        'batch_size': 500
    },
    'Dow Jones': {
        'ticker': '^DJI',
        'tickers': DOW_JONES_TICKERS,
        'use_batches': False
    }
}

# loads the nasdaq tickers from the txt file
def load_nasdaq_tickers(file_path='nasdaq_tickers.txt'):
    try:
        df = pd.read_csv(file_path, sep='|')
        tickers = df['Symbol'].dropna().tolist()
        return tickers
    except Exception as e:
        st.error(f"Error loading NASDAQ tickers from {file_path}: {e}")
        return []

# depending upon the users choice of index, retrives the appropriate tickers 
def get_index_tickers(index_name):
    try:
        config = INDEX_CONFIGS[index_name]
        
        if index_name == 'S&P 500':
            # get S&P 500 tickers from Wikipedia
            tables = pd.read_html(config['url'])
            df = tables[config['table_index']]
            tickers = df[config['symbol_column']].tolist()
            tickers = [ticker.replace('.', '-') for ticker in tickers]
            
        elif index_name == 'NASDAQ':
            tickers = load_nasdaq_tickers(config['file_path'])
            
        elif index_name == 'Dow Jones':
            tickers = config['tickers'].copy()
            
        return tickers
        
    except Exception as e:
        st.error(f"Error fetching {index_name} tickers: {e}")
        return []


# downloads a batch of tickers (used for NASDAQ) (used by the download_index_data)
def download_batch(tickers, period, interval): 
    try:
        return yf.download(
            tickers=tickers,
            period=period,
            interval=interval,
            group_by='ticker',
            auto_adjust=False,
            threads=True,
            progress=False
        )
    except Exception as e:
        st.error(f"Batch download failed. Error: {e}")
        return None

# downloads a all tickers in one go (used by the download_index_data)
def download_all(tickers, period, interval):
    try:
        return yf.download(
            tickers=tickers,
            period=period,
            interval=interval,
            group_by='ticker',
            auto_adjust=False,
            threads=True,
            progress=False
        )
    except Exception as e:
        st.error(f"Download failed. Error: {e}")
        return None

def download_index_data(index_name, period, interval):
    tickers = get_index_tickers(index_name)
    
    if not tickers:
        st.error(f"No tickers found for {index_name}")
        return None
    
    st.info(f"Found {len(tickers)} tickers for {index_name}")
    
    config = INDEX_CONFIGS[index_name]
    
    if config['use_batches']:
        # use batch processing (for NASDAQ)
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        batch_size = config['batch_size']
        batches = list(get_batches(tickers, batch_size))
        all_frames = []
        
        for batch_num, batch in enumerate(batches):
            status_text.text(f"Downloading Batch {batch_num + 1}/{len(batches)} ({len(batch)} tickers)...")
            progress_bar.progress((batch_num + 1) / len(batches))
            
            hist = download_batch(batch, period, interval)
            if hist is None:
                continue
                
            for ticker in batch:
                try:
                    if len(batch) == 1:
                        df = hist
                    else:
                        if isinstance(hist.columns, pd.MultiIndex):
                            df = hist.xs(ticker, axis=1, level=0)
                        else:
                            df = hist
                    
                    df = df.dropna()
                    if not df.empty:
                        df['Ticker'] = ticker
                        all_frames.append(df)
                        
                except Exception as e:
                    continue
            
            # a small delay to prevent rate limiting
            time.sleep(0.5)
        
        progress_bar.empty()
        status_text.empty()
        
        if all_frames:
            combined_df = pd.concat(all_frames)
            st.success(f"Successfully downloaded data for {len(all_frames)} stocks")
            return combined_df
        else:
            st.error("No data collected")
            return None
    
    else:
        # download data for all tickers in one go (for S&P 500 and Dow Jones)
        with st.spinner(f'Downloading {index_name} data...'):
            hist = download_all(tickers, period, interval)
            if hist is None:
                return None
            
            all_frames = []
            
            for ticker in tickers:
                try:
                    if len(tickers) == 1:
                        df = hist
                    else:
                        if isinstance(hist.columns, pd.MultiIndex):
                            df = hist.xs(ticker, axis=1, level=0)
                        else:
                            df = hist
                    
                    df = df.dropna()
                    if not df.empty:
                        df['Ticker'] = ticker
                        all_frames.append(df)
                        
                except Exception as e:
                    continue
            
            if all_frames:
                combined_df = pd.concat(all_frames)
                st.success(f"Successfully downloaded data for {len(all_frames)} stocks")
                return combined_df
            else:
                st.error("No data collected")
                return None
