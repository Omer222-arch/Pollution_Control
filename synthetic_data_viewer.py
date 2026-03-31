"""
Streamlit app to display synthetic pollution and traffic data with month information.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import datetime

# Setup paths
PROJECT_ROOT = Path(__file__).parent
SYNTHETIC_DATA_DIR = PROJECT_ROOT / "src" / "data" / "synthetic"

# Page configuration
st.set_page_config(
    page_title="Synthetic Data Viewer",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def load_synthetic_data():
    """Load and combine synthetic traffic and pollution data."""
    traffic_path = SYNTHETIC_DATA_DIR / "synthetic_traffic_data.csv"
    pollution_path = SYNTHETIC_DATA_DIR / "synthetic_pollution_data.csv"
    
    # Load data
    traffic_df = pd.read_csv(traffic_path)
    pollution_df = pd.read_csv(pollution_path)
    
    # Convert timestamp to datetime
    traffic_df['timestamp'] = pd.to_datetime(traffic_df['timestamp'])
    pollution_df['timestamp'] = pd.to_datetime(pollution_df['timestamp'])
    
    # Extract month information
    traffic_df['month'] = traffic_df['timestamp'].dt.month
    traffic_df['month_name'] = traffic_df['timestamp'].dt.strftime('%B')
    traffic_df['date'] = traffic_df['timestamp'].dt.date
    traffic_df['hour'] = traffic_df['timestamp'].dt.hour
    
    pollution_df['month'] = pollution_df['timestamp'].dt.month
    pollution_df['month_name'] = pollution_df['timestamp'].dt.strftime('%B')
    pollution_df['date'] = pollution_df['timestamp'].dt.date
    pollution_df['hour'] = pollution_df['timestamp'].dt.hour
    
    # Merge both datasets
    combined_df = pd.merge(
        traffic_df,
        pollution_df,
        on=['timestamp', 'month', 'month_name', 'date', 'hour'],
        how='inner'
    )
    
    # Reorder columns for better visibility
    column_order = [
        'timestamp', 'date', 'hour', 'month', 'month_name',
        'two_wheelers', 'cars', 'buses', 'trucks',
        'PM2.5', 'PM10', 'NO2', 'CO'
    ]
    combined_df = combined_df[column_order]
    
    return traffic_df, pollution_df, combined_df

# Load data
traffic_df, pollution_df, combined_df = load_synthetic_data()

# Sidebar
st.sidebar.title("⚙️ Options")
view_mode = st.sidebar.radio(
    "Select View:",
    ["Combined Data", "Traffic Data Only", "Pollution Data Only", "Summary Statistics"]
)

selected_month = st.sidebar.multiselect(
    "Filter by Month:",
    options=sorted(combined_df['month_name'].unique()),
    default=sorted(combined_df['month_name'].unique())
)

# Main content
st.title("📊 Synthetic Data Viewer")
st.markdown("Explore the synthetic traffic and air quality data with month information.")

# Apply month filter
if selected_month:
    display_data = combined_df[combined_df['month_name'].isin(selected_month)]
else:
    display_data = combined_df

# Display based on selected view
if view_mode == "Combined Data":
    st.subheader("Combined Traffic & Pollution Data")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Records", len(display_data))
    with col2:
        st.metric("Date Range", f"{display_data['date'].min()} to {display_data['date'].max()}")
    with col3:
        st.metric("Months Covered", display_data['month_name'].nunique())
    
    st.markdown("---")
    
    # Display data with pagination
    rows_per_page = st.slider("Rows per page:", 10, 500, 100)
    total_pages = (len(display_data) + rows_per_page - 1) // rows_per_page
    
    if total_pages > 0:
        page = st.number_input("Page:", 1, total_pages, 1) - 1
        start_idx = page * rows_per_page
        end_idx = start_idx + rows_per_page
        
        st.dataframe(
            display_data.iloc[start_idx:end_idx],
            use_container_width=True,
            height=600
        )
        
        st.caption(f"Showing rows {start_idx + 1} to {min(end_idx, len(display_data))} of {len(display_data)}")
    
    # Download button
    csv_data = display_data.to_csv(index=False)
    st.download_button(
        label="📥 Download Combined Data as CSV",
        data=csv_data,
        file_name=f"synthetic_combined_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

elif view_mode == "Traffic Data Only":
    st.subheader("Traffic Data")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg Two-Wheelers", f"{display_data['two_wheelers'].mean():.0f}")
    with col2:
        st.metric("Avg Cars", f"{display_data['cars'].mean():.0f}")
    with col3:
        st.metric("Avg Buses", f"{display_data['buses'].mean():.0f}")
    with col4:
        st.metric("Avg Trucks", f"{display_data['trucks'].mean():.0f}")
    
    st.markdown("---")
    
    traffic_display = display_data[['timestamp', 'date', 'hour', 'month', 'month_name', 'two_wheelers', 'cars', 'buses', 'trucks']]
    st.dataframe(traffic_display, use_container_width=True, height=600)
    
    csv_data = traffic_display.to_csv(index=False)
    st.download_button(
        label="📥 Download Traffic Data as CSV",
        data=csv_data,
        file_name=f"synthetic_traffic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

elif view_mode == "Pollution Data Only":
    st.subheader("Pollution Data")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Avg PM2.5", f"{display_data['PM2.5'].mean():.2f} μg/m³")
    with col2:
        st.metric("Avg PM10", f"{display_data['PM10'].mean():.2f} μg/m³")
    with col3:
        st.metric("Avg NO2", f"{display_data['NO2'].mean():.2f} μg/m³")
    with col4:
        st.metric("Avg CO", f"{display_data['CO'].mean():.2f} μg/m³")
    
    st.markdown("---")
    
    pollution_display = display_data[['timestamp', 'date', 'hour', 'month', 'month_name', 'PM2.5', 'PM10', 'NO2', 'CO']]
    st.dataframe(pollution_display, use_container_width=True, height=600)
    
    csv_data = pollution_display.to_csv(index=False)
    st.download_button(
        label="📥 Download Pollution Data as CSV",
        data=csv_data,
        file_name=f"synthetic_pollution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

elif view_mode == "Summary Statistics":
    st.subheader("Summary Statistics by Month")
    
    # Traffic statistics by month
    st.markdown("#### Traffic Statistics by Month")
    traffic_stats = display_data.groupby('month_name')[['two_wheelers', 'cars', 'buses', 'trucks']].agg(['mean', 'min', 'max', 'std'])
    st.dataframe(traffic_stats, use_container_width=True)
    
    # Pollution statistics by month
    st.markdown("#### Pollution Statistics by Month (μg/m³)")
    pollution_stats = display_data.groupby('month_name')[['PM2.5', 'PM10', 'NO2', 'CO']].agg(['mean', 'min', 'max', 'std'])
    st.dataframe(pollution_stats, use_container_width=True)
    
    # Hourly patterns
    st.markdown("#### Hourly Patterns (Averaged across all days)")
    hourly_data = display_data.groupby('hour')[['two_wheelers', 'cars', 'buses', 'trucks', 'PM2.5', 'PM10', 'NO2', 'CO']].mean()
    
    col1, col2 = st.columns(2)
    with col1:
        st.line_chart(hourly_data[['two_wheelers', 'cars', 'buses', 'trucks']], use_container_width=True)
        st.caption("Vehicle Count by Hour")
    
    with col2:
        st.line_chart(hourly_data[['PM2.5', 'PM10', 'NO2', 'CO']], use_container_width=True)
        st.caption("Pollution Levels by Hour")

# Footer
st.markdown("---")
st.caption("💡 Tip: Use the month filter in the sidebar to focus on specific months. Select 'Combined Data' to view all columns together.")
