#!/usr/bin/env python3
"""
Direct test of Instagram bypass functionality without needing a running server
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the functions we need to test
from instagram_service import InstagramAPIService
from models import SessionLocalenv python3
"""
Direct test of Instagram bypass functionality without needing a running server
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Import the functions we need to test
from app import get_instagrapi_client_for_user, get_db
import sqlite3

def test_bypass_directly():
    """Test the Instagram bypass functionality directly"""
    print("🧪 DIRECT INSTAGRAM BYPASS TEST")
    print("=" * 60)
    
    # Test user data (matches what we set up for bypass)
    test_user_data = {
        'id': 1,
        'username': 'testuser',
        'instagram_username': 'testuser',
        'instagram_pk': '12345678901',
        'session_data': None,  # No real session data
        'coins': 100
    }
    
    print(f"📸 Testing Instagram client creation for test user: {test_user_data['username']}")
    print(f"   Instagram PK: {test_user_data['instagram_pk']}")
    print(f"   Session Data: {test_user_data['session_data']}")
    
    try:
        # Call the function that should now have bypass logic
        client = get_instagrapi_client_for_user(test_user_data)
        
        if client:
            print("✅ BYPASS SUCCESSFUL!")
            print(f"   Client type: {type(client)}")
            
            # Test if client has expected attributes
            if hasattr(client, 'user_id'):
                print(f"   Mock User ID: {client.user_id}")
            if hasattr(client, 'username'):
                print(f"   Mock Username: {client.username}")
            if hasattr(client, 'device_settings'):
                print(f"   Device Settings: {'✓ Present' if client.device_settings else '✗ Missing'}")
            
            print(f"   🧪 Test mode bypass working correctly!")
            return True
        else:
            print("❌ BYPASS FAILED - No client returned")
            return False
            
    except Exception as e:
        print(f"❌ BYPASS FAILED - Exception: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_normal_user_flow():
    """Test that normal users still go through regular validation"""
    print("\n" + "=" * 60)
    print("🔍 Testing Normal User Flow (should fail without real session)")
    
    normal_user_data = {
        'id': 2,
        'username': 'normaluser',
        'instagram_username': 'normaluser',
        'instagram_pk': '98765432109',  # Different from test user
        'session_data': None,  # No real session data
        'coins': 50
    }
    
    print(f"📸 Testing Instagram client creation for normal user: {normal_user_data['username']}")
    
    try:
        # Call the function - should fail for normal users without session
        client = get_instagrapi_client_for_user(normal_user_data)
        
        if client:
            print("⚠️  Normal user got client (unexpected - might be a bypass leak)")
        else:
            print("✅ Normal user correctly rejected without valid session")
            
    except Exception as e:
        print(f"✅ Normal user correctly failed with exception: {e}")

if __name__ == "__main__":
    success = test_bypass_directly()
    test_normal_user_flow()
    
    print("\n" + "=" * 60)
    print("📋 DIRECT TEST SUMMARY")
    print("=" * 60)
    
    if success:
        print("✅ Test user Instagram bypass: WORKING")
        print("✅ Mock Instagram client: CREATED")
        print("✅ Bypass logic: FUNCTIONING")
        print("✅ Direct test completed successfully!")
    else:
        print("❌ Test user Instagram bypass: FAILED")
        print("❌ Check function implementation for issues")
    
    print("=" * 60)
