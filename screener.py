import streamlit as st
from datetime import datetime
from utils import *
from data_loader import *
from analysis import *
from visuals import *

# page configuration 
st.set_page_config(
    page_title="[: Multi-Index Stock Screener :]",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# custom CSS 
st.markdown("""
<style>  
            
     .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        color: #2a9d8f !important;
    }
    
    .config-section {
        background: none;
        padding: 2rem;
        border-radius: 15px;
        color: white;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    
    .criteria-section {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
            
    .section-divider {
        padding: 0.75rem;
        margin: 0.75rem 0;
    }
    
    .heading-divider {
        padding: 8px;
    }
            
    .success-banner, div[data-testid="stAlert"][data-baseweb="notification"] {
        background: linear-gradient(90deg, #2a9d8f, #20c997);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .warning-banner {
        background: linear-gradient(90deg, #ffc107, #fd7e14);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .error-banner {
        background: linear-gradient(90deg, #dc3545, #e74c3c);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
    }
            
    .stButton > button[kind="primary"], .stButton > button[kind="secondary"], .stDownloadButton > button {
        background: transparent !important;
        border: 1px solid #2a9d8f !important;
        color: #2a9d8f !important; 
        transition: 0.3s ease-in-out !important;
    }
            
    .stButton > button {
        height: 3rem !important;
        width: 100% !important;
    }

    .stButton > button[kind="primary"] {
        height: 3.5rem !important;
    }    

    .stButton > button[kind="primary"]:hover, .stButton > button[kind="secondary"]:hover, .stDownloadButton > button:hover {
        background: #2a9d8f !important;
        border: none !important;
        color: #fafafa !important;
    }

    /* Secondary button custom colors */
    .stButton > button[kind="secondary"] {
        margin-top: 1.7rem !important;
        height: 2rem !important;
    }
            
    div[data-testid="InputInstructions"] > span:nth-child(1) {
        visibility: hidden;
    }
</style>
""", unsafe_allow_html=True)

default_session_state = {
    'data_loaded': False,
    'raw_data': None,
    'summary_data': None,
    'selected_indices': None, 
    'filtered_data': None,
    'filters_applied': False
}

for key, default_value in default_session_state.items():
    if key not in st.session_state:
        st.session_state[key] = default_value


# shows the initial screen that prompts the user to choose the index, period and interval 
def configuration_screen():
    st.markdown('<h1 class="main-header">[: Multi-Index Stock Screener :]</h1>', unsafe_allow_html=True)

    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.markdown("## Configuration")
    st.markdown('<div class="heading-divider">', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Market Indices")
        selected_indices = st.multiselect(
            "Choose Indices",
            options=list(INDEX_CONFIGS.keys()),
            default=['DOWJONES'],
            help="Select one or more stock market indices to analyse"
        )
        
    with col2:
        tpdicol1, tpdicol2 = st.columns(2)
        with tpdicol1:
            st.markdown("### Time Period")
            period = st.selectbox(
                "Choose Period",
                options=['1d', '3d', '5d', '1wk', '2wk', '1mo', '2mo', '3mo'],
                index=1,  
                help="Time period for historical data"
            )
        
        with tpdicol2:
            st.markdown("### Data Interval")
            interval = st.selectbox(
                "Choose Interval",
                options=['15m', '30m', '1h', '1d', '5d', '1wk', '1mo', '3mo'],
                index=2, 
                help="Data interval (frequency)"
            )        
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider">', unsafe_allow_html=True)
    
    # validate the period and interval combination, in case of invalid cases show appropriate warnings
    is_valid_combination, validation_error = validate_period_interval(period, interval)
    
    no_indices_selected = not selected_indices
    invalid_period_interval = not is_valid_combination
    
    if no_indices_selected:
        st.warning("Please select at least one market index to proceed.")
    
    if invalid_period_interval:
        st.error(f"Invalid Configuration: {validation_error}")
        st.info("**Tip:** Choose a smaller interval or a longer period, for example, if you select '1d' period, use intervals like '15m', '30m', or '1h'.")
    
    # determine if button should be disabled
    button_disabled = no_indices_selected or invalid_period_interval
    
    if button_disabled:
        st.button("Load Data", type="primary", use_container_width=True, disabled=True)
    else:
        if st.button("Load Data", type="primary", use_container_width=True):
            st.session_state.selected_indices = selected_indices
            
            with st.spinner(f"Loading data for {', '.join(selected_indices)}..."):
                raw_data = download_index_data(selected_indices, period, interval)
                
                if raw_data is not None:
                    st.session_state.raw_data = raw_data
                    
                    with st.spinner("Creating summary data..."):
                        summary_data = create_summary_data(raw_data)
                        
                        if summary_data is not None:
                            st.session_state.summary_data = summary_data
                            st.session_state.data_loaded = True
                            st.session_state.filters_applied = False
                            st.session_state.filtered_data = None
                            st.rerun()

# displays the main interface that shocases the stock data and other visuals
def screening_interface():
    st.markdown('<h1 class="main-header">[: Multi-Index Stock Screener :]</h1>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider">', unsafe_allow_html=True)
    
    # show the current configuration (index choses and how many stocks loaded)
    col1, col2 = st.columns([3, 1])
    with col1:
        # Format the selected indices for display
        indices_display = ', '.join(st.session_state.selected_indices) if st.session_state.selected_indices else "None"
        st.info(f"**Current Data:** {indices_display} | {len(st.session_state.summary_data)} stocks loaded")
    with col2:
        if st.button("Load New Data", type="primary", use_container_width=True):
            st.session_state.data_loaded = False
            st.session_state.raw_data = None
            st.session_state.summary_data = None
            st.session_state.selected_indices = None  
            st.session_state.filtered_data = None
            st.session_state.filters_applied = False
            st.rerun()
    
    st.markdown('<div class="heading-divider">', unsafe_allow_html=True)
    # determine which data to display
    if st.session_state.filters_applied and st.session_state.filtered_data is not None:
        current_data = st.session_state.filtered_data
        data_type = "Filtered"
    else:
        current_data = st.session_state.summary_data
        data_type = "All"
    
    # display the data summary
    st.markdown(f"## {data_type} Stocks Summary")
    st.markdown('<div class="heading-divider">', unsafe_allow_html=True)
    
    # show the filter status
    if st.session_state.filters_applied:
        if not current_data.empty:
            st.markdown(
                f'<div class="success-banner"> Showing {len(current_data)} filtered stocks (out of {len(st.session_state.summary_data)} total)</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="error-banner"> No stocks found meeting the current criteria (out of {len(st.session_state.summary_data)} total)</div>',
                unsafe_allow_html=True
            )
    
    # show summary stats
    if not current_data.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Stocks", f"{len(current_data):,}")
        with col2:
            avg_price = current_data['Price ($)'].mean()
            st.metric("Avg Price", f"${avg_price:.2f}")
        with col3:
            avg_gap = current_data['Gap (%)'].mean()
            st.metric("Avg Gap", f"{avg_gap:.2f}%")
        with col4:
            total_volume = current_data['Volume'].sum()
            st.metric("Total Volume", f"{total_volume:,.0f}")
        
    # filters section
    st.markdown('<div class="section-divider">', unsafe_allow_html=True)
    st.markdown("## Filters")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Price Range")
        st.markdown('<div class="heading-divider">', unsafe_allow_html=True)
        price_col1, price_col2 = st.columns(2)
        with price_col1:
            price_min = st.number_input("Min Price ($)", min_value=0.01, value=0.1, step=0.1, format="%.2f")
        with price_col2:
            price_max = st.number_input("Max Price ($)", min_value=0.01, value=1000.0, step=1.0, format="%.2f")
    
    with col2:
        st.markdown("##### Volume Requirements")
        st.markdown('<div class="heading-divider">', unsafe_allow_html=True)
        vol_col1, vol_col2 = st.columns(2)
        with vol_col1:
            min_volume = st.number_input(
                "Min Volume", 
                min_value=0, 
                value=1000, 
                step=500,
                help="Minimum current volume"
            )
        with vol_col2:
            min_avg_volume = st.number_input(
                "Min Avg Volume", 
                min_value=0, 
                value=1000, 
                step=500,
                help="Minimum average volume"
            )
    
    st.markdown('<div class="heading-divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### Volatility & Gap")
        st.markdown('<div class="heading-divider">', unsafe_allow_html=True)
        gap_col1, gap_col2 = st.columns(2)
        with gap_col1:
            gap_pct_threshold = st.number_input(
                "Min Gap (%)", 
                min_value=0.0, 
                value=0.01, 
                step=0.1, 
                format="%.2f",
                help="Minimum gap percentage required"
            )
        with gap_col2:
            min_atr = st.number_input(
                "Min ATR", 
                min_value=0.0, 
                value=0.01, 
                step=0.05, 
                format="%.3f",
                help="Minimum Average True Range"
            )
       
    with col2:
        st.markdown("##### Sector Filter")
        st.markdown('<div class="heading-divider">', unsafe_allow_html=True)
        available_sectors = sorted([
            sector for sector in st.session_state.summary_data['Sector'].unique() 
            if sector != 'N/A' and pd.notna(sector)
        ])
        
        if available_sectors:
            selected_sectors = st.multiselect(
                "Select Sectors",
                options=available_sectors,
                help="Choose which sectors to include in the screening"
            )
        else:
            selected_sectors = []
            st.info("No sector data available")
    
    button_col1, button_col2 = st.columns(2)
    with button_col1:
        run_screen = st.button("Apply Filters", type="secondary", use_container_width=True,)
    with button_col2:
        reset_filters = st.button("Reset Filters", type="secondary", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-divider">', unsafe_allow_html=True)

    
    if not current_data.empty:
        # display data table
        display_df = current_data.copy()
        styled_df = apply_gap_styling(display_df)
        st.dataframe(styled_df, use_container_width=True, height=400)

        st.markdown('<div class="section-divider">', unsafe_allow_html=True)

        # top movers tables
        st.markdown("### Top Movers")
        gainers, losers = create_top_movers_tables(current_data)

        if gainers is not None and losers is not None:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Top Gainers")
                if not gainers.empty:
                    st.dataframe(gainers, use_container_width=True, hide_index=True)
                else:
                    st.info("No gainers found")
            
            with col2:
                st.markdown("##### Top Losers")
                if not losers.empty:
                    st.dataframe(losers, use_container_width=True, hide_index=True)
                else:
                    st.info("No losers found")



        # download button for filtered data
        if st.session_state.filters_applied and not current_data.empty:
            csv = current_data.to_csv(index=False)
            st.markdown('<div class="heading-divider">', unsafe_allow_html=True)
            indices_filename = '_'.join(st.session_state.selected_indices).replace(' ', '_')
            st.download_button(
                label=" Download as CSV",
                type="primary",
                data=csv,
                file_name=f"screened_stocks_{indices_filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )

        st.markdown('<div class="section-divider">', unsafe_allow_html=True)

        st.markdown("### Gap Distribution")
        # show the gap chart
        chart_title = f"{data_type} Stocks"
        gap_chart = create_gap_chart(current_data, chart_title)
        if gap_chart:
            st.plotly_chart(gap_chart, use_container_width=True)


    st.markdown('<div class="section-divider">', unsafe_allow_html=True)
    # market anomalies
    st.markdown("### Market Anomalies")
    anomalies = detect_anomalies(current_data)
    if anomalies is not None:
        col1, col2 = st.columns([3, 1])
        with col1:
            anomaly_chart = create_anomaly_chart(anomalies)
            if anomaly_chart:
                st.plotly_chart(anomaly_chart, use_container_width=True)
        with col2:
            st.markdown("##### Detected Anomalies")
            st.dataframe(anomalies[['Ticker', 'Anomaly Type', 'Value']], 
                        use_container_width=True, hide_index=True)
    else:
        st.info("No significant anomalies detected in current dataset")
    
    # handle the filter actions
    if run_screen:
        with st.spinner('Applying filters...'):
            screened_df = screen_stocks(
                st.session_state.summary_data, price_min, price_max, gap_pct_threshold, min_volume, min_avg_volume, min_atr, selected_sectors
            )
            st.session_state.filtered_data = screened_df
            st.session_state.filters_applied = True
            st.rerun()
    
    if reset_filters:
        st.session_state.filtered_data = None
        st.session_state.filters_applied = False
        st.rerun()

def main():
    if not st.session_state.data_loaded:
        configuration_screen()
    else:
        screening_interface()
    
    # footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #6c757d; padding: 1rem;'>"
        "[: Multi-Index Stock Screener :] by Syed Nasiruddin"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == '__main__':
    main()
