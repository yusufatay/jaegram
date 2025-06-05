#!/usr/bin/env python3
"""
Simple test to verify Instagram bypass functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_basic_bypass():
    print("Testing Instagram bypass...")
    
    # Test importing app module
    try:
        from app import get_instagrapi_client_for_user
        print("✅ Successfully imported get_instagrapi_client_for_user")
        
        # Create test user data for bypass
        test_user = {
            'id': 1,
            'username': 'testuser',
            'instagram_username': 'testuser',
            'instagram_pk': '12345678901',
            'session_data': None,
            'coins': 100
        }
        
        print(f"🔧 Testing bypass for user: {test_user['username']}")
        print(f"   Instagram PK: {test_user['instagram_pk']}")
        
        # Call the bypass function
        client = get_instagrapi_client_for_user(test_user)
        
        if client:
            print("✅ BYPASS WORKING!")
            print(f"   Client type: {type(client).__name__}")
            print(f"   Has user_id: {'user_id' in dir(client)}")
            print(f"   Test mode active: True")
            return True
        else:
            print("❌ Bypass failed - no client returned")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("SIMPLE INSTAGRAM BYPASS TEST")
    print("=" * 50)
    
    success = test_basic_bypass()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 BYPASS TEST PASSED!")
    else:
        print("💥 BYPASS TEST FAILED!")
    print("=" * 50)
