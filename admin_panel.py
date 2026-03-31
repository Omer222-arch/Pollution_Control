"""
Admin Panel for User Management
Allows admins to manage users and their roles
"""

import streamlit as st
import pandas as pd
from src.auth.firebase_auth import (
    is_authenticated, is_admin, get_all_users, 
    update_user_role, logout_user
)


def check_admin_access():
    """Check if user is authenticated and is admin"""
    if not st.session_state.get("authenticated", False):
        st.error("Please login first")
        if st.button("Go to Login"):
            st.switch_page("pages/login.py")
        st.stop()
    
    if not is_admin():
        st.error("❌ Access Denied: Admin role required")
        if st.button("Go to Dashboard"):
            st.switch_page("pages/dashboard_authenticated.py")
        st.stop()


def user_management_section():
    """Display user management interface"""
    st.subheader("👥 User Management")
    
    users = get_all_users()
    
    if users:
        # Convert to DataFrame for better display
        user_list = []
        for uid, user_data in users.items():
            user_list.append({
                "UID": uid,
                "Email": user_data.get("email", "N/A"),
                "Full Name": user_data.get("full_name", "N/A"),
                "Role": user_data.get("role", "User"),
                "Created At": user_data.get("created_at", "N/A")
            })
        
        df_users = pd.DataFrame(user_list)
        
        # Display users table
        st.dataframe(df_users, use_container_width=True, key="users_table")
        
        st.markdown("---")
        
        # Update user role
        st.subheader("Update User Role")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            selected_user = st.selectbox(
                "Select User",
                options=[u["Email"] for u in user_list],
                key="user_select"
            )
        
        with col2:
            new_role = st.selectbox(
                "New Role",
                ["User", "Admin"],
                key="role_select"
            )
        
        with col3:
            st.markdown("")  # Spacing
            st.markdown("")
            if st.button("Update Role", use_container_width=True, key="update_btn"):
                # Find UID for selected user
                selected_uid = next(
                    (u["UID"] for u in user_list if u["Email"] == selected_user),
                    None
                )
                if selected_uid:
                    success, message = update_user_role(selected_uid, new_role)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
    else:
        st.info("No users found in the system")


def system_settings_section():
    """Display system settings"""
    st.subheader("⚙️ System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Authentication Settings**")
        st.info("""
        - Firebase Authentication: Enabled ✅
        - Role-Based Access: Enabled ✅
        - Session Management: Enabled ✅
        """)
    
    with col2:
        st.write("**Data Configuration**")
        st.info("""
        - Synthetic Data Generation: Available
        - Model Training: Available
        - Report Generation: Available
        """)
    
    st.markdown("---")
    
    # Danger zone
    st.subheader("⚠️ Danger Zone")
    if st.checkbox("I understand the consequences"):
        if st.button("Clear All User Sessions", key="clear_sessions"):
            st.warning("This feature would clear all active sessions (requires backend implementation)")


def analytics_section():
    """Display admin analytics"""
    st.subheader("📊 Admin Analytics")
    
    users = get_all_users()
    
    if users:
        # Calculate statistics
        total_users = len(users)
        admin_count = sum(1 for u in users.values() if u.get("role") == "Admin")
        user_count = total_users - admin_count
        
        # Display metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Users", total_users)
        with col2:
            st.metric("Admins", admin_count)
        with col3:
            st.metric("Regular Users", user_count)
        
        st.markdown("---")
        
        # Role distribution chart
        st.subheader("Role Distribution")
        role_data = {
            "Role": ["Admin", "User"],
            "Count": [admin_count, user_count]
        }
        df_roles = pd.DataFrame(role_data)
        st.bar_chart(df_roles.set_index("Role"))
    else:
        st.info("No users to analyze")


def main():
    """Main admin panel"""
    st.set_page_config(
        page_title="Admin Panel - Pollution Control",
        page_icon="⚙️",
        layout="wide"
    )
    
    check_admin_access()
    
    # Sidebar
    with st.sidebar:
        st.title("Admin Panel")
        st.markdown("---")
        
        admin_section = st.radio("Select Section:", [
            "User Management",
            "System Settings",
            "Analytics"
        ])
        
        st.markdown("---")
        
        user = st.session_state.get("user", {})
        st.write(f"**Logged in as:** {user.get('email', 'Unknown')}")
        st.write(f"**Role:** `Admin` ⭐")
        
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.success("Logged out successfully!")
            st.switch_page("pages/login.py")
    
    # Main content
    st.title("⚙️ Admin Control Panel")
    
    if admin_section == "User Management":
        user_management_section()
    elif admin_section == "System Settings":
        system_settings_section()
    elif admin_section == "Analytics":
        analytics_section()


if __name__ == "__main__":
    main()
