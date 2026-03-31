#!/usr/bin/env python3
"""
Admin Role Verification Script
Tests if admin role functionality is working correctly
"""

import sys
from pathlib import Path

def check_admin_role_setup():
    """Check if admin role setup is correct"""
    
    print("\n" + "="*70)
    print("🔐 Admin Role Verification")
    print("="*70 + "\n")
    
    checks_passed = 0
    checks_total = 0
    
    # Check 1: Firebase auth module
    print("1️⃣  Checking Firebase authentication module...")
    checks_total += 1
    try:
        from src.auth.firebase_auth import (
            register_user, login_user, is_admin, 
            get_user_role, initialize_firebase
        )
        print("   ✅ Firebase auth module loaded successfully\n")
        checks_passed += 1
    except ImportError as e:
        print(f"   ❌ Failed to import: {e}\n")
    
    # Check 2: Streamlit secrets
    print("2️⃣  Checking Streamlit secrets configuration...")
    checks_total += 1
    try:
        import streamlit as st
        secrets_file = Path(".streamlit/secrets.toml")
        if secrets_file.exists():
            print(f"   ✅ Secrets file found: {secrets_file}\n")
            checks_passed += 1
        else:
            print("   ❌ Secrets file not found: .streamlit/secrets.toml")
            print("      Run: python setup_firebase.py\n")
    except Exception as e:
        print(f"   ❌ Error checking secrets: {e}\n")
    
    # Check 3: Pages directory
    print("3️⃣  Checking pages directory structure...")
    checks_total += 1
    try:
        pages_dir = Path("pages")
        required_files = [
            "pages/__init__.py",
            "pages/dashboard.py",
            "pages/home.py",
            "pages/admin_panel.py"
        ]
        
        missing = []
        for page_file in required_files:
            if not Path(page_file).exists():
                missing.append(page_file)
        
        if not missing:
            print("   ✅ All pages files present")
            for f in required_files:
                print(f"      • {f}")
            print()
            checks_passed += 1
        else:
            print("   ❌ Missing files:")
            for f in missing:
                print(f"      • {f}\n")
    except Exception as e:
        print(f"   ❌ Error checking pages: {e}\n")
    
    # Check 4: Admin panel access check
    print("4️⃣  Checking admin panel access control...")
    checks_total += 1
    try:
        with open("pages/admin_panel.py") as f:
            content = f.read()
            if "check_admin_access()" in content and "is_admin()" in content:
                print("   ✅ Admin access control implemented\n")
                checks_passed += 1
            else:
                print("   ❌ Admin access control missing\n")
    except Exception as e:
        print(f"   ❌ Error checking admin panel: {e}\n")
    
    # Check 5: Session state backup
    print("5️⃣  Checking session state backup (role persistence)...")
    checks_total += 1
    try:
        with open("src/auth/firebase_auth.py") as f:
            content = f.read()
            if "st.session_state" in content and "stored_role" in content:
                print("   ✅ Session state backup implemented\n")
                checks_passed += 1
            else:
                print("   ⚠️  Session state backup not found")
                print("      Role persistence may not work if database fails\n")
    except Exception as e:
        print(f"   ❌ Error checking session backup: {e}\n")
    
    # Check 6: Radio button role selection
    print("6️⃣  Checking role selection UI (radio button)...")
    checks_total += 1
    try:
        with open("login.py") as f:
            content = f.read()
            if "st.radio" in content and "Account Type" in content:
                print("   ✅ Radio button role selection implemented\n")
                checks_passed += 1
            else:
                print("   ⚠️  Role selection may not be optimal")
                print("      Consider using st.radio for better UX\n")
    except Exception as e:
        print(f"   ❌ Error checking role selection: {e}\n")
    
    # Check 7: Home page profile section
    print("7️⃣  Checking home page profile display...")
    checks_total += 1
    try:
        with open("pages/home.py") as f:
            content = f.read()
            if "Your Profile" in content or "is_authenticated()" in content:
                print("   ✅ Home page profile section implemented\n")
                checks_passed += 1
            else:
                print("   ⚠️  Home page profile section may be missing\n")
    except Exception as e:
        print(f"   ❌ Error checking home page: {e}\n")
    
    # Summary
    print("="*70)
    print(f"📊 Results: {checks_passed}/{checks_total} checks passed")
    print("="*70 + "\n")
    
    if checks_passed == checks_total:
        print("✅ All checks passed! Admin role setup looks good.")
        print("\n📝 Next steps:")
        print("   1. Start Streamlit: streamlit run login.py")
        print("   2. Register as Admin")
        print("   3. Verify role shows as Admin in home profile")
        print("   4. Check Admin Panel is accessible\n")
        return True
    else:
        print(f"❌ {checks_total - checks_passed} check(s) failed or need attention")
        print("\n📝 Fix the issues above and run this script again.\n")
        return False

if __name__ == "__main__":
    try:
        success = check_admin_role_setup()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Verification cancelled.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error during verification: {e}")
        sys.exit(1)
