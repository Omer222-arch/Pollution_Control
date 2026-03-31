#!/usr/bin/env python3
"""
Verification script for Streamlit multi-page app structure
Checks if all required files and directories exist
"""

from pathlib import Path
import sys

def check_structure():
    """Check if the multi-page app structure is correct"""
    
    project_root = Path(__file__).parent
    issues = []
    
    print("🔍 Checking Streamlit Multi-Page App Structure...\n")
    
    # Check main entry point
    main_file = project_root / "login.py"
    if main_file.exists():
        print("✅ Main entry point exists: login.py")
    else:
        print("❌ Main entry point missing: login.py")
        issues.append("Missing login.py")
    
    # Check pages directory
    pages_dir = project_root / "pages"
    if pages_dir.exists() and pages_dir.is_dir():
        print("✅ Pages directory exists: pages/")
    else:
        print("❌ Pages directory missing: pages/")
        issues.append("Missing pages/ directory")
        return issues
    
    # Check required page files
    required_pages = ["dashboard.py", "home.py", "admin_panel.py", "__init__.py"]
    for page_file in required_pages:
        page_path = pages_dir / page_file
        if page_path.exists():
            print(f"  ✅ {page_file}")
        else:
            print(f"  ❌ {page_file}")
            issues.append(f"Missing pages/{page_file}")
    
    # Check firebase auth file
    auth_file = project_root / "src" / "auth" / "firebase_auth.py"
    if auth_file.exists():
        print("\n✅ Firebase auth module exists: src/auth/firebase_auth.py")
    else:
        print("\n❌ Firebase auth module missing: src/auth/firebase_auth.py")
        issues.append("Missing src/auth/firebase_auth.py")
    
    # Check secrets file
    secrets_file = project_root / ".streamlit" / "secrets.toml"
    if secrets_file.exists():
        print("✅ Secrets file exists: .streamlit/secrets.toml")
    else:
        print("⚠️  Secrets file not found: .streamlit/secrets.toml")
        print("   This is needed for Firebase authentication")
        print("   See: FIREBASE_TROUBLESHOOTING.md for setup instructions")
    
    # Summary
    print("\n" + "="*60)
    if issues:
        print(f"❌ Found {len(issues)} issue(s):\n")
        for issue in issues:
            print(f"  - {issue}")
        return issues
    else:
        print("✅ All structure checks passed!")
        print("\n📝 Next steps:")
        print("  1. Ensure .streamlit/secrets.toml is configured")
        print("  2. Run: streamlit run login.py")
        return []

if __name__ == "__main__":
    issues = check_structure()
    sys.exit(0 if not issues else 1)
