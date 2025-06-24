import plotly.graph_objects as go
from utils import format_dataframe

# creates a chart for showcasing the positive and negative gaps  
def create_gap_chart(df, title="Gap Distribution"):
    if df.empty:
        return None
        
    fig = go.Figure()
    
    positive_gaps = df[df['Gap(%)'] > 0]
    negative_gaps = df[df['Gap(%)'] < 0]
    
    if not positive_gaps.empty:
        fig.add_trace(go.Bar(
            x=positive_gaps['Ticker'],
            y=positive_gaps['Gap(%)'],
            name='Gap Up',
            marker_color='#2a9d8f',
            hovertemplate='<b>%{x}</b><br>Gap: %{y:.2f}%<extra></extra>'
        ))
    
    if not negative_gaps.empty:
        fig.add_trace(go.Bar(
            x=negative_gaps['Ticker'],
            y=negative_gaps['Gap(%)'],
            name='Gap Down',
            marker_color='#e74c3c',
            hovertemplate='<b>%{x}</b><br>Gap: %{y:.2f}%<extra></extra>'
        ))
    
    fig.update_layout(
        title=title,
        xaxis_title='Ticker',
        yaxis_title='Gap (%)',
        hovermode='x unified',
        height=400,
        showlegend=True
    )
    
    return fig

# creates the tables for the top movers (highest gainers and highest losers)
def create_top_movers_tables(df):
    
    if df.empty:
        return None, None
    
    df = format_dataframe(df)
    
    # Top gainers (positive gaps)
    gainers = df[df['Gap (%)'] > 0].nlargest(10, 'Gap (%)')
    gainers_display = gainers[['Ticker', 'Price ($)', 'Gap (%)', 'Volume']].copy()
    gainers_display['Gap (%)'] = gainers_display['Gap (%)'].round(2)
    gainers_display['Price ($)'] = gainers_display['Price ($)'].round(2)
    
    # Top losers (negative gaps)
    losers = df[df['Gap (%)'] < 0].nsmallest(10, 'Gap (%)')
    losers_display = losers[['Ticker', 'Price ($)', 'Gap (%)', 'Volume']].copy()
    losers_display['Gap (%)'] = losers_display['Gap (%)'].round(2)
    losers_display['Price ($)'] = losers_display['Price ($)'].round(2)
    
    return gainers_display, losers_display

# creates a chart to showcase the anomalies 
def create_anomaly_chart(anomaly_df):
    if anomaly_df is None or anomaly_df.empty:
        return None
    
    fig = go.Figure()
    
    colors = ['#e74c3c', '#f39c12', '#9b59b6', '#3498db', '#2ecc71']
    
    for i, anomaly_type in enumerate(anomaly_df['Anomaly Type'].unique()):
        data = anomaly_df[anomaly_df['Anomaly Type'] == anomaly_type]
        fig.add_trace(go.Scatter(
            x=data['Ticker'],
            y=data['Z Score'],
            mode='markers',
            marker=dict(
                size=12,
                color=colors[i % len(colors)],
                symbol='star'
            ),
            name=anomaly_type,
            hovertemplate='<b>%{x}</b><br>Z-Score: %{y:.2f}<br>' +
                         '<extra></extra>'
        ))
    
    fig.add_hline(y=2.5, line_dash="dash", line_color="red", annotation_text="Anomaly Threshold")
    
    fig.update_layout(
        xaxis_title='Ticker',
        yaxis_title='Z-Score',
        height=400,
        showlegend=True
    )
    
    return fig
