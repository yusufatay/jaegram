#!/usr/bin/env python3
"""
Test script to verify the Instagram challenge resolution fix
This tests that the _finalize_challenge_success method properly maps field names
"""

import asyncio
import sys
import json
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from instagram_service import InstagramService

async def test_challenge_field_mapping():
    """Test that challenge resolution properly maps instagram_pk to id"""
    print("🧪 Testing Instagram challenge field mapping fix...")
    
    # Create Instagram service instance
    service = InstagramService()
    
    # Test with a mock challenge client simulation
    # We'll test the _finalize_challenge_success method directly
    
    print("\n1. Testing _finalize_challenge_success method existence...")
    
    # Check if the method exists
    if hasattr(service, '_finalize_challenge_success'):
        print("✅ _finalize_challenge_success method found")
    else:
        print("❌ _finalize_challenge_success method missing")
        return False
    
    print("\n2. Testing field mapping logic...")
    
    # Create a mock response that would come from get_full_user_info
    mock_user_data = {
        "instagram_pk": "12345678",
        "username": "testuser",
        "full_name": "Test User", 
        "profile_pic_url": None,
        "follower_count": 1000,
        "following_count": 500,
        "media_count": 100,
        "is_private": False,
        "is_verified": False,
        "biography": "Test bio"
    }
    
    # Mock the get_full_user_info method to return our test data
    original_get_full_user_info = service.get_full_user_info
    
    async def mock_get_full_user_info(client, instagram_pk):
        return mock_user_data
    
    service.get_full_user_info = mock_get_full_user_info
    
    # Create a mock client
    class MockClient:
        def __init__(self):
            self.pk = "12345678"
            self.username = "testuser"
            self.full_name = "Test User"
            self.profile_pic_url = None
            self.is_private = False
            self.is_verified = False
            
        def account_info(self):
            return self
            
        def get_settings(self):
            return {"session": "mock_session"}
            
        def dump_settings(self, filename):
            pass
    
    # Mock cleanup method
    def mock_cleanup_challenge_data(username):
        pass
    
    service._cleanup_challenge_data = mock_cleanup_challenge_data
    
    try:
        # Test the _finalize_challenge_success method
        mock_client = MockClient()
        mock_response = {"status": "ok"}
        
        result = await service._finalize_challenge_success("testuser", mock_client, mock_response)
        
        print(f"Result: {json.dumps(result, indent=2)}")
        
        # Verify the result structure
        if result.get("success") == True:
            print("✅ Method returns success")
            
            user_data = result.get("user_data", {})
            
            # Check critical field mapping
            if "id" in user_data:
                print(f"✅ 'id' field present: {user_data['id']}")
            else:
                print("❌ 'id' field missing")
                return False
            
            if "user_id" in user_data:
                print(f"✅ 'user_id' field present: {user_data['user_id']}")
            else:
                print("❌ 'user_id' field missing")
            
            if "instagram_pk" in user_data:
                print(f"✅ 'instagram_pk' field present: {user_data['instagram_pk']}")
            else:
                print("❌ 'instagram_pk' field missing")
            
            # Verify field mapping is correct
            if user_data.get("id") == mock_user_data["instagram_pk"]:
                print("✅ Field mapping correct: instagram_pk -> id")
            else:
                print(f"❌ Field mapping incorrect: expected {mock_user_data['instagram_pk']}, got {user_data.get('id')}")
                return False
            
            # Check other required fields
            required_fields = ["username", "full_name", "profile_pic_url"]
            for field in required_fields:
                if field in user_data:
                    print(f"✅ '{field}' field present: {user_data[field]}")
                else:
                    print(f"❌ '{field}' field missing")
                    return False
            
            print("\n✅ All field mapping tests passed!")
            return True
            
        else:
            print(f"❌ Method failed: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing method: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Restore original method
        service.get_full_user_info = original_get_full_user_info

async def main():
    """Main test function"""
    print("🔧 Testing Instagram Challenge Resolution Fix")
    print("=" * 50)
    
    success = await test_challenge_field_mapping()
    
    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Challenge resolution field mapping fix is working correctly")
        print("✅ Frontend will now receive 'id' field instead of null")
        print("✅ Null safety issues should be resolved")
    else:
        print("❌ TESTS FAILED!")
        print("❌ Challenge resolution fix needs attention")
    
    return success

if __name__ == "__main__":
    result = asyncio.run(main())
    sys.exit(0 if result else 1)
