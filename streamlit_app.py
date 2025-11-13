import streamlit as st
import pandas as pd
import numpy as np
import datetime
from datetime import datetime as dt

# Try to import plotly with fallback
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.error("Plotly is not installed. Please install it using: pip install plotly")

# Page configuration
st.set_page_config(
    page_title="Germany Energy Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .kpi-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin: 2rem 0 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def preprocess_data(df):
    df['utc_timestamp'] = pd.to_datetime(df['utc_timestamp'])
    df = df.sort_values('utc_timestamp')
    df['year'] = df['utc_timestamp'].dt.year
    df['month'] = df['utc_timestamp'].dt.month
    df['date'] = df['utc_timestamp'].dt.date
    return df

def create_dashboard(df):
    df = preprocess_data(df)
    st.markdown('<h1 class="main-header">GERMANY ENERGY INTELLIGENCE DASHBOARD</h1>', unsafe_allow_html=True)

    # Sidebar controls
    st.sidebar.header("🔧 Dashboard Controls")

    min_date, max_date = df['utc_timestamp'].min().date(), df['utc_timestamp'].max().date()
    selected_dates = st.sidebar.date_input("Select Date Range", [min_date, max_date],
                                           min_value=min_date, max_value=max_date)

    if isinstance(selected_dates, tuple) and len(selected_dates) == 2:
        start_date, end_date = selected_dates
    else:
        start_date, end_date = min_date, max_date

    mask = (df['date'] >= start_date) & (df['date'] <= end_date)
    filtered_df = df.loc[mask].copy()

    # Year comparison
    years = sorted(df['year'].unique())
    selected_years = st.sidebar.multiselect("Select Years for Comparison", years, default=[2019, 2020])
    comparison_df = df[df['year'].isin(selected_years)]

    # --- KPIs ---
    st.markdown('<h2 class="section-header">📊 KEY PERFORMANCE INDICATORS</h2>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if all(col in filtered_df for col in ['DE_solar_generation_actual', 'DE_wind_generation_actual', 'DE_load_actual_entsoe_transparency']):
            avg_renewable_share = (
                filtered_df['DE_solar_generation_actual'].sum() +
                filtered_df['DE_wind_generation_actual'].sum()
            ) / filtered_df['DE_load_actual_entsoe_transparency'].sum() * 100
            st.metric("Average Renewable Share", f"{avg_renewable_share:.1f}%", delta=f"{(avg_renewable_share - 25):+.1f}% vs 2025 Target")
        else:
            st.metric("Average Renewable Share", "N/A")

    # Solar utilization
    with col2:
        if 'DE_solar_capacity' in filtered_df:
            solar_util = filtered_df['DE_solar_generation_actual'].mean() / filtered_df['DE_solar_capacity'].max() * 100
            st.metric("Solar Capacity Utilization", f"{solar_util:.1f}%")
        else:
            st.metric("Solar Capacity Utilization", "N/A")

    # Offshore wind
    with col3:
        if all(col in filtered_df for col in ['DE_wind_offshore_capacity', 'DE_wind_capacity']):
            offshore_share = filtered_df['DE_wind_offshore_capacity'].max() / filtered_df['DE_wind_capacity'].max() * 100
            st.metric("Offshore Wind Share", f"{offshore_share:.1f}%")
        else:
            st.metric("Offshore Wind Share", "N/A")

    # Forecast accuracy
    with col4:
        if all(col in filtered_df for col in ['DE_load_actual_entsoe_transparency', 'DE_load_forecast_entsoe_transparency']):
            accuracy = (1 - (abs(filtered_df['DE_load_actual_entsoe_transparency'] -
                                 filtered_df['DE_load_forecast_entsoe_transparency']) /
                             filtered_df['DE_load_actual_entsoe_transparency'])).mean() * 100
            st.metric("Load Forecast Accuracy", f"{accuracy:.1f}%")
        else:
            st.metric("Load Forecast Accuracy", "N/A")

    # --- MAIN CHARTS ---
    st.markdown('<h3 class="section-header">🏭 Energy Generation Mix Over Time</h3>', unsafe_allow_html=True)
    daily_df = (filtered_df
                .set_index('utc_timestamp')
                .resample('D')[['DE_solar_generation_actual', 'DE_wind_generation_actual', 'DE_load_actual_entsoe_transparency']]
                .sum()
                .reset_index())

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=daily_df['utc_timestamp'], y=daily_df['DE_solar_generation_actual'], name='Solar', line=dict(color='#FFD700')))
    fig.add_trace(go.Scatter(x=daily_df['utc_timestamp'], y=daily_df['DE_wind_generation_actual'], name='Wind', line=dict(color='#87CEEB')))
    fig.add_trace(go.Scatter(x=daily_df['utc_timestamp'], y=daily_df['DE_load_actual_entsoe_transparency'], name='Total Load', line=dict(color='#FF6B6B', dash='dash')))
    fig.update_layout(height=400, xaxis_title="Date", yaxis_title="Daily Energy (MWh)", hovermode='x unified')
    st.plotly_chart(fig, use_container_width=True)

    # Capacity vs generation donut charts
    st.markdown('<h3 class="section-header">📈 Capacity vs Generation Profiles</h3>', unsafe_allow_html=True)
    if not filtered_df.empty:
        latest = filtered_df.iloc[-1]
        solar_vals = [latest['DE_solar_generation_actual'], latest['DE_solar_capacity'] - latest['DE_solar_generation_actual']]
        wind_vals = [latest['DE_wind_generation_actual'], latest['DE_wind_capacity'] - latest['DE_wind_generation_actual']]

        pie = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
        pie.add_trace(go.Pie(labels=['Generating', 'Available'], values=solar_vals, name='Solar', marker_colors=['#FFD700', '#FFF4CC']), 1, 1)
        pie.add_trace(go.Pie(labels=['Generating', 'Available'], values=wind_vals, name='Wind', marker_colors=['#87CEEB', '#E0F2FF']), 1, 2)
        pie.update_traces(hole=.4, hoverinfo="label+percent+name")
        pie.update_layout(height=400, annotations=[dict(text='Solar', x=0.18, y=0.5), dict(text='Wind', x=0.82, y=0.5)])
        st.plotly_chart(pie, use_container_width=True)

# Main execution
try:
    # Load data
    df = pd.read_csv("data/time_series_15min_singleindex.csv", parse_dates=["utc_timestamp"])
    df = df.sort_values("utc_timestamp")
    
    # Run the dashboard
    create_dashboard(df)
    
except FileNotFoundError:
    st.error("Data file not found. Please ensure 'data/time_series_15min_singleindex.csv' exists.")
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your data file and ensure all required columns are present.")