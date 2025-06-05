#!/usr/bin/env python3
"""
Test Instagram bypass functionality without needing a running server
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_instagram_service_bypass():
    """Test Instagram service bypass functionality directly"""
    print("🧪 TESTING INSTAGRAM SERVICE BYPASS")
    print("=" * 60)
    
    try:
        # Import Instagram service
        from instagram_service import InstagramAPIService
        print("✅ Successfully imported InstagramAPIService")
        
        # Create service instance
        service = InstagramAPIService()
        print("✅ Successfully created service instance")
        
        # Create mock test user object
        class MockUser:
            def __init__(self):
                self.id = 1
                self.username = "testuser"
                self.instagram_username = "test_instagram_user"
                self.instagram_pk = "12345678901"
                self.full_name = "Test User"
                self.profile_pic_url = None
        
        test_user = MockUser()
        print(f"✅ Created mock test user: {test_user.username}")
        
        # Test various service methods with bypass
        print("\n🔍 Testing Service Methods...")
        
        # Test 1: get_user_profile_data bypass
        print("\n1. Testing get_user_profile_data bypass")
        try:
            import asyncio
            profile_result = asyncio.run(service.get_user_profile_data(test_user, None))
            if profile_result.get("success") and profile_result.get("test_mode"):
                print("   ✅ Profile data bypass working!")
                print(f"   📸 Username: {profile_result.get('username')}")
                print(f"   👥 Followers: {profile_result.get('follower_count')}")
                print(f"   🧪 Test Mode: {profile_result.get('test_mode')}")
            else:
                print("   ❌ Profile data bypass failed")
        except Exception as e:
            print(f"   ❌ Profile data test error: {e}")
        
        # Test 2: validate_like_action bypass
        print("\n2. Testing validate_like_action bypass")
        try:
            like_result = asyncio.run(service.validate_like_action(test_user, "https://instagram.com/p/test", None))
            if like_result.get("success") and like_result.get("test_mode"):
                print("   ✅ Like validation bypass working!")
                print(f"   ❤️ Media ID: {like_result.get('media_id')}")
                print(f"   👍 Like Count: {like_result.get('like_count')}")
                print(f"   🧪 Test Mode: {like_result.get('test_mode')}")
            else:
                print("   ❌ Like validation bypass failed")
        except Exception as e:
            print(f"   ❌ Like validation test error: {e}")
        
        # Test 3: validate_follow_action bypass
        print("\n3. Testing validate_follow_action bypass")
        try:
            follow_result = asyncio.run(service.validate_follow_action(test_user, "https://instagram.com/testprofile", None))
            if follow_result.get("success") and follow_result.get("test_mode"):
                print("   ✅ Follow validation bypass working!")
                print(f"   👤 Target Username: {follow_result.get('target_username')}")
                print(f"   🔗 Target ID: {follow_result.get('target_user_id')}")
                print(f"   🧪 Test Mode: {follow_result.get('test_mode')}")
            else:
                print("   ❌ Follow validation bypass failed")
        except Exception as e:
            print(f"   ❌ Follow validation test error: {e}")
        
        # Test 4: test_connection bypass
        print("\n4. Testing test_connection bypass")
        try:
            connection_result = asyncio.run(service.test_connection("testuser"))
            if connection_result.get("success") and connection_result.get("test_mode"):
                print("   ✅ Connection test bypass working!")
                print(f"   📱 Username: {connection_result.get('username')}")
                print(f"   ✅ Message: {connection_result.get('message')}")
                print(f"   🧪 Test Mode: {connection_result.get('test_mode')}")
            else:
                print("   ❌ Connection test bypass failed")
        except Exception as e:
            print(f"   ❌ Connection test error: {e}")
        
        # Test 5: get_profile_info bypass
        print("\n5. Testing get_profile_info bypass")
        try:
            profile_info_result = asyncio.run(service.get_profile_info("test_instagram_user"))
            if profile_info_result.get("success") and profile_info_result.get("test_mode"):
                print("   ✅ Profile info bypass working!")
                print(f"   👤 Username: {profile_info_result.get('username')}")
                print(f"   📝 Bio: {profile_info_result.get('biography')}")
                print(f"   🧪 Test Mode: {profile_info_result.get('test_mode')}")
            else:
                print("   ❌ Profile info bypass failed")
        except Exception as e:
            print(f"   ❌ Profile info test error: {e}")
        
        print("\n" + "=" * 60)
        print("🎉 INSTAGRAM SERVICE BYPASS TESTS COMPLETED!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_instagram_service_bypass()
