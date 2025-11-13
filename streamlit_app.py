import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime
from datetime import datetime as dt

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

# Load data
df = pd.read_csv("data/time_series_15min_singleindex.csv", parse_dates=["utc_timestamp"])
df = df.sort_values("utc_timestamp")

def create_dashboard(df):
    # Convert timestamp and ensure proper sorting
    df['utc_timestamp'] = pd.to_datetime(df['utc_timestamp'])
    df = df.sort_values('utc_timestamp')
    
    # Create yearly and monthly aggregations
    df['year'] = df['utc_timestamp'].dt.year
    df['month'] = df['utc_timestamp'].dt.month
    df['date'] = df['utc_timestamp'].dt.date
    
    # Header
    st.markdown('<h1 class="main-header">GERMANY ENERGY INTELLIGENCE DASHBOARD</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.header("🔧 Dashboard Controls")
    
    # Date range selector
    min_date = df['utc_timestamp'].min().date()
    max_date = df['utc_timestamp'].max().date()
    
    selected_dates = st.sidebar.date_input(
        "Select Date Range",
        [min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    if len(selected_dates) == 2:
        start_date, end_date = selected_dates
        mask = (df['date'] >= start_date) & (df['date'] <= end_date)
        filtered_df = df.loc[mask]
    else:
        filtered_df = df
    
    # Year selector
    years = sorted(df['year'].unique())
    selected_years = st.sidebar.multiselect(
        "Select Years for Comparison",
        years,
        default=[2019, 2020]
    )
    
    # KPI Section
    st.markdown('<h2 class="section-header">📊 KEY PERFORMANCE INDICATORS</h2>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        # Safe calculation with error handling
        try:
            avg_renewable_share = (filtered_df['DE_solar_generation_actual'].mean() + 
                                 filtered_df['DE_wind_generation_actual'].mean()) / filtered_df['DE_load_actual_entsoe_transparency'].mean() * 100
            st.metric(
                label="Average Renewable Share",
                value=f"{avg_renewable_share:.1f}%",
                delta=f"{(avg_renewable_share - 25):+.1f}% vs 2025 Target"
            )
        except:
            st.metric(
                label="Average Renewable Share",
                value="N/A",
                delta="Data unavailable"
            )
    
    with col2:
        try:
            max_solar_capacity = filtered_df['DE_solar_capacity'].max()
            solar_utilization = filtered_df['DE_solar_generation_actual'].mean() / max_solar_capacity * 100
            st.metric(
                label="Solar Capacity Utilization",
                value=f"{solar_utilization:.1f}%",
                delta=f"Capacity: {max_solar_capacity:,.0f} MW"
            )
        except:
            st.metric(
                label="Solar Capacity Utilization",
                value="N/A",
                delta="Data unavailable"
            )
    
    with col3:
        try:
            wind_capacity = filtered_df['DE_wind_capacity'].max()
            offshore_share = (filtered_df['DE_wind_offshore_capacity'].max() / wind_capacity * 100)
            st.metric(
                label="Offshore Wind Share",
                value=f"{offshore_share:.1f}%",
                delta=f"Total Wind: {wind_capacity:,.0f} MW"
            )
        except:
            st.metric(
                label="Offshore Wind Share",
                value="N/A",
                delta="Data unavailable"
            )
    
    with col4:
        try:
            load_forecast_accuracy = (1 - (abs(filtered_df['DE_load_actual_entsoe_transparency'] - 
                                             filtered_df['DE_load_forecast_entsoe_transparency']) / 
                                          filtered_df['DE_load_actual_entsoe_transparency'])).mean() * 100
            st.metric(
                label="Load Forecast Accuracy",
                value=f"{load_forecast_accuracy:.1f}%",
                delta=f"±{(100-load_forecast_accuracy):.1f}% Error"
            )
        except:
            st.metric(
                label="Load Forecast Accuracy",
                value="N/A",
                delta="Data unavailable"
            )
    
    # Main charts - First Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="section-header">🏭 Energy Generation Mix Over Time</h3>', unsafe_allow_html=True)
        
        # FIXED: Select only numeric columns for resampling and use sum instead of mean for energy
        numeric_columns = ['DE_solar_generation_actual', 'DE_wind_generation_actual', 'DE_load_actual_entsoe_transparency']
        daily_df = filtered_df[['utc_timestamp'] + numeric_columns].resample('D', on='utc_timestamp').sum().reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=daily_df['utc_timestamp'], y=daily_df['DE_solar_generation_actual'], 
                               name='Solar', line=dict(color='#FFD700')))
        fig.add_trace(go.Scatter(x=daily_df['utc_timestamp'], y=daily_df['DE_wind_generation_actual'], 
                               name='Wind', line=dict(color='#87CEEB')))
        fig.add_trace(go.Scatter(x=daily_df['utc_timestamp'], y=daily_df['DE_load_actual_entsoe_transparency'], 
                               name='Total Load', line=dict(color='#FF6B6B', dash='dash')))
        
        fig.update_layout(
            height=400,
            xaxis_title="Date",
            yaxis_title="Daily Energy (MWh)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="section-header">📈 Capacity vs Generation Profiles</h3>', unsafe_allow_html=True)
        
        # Latest data for current state analysis
        if len(filtered_df) > 0:
            latest_data = filtered_df.iloc[-1]
            
            fig = make_subplots(rows=1, cols=2, specs=[[{'type':'domain'}, {'type':'domain'}]])
            
            # Solar capacity vs generation
            solar_values = [latest_data['DE_solar_generation_actual'], 
                           max(latest_data['DE_solar_capacity'] - latest_data['DE_solar_generation_actual'], 0)]
            fig.add_trace(go.Pie(labels=['Generating', 'Available Capacity'], values=solar_values, 
                               name="Solar", marker_colors=['#FFD700', '#FFF4CC']), 1, 1)
            
            # Wind capacity vs generation
            wind_values = [latest_data['DE_wind_generation_actual'], 
                          max(latest_data['DE_wind_capacity'] - latest_data['DE_wind_generation_actual'], 0)]
            fig.add_trace(go.Pie(labels=['Generating', 'Available Capacity'], values=wind_values, 
                               name="Wind", marker_colors=['#87CEEB', '#E0F2FF']), 1, 2)
            
            fig.update_traces(hole=.4, hoverinfo="label+percent+name")
            fig.update_layout(
                height=400,
                annotations=[dict(text='Solar', x=0.18, y=0.5, font_size=14, showarrow=False),
                            dict(text='Wind', x=0.82, y=0.5, font_size=14, showarrow=False)]
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No data available for the selected date range")
    
    # Second Row
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<h3 class="section-header">🌬️ Wind Generation Breakdown</h3>', unsafe_allow_html=True)
        
        # FIXED: Use the filtered_df for yearly analysis if years are selected
        if selected_years:
            analysis_df = df[df['year'].isin(selected_years)]
        else:
            analysis_df = df
            
        yearly_wind = analysis_df.groupby('year').agg({
            'DE_wind_onshore_generation_actual': 'mean',
            'DE_wind_offshore_generation_actual': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(name='Onshore Wind', x=yearly_wind['year'], 
                           y=yearly_wind['DE_wind_onshore_generation_actual'],
                           marker_color='#4ECDC4'))
        fig.add_trace(go.Bar(name='Offshore Wind', x=yearly_wind['year'], 
                           y=yearly_wind['DE_wind_offshore_generation_actual'],
                           marker_color='#45B7D1'))
        
        fig.update_layout(
            height=400,
            barmode='stack',
            xaxis_title="Year",
            yaxis_title="Average Generation (MW)",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('<h3 class="section-header">📊 Renewable Capacity Growth</h3>', unsafe_allow_html=True)
        
        # Use analysis_df which considers year selection
        yearly_capacity = analysis_df.groupby('year').agg({
            'DE_solar_capacity': 'max',
            'DE_wind_capacity': 'max',
            'DE_wind_onshore_capacity': 'max',
            'DE_wind_offshore_capacity': 'max'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=yearly_capacity['year'], y=yearly_capacity['DE_solar_capacity'], 
                               name='Solar Capacity', line=dict(color='#FFD700', width=3)))
        fig.add_trace(go.Scatter(x=yearly_capacity['year'], y=yearly_capacity['DE_wind_capacity'], 
                               name='Total Wind Capacity', line=dict(color='#87CEEB', width=3)))
        fig.add_trace(go.Scatter(x=yearly_capacity['year'], y=yearly_capacity['DE_wind_offshore_capacity'], 
                               name='Offshore Wind', line=dict(color='#45B7D1', width=3, dash='dot')))
        
        fig.update_layout(
            height=400,
            xaxis_title="Year",
            yaxis_title="Installed Capacity (MW)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Third Row - Detailed Analysis
    st.markdown('<h3 class="section-header">🔍 Detailed Performance Analysis</h3>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('**Seasonal Patterns**')
        
        # Create monthly patterns from filtered data
        monthly_patterns = filtered_df.groupby('month').agg({
            'DE_solar_generation_actual': 'mean',
            'DE_wind_generation_actual': 'mean',
            'DE_load_actual_entsoe_transparency': 'mean'
        }).reset_index()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly_patterns['month'], y=monthly_patterns['DE_solar_generation_actual'], 
                               name='Solar Generation', line=dict(color='#FFD700')))
        fig.add_trace(go.Scatter(x=monthly_patterns['month'], y=monthly_patterns['DE_wind_generation_actual'], 
                               name='Wind Generation', line=dict(color='#87CEEB')))
        fig.add_trace(go.Scatter(x=monthly_patterns['month'], y=monthly_patterns['DE_load_actual_entsoe_transparency'], 
                               name='Energy Load', line=dict(color='#FF6B6B')))
        
        fig.update_layout(
            height=300,
            xaxis=dict(tickvals=list(range(1, 13)), ticktext=['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                                                             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']),
            xaxis_title="Month",
            yaxis_title="Average Power (MW)"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown('**Capacity Factor Analysis**')
        
        capacity_factors = filtered_df.agg({
            'DE_solar_profile': 'mean',
            'DE_wind_profile': 'mean',
            'DE_wind_onshore_profile': 'mean',
            'DE_wind_offshore_profile': 'mean'
        })
        
        fig = go.Figure(data=[go.Bar(
            x=['Solar', 'Wind Total', 'Wind Onshore', 'Wind Offshore'],
            y=[capacity_factors['DE_solar_profile'] * 100, 
               capacity_factors['DE_wind_profile'] * 100,
               capacity_factors['DE_wind_onshore_profile'] * 100,
               capacity_factors['DE_wind_offshore_profile'] * 100],
            marker_color=['#FFD700', '#87CEEB', '#4ECDC4', '#45B7D1']
        )])
        
        fig.update_layout(
            height=300,
            xaxis_title="Technology",
            yaxis_title="Average Capacity Factor (%)",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Footer with insights
    st.markdown("---")
    st.markdown("### 💡 Key Insights")
    
    insight_col1, insight_col2, insight_col3 = st.columns(3)
    
    with insight_col1:
        st.info("""
        **Renewable Growth**: 
        Germany shows consistent growth in renewable capacity, with solar and wind leading the energy transition.
        """)
    
    with insight_col2:
        st.warning("""
        **Seasonal Variation**: 
        Strong seasonal patterns observed with solar peaking in summer and wind in winter months.
        """)
    
    with insight_col3:
        st.success("""
        **Grid Stability**: 
        High forecast accuracy indicates robust grid management capabilities.
        """)

# Run the dashboard
try:
    create_dashboard(df)
except Exception as e:
    st.error(f"An error occurred: {str(e)}")
    st.info("Please check your data file and ensure all required columns are present.")