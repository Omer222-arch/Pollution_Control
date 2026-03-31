"""
Updated Dashboard with Authentication
Main entry point for the Pollution Control Dashboard
"""

import streamlit as st
import pandas as pd
import os
from pathlib import Path
from src.auth.firebase_auth import (
    is_authenticated, get_user_role, logout_user, is_admin
)

# Setup paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data" / "synthetic"
RESULTS_DIR = PROJECT_ROOT / "models" / "results"
FIGURES_DIR = PROJECT_ROOT / "outputs" / "figures"
POLLUTANTS = ['PM2.5', 'PM10', 'NO2', 'CO']


def init_session():
    """Initialize session state"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False


def check_authentication():
    """Check if user is authenticated, redirect to login if not"""
    init_session()
    
    if not st.session_state.get("authenticated", False):
        st.error("Please login first")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Go to Login", use_container_width=True):
                st.switch_page("pages/login.py")
        with col2:
            if st.button("Go Home", use_container_width=True):
                st.switch_page("pages/home.py")
        st.stop()


def load_csv(path):
    """Load CSV file safely"""
    if os.path.exists(path):
        return pd.read_csv(path)
    return None


def render_sidebar():
    """Render sidebar with user info and navigation"""
    with st.sidebar:
        st.markdown("---")
        st.subheader("👤 User Profile")
        
        user = st.session_state.get("user", {})
        user_role = st.session_state.get("user_role", "Guest")
        
        st.write(f"**Email:** {user.get('email', 'Unknown')}")
        st.write(f"**Role:** `{user_role}`")
        
        st.markdown("---")
        
        # Navigation
        st.subheader("📍 Navigation")
        
        page = st.radio("Go to:", [
            "Overview & Run Pipeline", 
            "Data Explorer", 
            "Model Evaluation Metrics", 
            "Visualizations"
        ], key="main_nav")
        
        # Admin section
        if is_admin():
            st.markdown("---")
            st.subheader("⚙️ Admin Panel")
            admin_section = st.radio("Admin Tools:", [
                "User Management",
                "System Settings",
                "Analytics"
            ], key="admin_nav")
        
        st.markdown("---")
        if st.button("🚪 Logout", use_container_width=True, key="logout_btn"):
            logout_user()
            st.success("Logged out successfully!")
            st.switch_page("pages/login.py")
        
        return page


def main():
    """Main dashboard"""
    check_authentication()
    
    # Configure page
    st.set_page_config(
        page_title="Vehicular Pollution Estimation Pipeline Dashboard",
        page_icon="🌍",
        layout="wide"
    )
    
    page = render_sidebar()

    if page == "Overview & Run Pipeline":
        st.title("🌍 Vehicular Pollution Estimation Dashboard")
        st.markdown("""
        Welcome to the **Vehicular Pollution Estimation Pipeline Dashboard**!
        This system analyzes vehicular emissions and their contribution to air pollution.
        
        ### 📊 Key Features
        - **Real-time Data Analysis**: Process and analyze pollution data
        - **Machine Learning Models**: Multiple model types for accurate predictions
        - **Advanced Visualizations**: Interactive charts and analysis reports
        - **Role-Based Access**: Secure access control with Admin and User roles
        """)
        
        # Display Key Numerical Values
        st.subheader("📊 Key Numerical Metrics (Best R² per Pollutant)")
        metrics_cols = st.columns(len(POLLUTANTS))
        for i, pollutant in enumerate(POLLUTANTS):
            with metrics_cols[i]:
                comp_path = RESULTS_DIR / pollutant / "model_comparison.csv"
                comp_df = load_csv(comp_path)
                if comp_df is not None:
                    best_r2 = comp_df['R² Score'].max()
                    best_model = comp_df.loc[comp_df['R² Score'].idxmax(), 'Model']
                    st.metric(f"{pollutant} - {best_model}", f"{best_r2:.4f}")
                else:
                    st.warning(f"No data for {pollutant}")
        
        # Pipeline status
        st.subheader("🔄 Pipeline Status")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if os.path.exists(DATA_DIR / "synthetic_pollution_data.csv"):
                st.info("✅ Synthetic Data Generated")
            else:
                st.warning("⏳ Synthetic Data Pending")
        
        with col2:
            if os.path.exists(Path(__file__).parent / "models" / "saved_models"):
                st.info("✅ Models Trained")
            else:
                st.warning("⏳ Model Training Pending")
        
        with col3:
            if os.path.exists(RESULTS_DIR):
                st.info("✅ Evaluation Complete")
            else:
                st.warning("⏳ Evaluation Pending")
    
    elif page == "Data Explorer":
        st.title("📈 Data Explorer")
        
        pollutant = st.selectbox("Select Pollutant:", POLLUTANTS)
        
        # Load and display data
        pollution_path = DATA_DIR / "synthetic_pollution_data.csv"
        traffic_path = DATA_DIR / "synthetic_traffic_data.csv"
        
        if os.path.exists(pollution_path):
            df = pd.read_csv(pollution_path)
            if 'Pollutant' in df.columns:
                pollutant_data = df[df['Pollutant'] == pollutant]
                st.dataframe(pollutant_data, use_container_width=True)
                
                # Statistics
                st.subheader("📊 Statistics")
                st.write(pollutant_data.describe())
            else:
                st.write(df.head(100))
        else:
            st.warning(f"Data file not found: {pollution_path}")
    
    elif page == "Model Evaluation Metrics":
        st.title("📉 Model Evaluation Metrics")
        
        pollutant = st.selectbox("Select Pollutant:", POLLUTANTS, key="eval_pollutant")
        
        comp_path = RESULTS_DIR / pollutant / "model_comparison.csv"
        comp_df = load_csv(comp_path)
        
        if comp_df is not None:
            st.subheader(f"Model Comparison - {pollutant}")
            st.dataframe(comp_df, use_container_width=True)
            
            # Visualization
            try:
                import matplotlib.pyplot as plt
                fig, axes = plt.subplots(1, 2, figsize=(12, 5))
                
                axes[0].barh(comp_df['Model'], comp_df['R² Score'])
                axes[0].set_xlabel('R² Score')
                axes[0].set_title(f'R² Scores - {pollutant}')
                
                axes[1].barh(comp_df['Model'], comp_df['RMSE'])
                axes[1].set_xlabel('RMSE')
                axes[1].set_title(f'RMSE - {pollutant}')
                
                st.pyplot(fig)
            except:
                st.info("Visualization not available")
        else:
            st.warning(f"No evaluation data for {pollutant}")
    
    elif page == "Visualizations":
        st.title("📊 Visualizations")
        
        fig_path = FIGURES_DIR / POLLUTANTS[0]
        if os.path.exists(fig_path):
            images = list(fig_path.glob("*.png"))
            if images:
                st.subheader(f"Generated Plots - {POLLUTANTS[0]}")
                for img_file in images[:5]:  # Show first 5 images
                    st.image(str(img_file), use_column_width=True)
            else:
                st.info("No visualizations available yet")
        else:
            st.info("Figures directory not found")


if __name__ == "__main__":
    main()
