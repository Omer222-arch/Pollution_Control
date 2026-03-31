"""
Home Page - Welcome to Pollution Control Dashboard
"""

import streamlit as st
from src.auth.firebase_auth import is_authenticated


def main():
    """Home page for the application"""
    
    st.set_page_config(
        page_title="Pollution Control Dashboard",
        page_icon="🌍",
        layout="wide"
    )
    
    # Header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# 🌍 Vehicular Pollution Control Dashboard")
        st.markdown("### Comprehensive Air Quality Analysis System")
    
    st.markdown("---")
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ## Welcome! 👋
        
        This is a sophisticated system for analyzing vehicular emissions and their 
        contribution to air pollution. Our dashboard provides real-time insights into 
        pollution data, predictive modeling, and visualization tools.
        
        ### 🎯 What We Offer
        
        **📊 Data Analysis**
        - Comprehensive pollution data exploration
        - Traffic pattern analysis
        - Emission source tracking
        
        **🤖 Machine Learning Models**
        - Multiple model types for accurate predictions
        - Pollutant concentration forecasting
        - Contributing factor analysis
        
        **📈 Advanced Analytics**
        - SHAP-based explainability
        - Contribution analysis
        - Trend identification
        
        **🔒 Secure Access**
        - Role-based authentication
        - User and Admin profiles
        - Secure data management
        """)
    
    with col2:
        st.markdown("### Quick Actions")
        
        if is_authenticated():
            st.success("✅ You are logged in!")
            col_dash, col_admin = st.columns(1)
            with col_dash:
                if st.button("📊 Go to Dashboard", use_container_width=True):
                    st.switch_page("pages/dashboard.py")
            
            # Check if admin
            user_role = st.session_state.get("user_role", "User")
            if user_role == "Admin":
                with col_admin:
                    if st.button("⚙️ Admin Panel", use_container_width=True):
                        st.switch_page("pages/admin_panel.py")
        else:
            st.info("📝 Not logged in yet")
            col_login, col_register = st.columns(1)
            with col_login:
                if st.button("🔐 Login", use_container_width=True, key="btn_home_login"):
                    st.switch_page("pages/login.py")
    
    st.markdown("---")
    
    # Statistics section
    st.subheader("📊 System Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Pollutants Tracked", 4, help="PM2.5, PM10, NO2, CO")
    
    with col2:
        st.metric("Model Types", 5, help="Linear, Ridge, Lasso, XGBoost, Random Forest")
    
    with col3:
        st.metric("Data Sources", 2, help="Synthetic traffic and pollution data")
    
    with col4:
        st.metric("User Roles", 2, help="Admin, User")
    
    st.markdown("---")
    
    # Features table
    st.subheader("👤 Account Types & Features")
    
    features_data = {
        "Feature": [
            "View Dashboard",
            "Data Explorer",
            "Model Metrics",
            "Visualizations",
            "Download Reports",
            "User Management",
            "System Settings",
            "Advanced Analytics"
        ],
        "👤 User": ["✅", "✅", "✅", "✅", "✅", "❌", "❌", "❌"],
        "👨‍💼 Admin": ["✅", "✅", "✅", "✅", "✅", "✅", "✅", "✅"]
    }
    
    import pandas as pd
    df_features = pd.DataFrame(features_data)
    st.table(df_features)
    
    st.markdown("---")
    
    # Footer with info
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **System Status:** ✅ Operational
        
        **Version:** 1.0.0
        """)
    
    with col2:
        st.markdown("""
        **Authentication:** Firebase
        
        **Database:** Realtime Database
        """)
    
    with col3:
        st.markdown("""
        **Last Updated:** 2026-03-11
        
        **Support:** Firebase Docs
        """)


if __name__ == "__main__":
    main()
