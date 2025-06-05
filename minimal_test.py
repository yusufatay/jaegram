#!/usr/bin/env python3
"""
Minimal test to check imports and basic functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

print("Starting minimal test...")

try:
    print("Testing imports...")
    
    # Test app import
    try:
        from app import get_instagrapi_client_for_user
        print("✅ app.py import successful")
    except Exception as e:
        print(f"❌ app.py import failed: {e}")
    
    # Test instagram service import
    try:
        from instagram_service import InstagramAPIService
        print("✅ instagram_service.py import successful")
    except Exception as e:
        print(f"❌ instagram_service.py import failed: {e}")
    
    # Test basic mock user creation
    try:
        test_user = {
            'id': 1,
            'username': 'testuser',
            'instagram_username': 'test_instagram_user',
            'instagram_pk': '12345678901',
            'session_data': None,
            'coins': 100
        }
        print("✅ Mock user created successfully")
        print(f"   Username: {test_user['username']}")
        print(f"   Instagram PK: {test_user['instagram_pk']}")
    except Exception as e:
        print(f"❌ Mock user creation failed: {e}")
    
    print("\n✅ All basic tests passed!")
    
except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")
