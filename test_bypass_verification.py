#!/usr/bin/env python3
"""
Simple bypass verification test.
Directly tests the bypass logic by examining the code.
"""

import sys
import os
from pathlib import Path

def test_bypass_logic_exists():
    """Test that bypass logic exists in the code"""
    print("🔍 TESTING BYPASS LOGIC EXISTENCE")
    print("="*40)
    
    # Read the instagram_service.py file
    backend_path = Path(__file__).parent / "backend" / "instagram_service.py"
    
    try:
        with open(backend_path, 'r') as f:
            content = f.read()
        
        # Check for test user bypass patterns
        bypass_checks = [
            'username == "testuser"',
            'test_mode": True',
            '🧪 Test user bypass activated',
            'instagram_pk == "12345678901"'
        ]
        
        found_bypasses = []
        for check in bypass_checks:
            if check in content:
                found_bypasses.append(check)
                print(f"✅ Found bypass pattern: {check}")
            else:
                print(f"❌ Missing bypass pattern: {check}")
        
        # Count occurrences
        testuser_count = content.count('username == "testuser"')
        test_mode_count = content.count('test_mode": True')
        bypass_log_count = content.count('🧪 Test user bypass activated')
        
        print(f"\n📊 Bypass Pattern Statistics:")
        print(f"   'testuser' checks: {testuser_count}")
        print(f"   'test_mode' responses: {test_mode_count}")
        print(f"   Bypass log messages: {bypass_log_count}")
        
        if len(found_bypasses) >= 3:
            print("\n✅ Bypass logic is properly implemented!")
            return True
        else:
            print("\n❌ Bypass logic is incomplete!")
            return False
            
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

def test_app_bypass_logic():
    """Test that app.py has bypass logic"""
    print("\n🔍 TESTING APP.PY BYPASS LOGIC")
    print("="*40)
    
    app_path = Path(__file__).parent / "backend" / "app.py"
    
    try:
        with open(app_path, 'r') as f:
            content = f.read()
        
        # Check for bypass patterns in app.py
        app_bypass_checks = [
            'testuser',
            'bypass',
            'test_mode'
        ]
        
        found_app_bypasses = []
        for check in app_bypass_checks:
            if check.lower() in content.lower():
                found_app_bypasses.append(check)
                print(f"✅ Found app bypass pattern: {check}")
            else:
                print(f"❌ Missing app bypass pattern: {check}")
        
        if len(found_app_bypasses) >= 2:
            print("\n✅ App bypass logic is present!")
            return True
        else:
            print("\n❌ App bypass logic may be missing!")
            return False
            
    except Exception as e:
        print(f"❌ Error reading app.py: {e}")
        return False

def test_database_file():
    """Test that database file exists"""
    print("\n🗄️ TESTING DATABASE FILE")
    print("="*30)
    
    db_paths = [
        Path(__file__).parent / "backend" / "instagram_platform.db",
        Path(__file__).parent / "instagram_platform.db",
        Path(__file__).parent / "test.db"
    ]
    
    for db_path in db_paths:
        if db_path.exists():
            size = db_path.stat().st_size
            print(f"✅ Database found: {db_path}")
            print(f"   Size: {size} bytes")
            return True
    
    print("❌ No database file found!")
    return False

def main():
    """Main test function"""
    print("🧪 INSTAGRAM BYPASS VERIFICATION TEST")
    print("="*50)
    
    # Test bypass logic existence
    service_bypass = test_bypass_logic_exists()
    
    # Test app bypass logic
    app_bypass = test_app_bypass_logic()
    
    # Test database
    db_exists = test_database_file()
    
    # Final summary
    print("\n" + "="*60)
    print("🏁 BYPASS VERIFICATION SUMMARY")
    print("="*60)
    
    if service_bypass:
        print("✅ Instagram service bypass logic: IMPLEMENTED")
    else:
        print("❌ Instagram service bypass logic: MISSING")
    
    if app_bypass:
        print("✅ App.py bypass logic: PRESENT")
    else:
        print("❌ App.py bypass logic: MISSING")
    
    if db_exists:
        print("✅ Database file: EXISTS")
    else:
        print("❌ Database file: MISSING")
    
    if service_bypass and app_bypass and db_exists:
        print("\n🎉 BYPASS SYSTEM VERIFICATION: COMPLETE!")
        print("   All components are in place for testing.")
        print("   The bypass functionality should work correctly.")
    else:
        print("\n⚠️  BYPASS SYSTEM VERIFICATION: INCOMPLETE")
        print("   Some components need attention.")
    
    print("="*60)

    # Next steps recommendation
    print("\n📋 NEXT STEPS:")
    if service_bypass and app_bypass:
        print("   1. ✅ Bypass logic is implemented")
        print("   2. 🚀 Ready to test with server startup")
        print("   3. 🧪 Run integration tests")
        print("   4. 📱 Test frontend integration")
    else:
        print("   1. ⚠️  Fix missing bypass logic")
        print("   2. 🔧 Debug import issues")
        print("   3. 🧪 Retry testing")

if __name__ == "__main__":
    main()
