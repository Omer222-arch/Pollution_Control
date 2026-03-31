"""
Login Page for Role-Based Authentication
Handles user authentication with Firebase
"""

import streamlit as st
import pandas as pd
from src.auth.firebase_auth import (
    register_user, login_user, logout_user, 
    is_authenticated, get_user_role, initialize_firebase,
    check_firebase_config
)


def init_session_state():
    """Initialize session state variables"""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user_role" not in st.session_state:
        st.session_state.user_role = "Guest"
    if "user" not in st.session_state:
        st.session_state.user = None


def show_setup_warning():
    """Show setup instructions if Firebase not configured"""
    st.error("⚠️ Firebase Configuration Missing!")
    st.markdown("""
    Your Firebase credentials are not configured. Please follow these steps:
    
    ### Setup Instructions:
    
    1. **Create Firebase Project**
       - Go to [Firebase Console](https://console.firebase.google.com)
       - Click "Add Project"
       - Follow the setup wizard
    
    2. **Enable Authentication**
       - In Firebase Console, go to **Build > Authentication**
       - Click **Get Started**
       - Enable **Email/Password** provider
    
    3. **Create Realtime Database**
       - Go to **Build > Realtime Database**
       - Click **Create Database**
       - Choose location and start in Test Mode
    
    4. **Get Your Credentials**
       - Go to **Project Settings** (gear icon)
       - Copy your credentials:
         - Project ID
         - Web API Key
         - Auth Domain
         - Database URL
    
    5. **Update `.streamlit/secrets.toml`**
       
       Edit: `D:\\pollution_control\\.streamlit\\secrets.toml`
       
       ```toml
       FIREBASE_API_KEY = "AIzaSyAP2SUtOPOm-yiZwiVYmH7_b_KrbihTcAg"
       FIREBASE_AUTH_DOMAIN = "pollutioncontrol-745a5.firebaseapp.com"
       FIREBASE_PROJECT_ID = "pollutioncontrol-745a5"
       FIREBASE_STORAGE_BUCKET = "pollutioncontrol-745a5.firebasestorage.app"
       FIREBASE_MESSAGING_SENDER_ID = "804276061581"
       FIREBASE_APP_ID = "1:804276061581:web:50d4bc24589589f09529c4"
       FIREBASE_DATABASE_URL = "https://pollutioncontrol-745a5-default-rtdb.firebaseio.com"
       ```
    
    6. **Restart Streamlit**
       ```bash
       streamlit run login.py
       ```
    
    **Need help?** Read: `FIREBASE_SETUP_GUIDE.md`
    """)
    
    if st.button("🔄 Reload After Updating Secrets"):
        st.rerun()


def login_page():
    """Display login/registration page"""
    init_session_state()
    
    # Check Firebase configuration
    is_configured, missing_keys = check_firebase_config()
    
    if not is_configured:
        show_setup_warning()
        st.stop()
    
    st.set_page_config(
        page_title="Pollution Control - Login",
        page_icon="🔐",
        layout="centered"
    )
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("# 🔒 Pollution Control Dashboard")
        st.markdown("### Vehicular Emission Analysis System")
        
        # Tab selection for Login/Register
        tab1, tab2 = st.tabs(["Login", "Register"])
        
        with tab1:
            st.subheader("Login")
            login_email = st.text_input("Email", key="login_email")
            login_password = st.text_input("Password", type="password", key="login_password")
            
            col_login1, col_login2 = st.columns(2)
            
            with col_login1:
                if st.button("Login", use_container_width=True, key="btn_login"):
                    if not login_email or not login_password:
                        st.error("Please enter both email and password")
                    else:
                        with st.spinner("Logging in..."):
                            success, message, user_data = login_user(login_email, login_password)
                            
                            if success:
                                # Store user info in session
                                st.session_state.authenticated = True
                                st.session_state.user = user_data
                                st.session_state.user_role = user_data.get("role", "User")
                                st.success(message)
                                st.balloons()
                                st.rerun()
                            else:
                                st.error(message)
            
            with col_login2:
                st.markdown("")  # Spacing
                st.markdown("")
                if st.button("Demo Login", use_container_width=True, help="Login with demo credentials"):
                    st.info("Demo login for testing (use actual Firebase credentials for production)")
        
        with tab2:
            st.subheader("Create New Account")
            reg_email = st.text_input("Email", key="reg_email")
            reg_password = st.text_input("Password (min 6 chars)", type="password", key="reg_password")
            reg_confirm = st.text_input("Confirm Password", type="password", key="reg_confirm")
            reg_name = st.text_input("Full Name", key="reg_name")
            
            reg_role = st.radio(
                "Account Type",
                ["User", "Admin"],
                horizontal=True,
                help="User: View and analyze data. Admin: Manage users and all features."
            )
            
            # Show role explanation
            if reg_role == "Admin":
                st.info("✨ **Admin Account** - Full system access including user management")
            else:
                st.info("👤 **User Account** - Data viewing and analysis access")
            
            col_reg1, col_reg2 = st.columns(2)
            
            with col_reg1:
                if st.button("Register", use_container_width=True, key="btn_register"):
                    if not all([reg_email, reg_password, reg_confirm, reg_name]):
                        st.error("Please fill all fields")
                    elif reg_password != reg_confirm:
                        st.error("Passwords do not match")
                    elif len(reg_password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        with st.spinner("Creating account..."):
                            success, message = register_user(
                                reg_email, reg_password, reg_name, reg_role
                            )
                            if success:
                                st.success(f"✅ {message}")
                                st.info(f"🎓 Account created as: **{reg_role}**")
                                st.info("👉 Switch to the Login tab and login with your new account")
                            else:
                                st.error(message)
        
        st.markdown("---")
        
        # Information section
        st.markdown("""
        ### 📋 Account Types
        
        **👤 User Account**
        - View dashboard and visualizations
        - Explore pollution data
        - Download reports
        
        **👨‍💼 Admin Account**
        - All User features
        - Manage user accounts
        - Configure system settings
        - Access advanced analytics
        """)


def main():
    """Main entry point"""
    init_session_state()
    
    if not is_authenticated():
        login_page()
    else:
        # Redirect to main dashboard
        st.switch_page("pages/dashboard.py")


if __name__ == "__main__":
    main()
