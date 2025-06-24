# multi-index-stock-screener

A dynamic and interactive Streamlit app that enables real-time screening and analysis of stocks across major U.S. market indices (S&P 500, NASDAQ, and more), designed with both traders and data analysts in mind as it combines great visuals with powerful filters to help you discover useful market insights effortlessly!

Give it a try: https://multi-index-stock-screener.streamlit.app/

---

## Key Features
- **Multi-Index Support**: Analyse stocks across S&P major U.S market indices with a simple dropdown.
- **Powerful Filters**: Filter stocks based on customizable criteria like volatility, volume, gap and more.
- **Real-Time Summary Metrics**: Get instant stats to help discover market insights.
- **Anomaly Detection**: Identify market outliers using Z-Score based anomaly detection.
- **CSV Export**: Download screened stocks directly as CSV for external analysis.
---

## Technologies & Architecture
### Technologies Used
- **Streamlit** - Rapid UI development for data apps
- **Pandas** - Data processing & transformation
- **YFinance** - Fetching stock data
- **Plotly** - Interactive visualizations

### Architecture Overview
- **screener.py**: Orchestrates UI, routing, state management, and main screening logic.
- **data_loader.py**: Fetches and downloads tickers based on selected index.
- **visuals.py**: Generates the charts and tables.
- **analysis.py**: Summarises the raw data, applies user-provided filters (if any) and detects anomalies.
- **utils.py**: Splits large number of stocks into batches (to prevent rate limiting), formats and styles the dataframe as well.

---

## How 2 Run?
clone the repository
```bash
git clone https://github.com/yourusername/multi-index-stock-screener.git
```
download the dependencies
```bash
pip install pandas numpy streamlit yfinance plotly
```
and finally run the screener.py file!
```bash
python -m streamlit run screener.py
```
